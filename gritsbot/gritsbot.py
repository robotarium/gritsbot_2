import gritsbotserial
import json
import vizier.node as node
import time
import argparse
from uuid import getnode
import logging
import queue

# Set up logging
global logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)

# Constants
MAX_QUEUE_SIZE = 100


def get_mac():
    """Gets the MAC address for the robot from the network config info.

    Returns:
        A MAC address for the robot.
    """
    hex_mac = hex(getnode())[2:].zfill(12)
    return ':'.join(x + y for x, y in zip(hex_mac[::2], hex_mac[1::2]))


def create_node_descriptor(end_point):
    """Returns a node descriptor for the robot based on the end_point.

    The server_alive link is for the robot to check the MQTT connection periodically.

    Args:
        end_point (str): The ID of the robot.

    Returns:
        A node descriptor of the vizier format for the robot.
    """

    node_descriptor = \
        {
            'end_point': end_point,
            'links':
            {
                '/status': {'type': 'DATA'},
                '/server_alive': {'type': 'STREAM'}
            },
            'requests':
            [
                {
                    'link': 'matlab_api/'+end_point,
                    'type': 'STREAM',
                    'required': False
                },
                {
                    'link': end_point+'/server_alive',
                    'type': 'STREAM',
                    'required': True
                }
            ]
        }

    return node_descriptor


class Gritsbot:

    def __init__(self, node_descriptor, serial_dev='/dev/ttyACM0', baud_rate=115200, host='192.168.1.7', port=1884):
        self.serial_dev = serial_dev
        self.baud_rate = baud_rate
        self.host = host
        self.port = port
        self.node_descriptor = node_descriptor

        # Attributes set and removed by relevant start/stop methods
        self.robot_node = None
        self.serial = None

    def start_robot_node(self):
        self.robot_node = node.Node(self.host, self.port, self.node_descriptor)
        self.robot_node.start()

    def stop_robot_node(self):
        self.robot_node.stop()
        self.robot_node = None

    def start_serial(self):
        self.serial = gritsbotserial.GritsbotSerial(self.serial_dev, self.baud_rate)
        self.serial.start()

    def stop_serial(self):
        self.serial.stop()
        self.robot_node = None

    def start(self):
        self.start_robot_node()
        self.start_serial()

    def stop(self):
        self.stop_serial()
        self.stop_robot_node()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("mac_list", help="JSON file containing MAC to id mapping")
    parser.add_argument("-port", type=int, help="MQTT Port", default=8080)
    parser.add_argument("-host", help="MQTT Host IP", default="localhost")
    parser.add_argument('-update_rate', type=float, help='Update rate for robot main loop', default=0.016)
    parser.add_argument('-status_update_rate', type=float, help='How often to check status info', default=1)

    # Retrieve the MAC address for the robot
    mac_address = get_mac()

    # Parser and set CLI arguments
    args = parser.parse_args()
    update_rate = args.update_rate
    status_update_rate = args.status_update_rate

    try:
        f = open(args.mac_list, 'r')
        mac_list = json.load(f)
    except Exception as e:
        print(repr(e))
        print('Could not open file ({})'.format(args.node_descriptor))

    if(mac_address in mac_list):
        robot_id = mac_list[mac_address]
    else:
        print('MAC address {} not in supplied MAC list file'.format(mac_address))
        return -1

    logger.info('This is robot: ({0}) with MAC address: ({1})'.format(robot_id, mac_address))

    # Create node descriptor for robot and set up links
    node_descriptor = create_node_descriptor(mac_list[mac_address])
    status_link = robot_id + '/status'
    input_link = 'matlab_api/' + robot_id
    server_alive_link = robot_id+'/server_alive'

    robot = Gritsbot(node_descriptor, serial_dev='/dev/ttyACM0', baud_rate=115200,
                     host=args.host, port=args.port)

    # Sit here until we get a valid connection to the robot's required interfaces
    started = False
    while not started:
        try:
            robot.start()
            started = True
        except Exception as e:
            logger.critical('Could not start robot.')
            logger.critical(repr(e))

        time.sleep(1)

    # Queues for STREAM links
    motor_commands = robot.robot_node.subscribe(input_link)
    heartbeats = robot.robot_node.subscribe(server_alive_link)

    # Initialize times for various activities
    start_time = time.time()
    print_time = time.time()
    status_update_time = time.time()
    heartbeat_time = time.time()

    # Initialize data
    battery_data = robot.serial.read_battery_voltage()
    charging_data = robot.serial.read_charging_status()
    status_data = {'batt_volt': -1, 'charge_status': True}
    last_motor_message = {}

    # Main loop for the robot
    while True:

        start_time = time.time()

        # Check if MQTT server is alive and well
        if((start_time - heartbeat_time) >= status_update_rate):
            # Publish arbitrary message on self loop
            robot.robot_node.publish(server_alive_link, ''.encode(encoding='UTF-8'))
            heartbeat = None
            try:
                heartbeat = heartbeats.get(timeout=1)
            except queue.Empty:
                logger.critical('Could not heartbeat server.  Restarting node.')

            # Error handling.  Restart robot node and resubscribe to relevant topics
            if(heartbeat is None):
                try:
                    robot.stop_robot_node()
                    robot.start_robot_node()
                    motor_commands = robot.robot_node.subscribe(input_link)
                    heartbeats = robot.robot_node.subscribe(server_alive_link)
                except Exception as e:
                    logger.critical('Could not reconnect to vizier network')
                    logger.critical(repr(e))

            heartbeat_time = start_time

        # Retrieve status data: battery voltage and charging status
        if((start_time - status_update_time) >= status_update_rate):
            try:
                battery_data = robot.serial.read_battery_voltage()
                charging_data = robot.serial.read_charging_status()
                status_data.update(battery_data)
                status_data.update(charging_data)
                robot.robot_node.put(status_link, status_data)
            except gritsbotserial.ReadWriteError:
                pass
            except gritsbotserial.ByteOverflow:
                robot.serial.flush_serial()

            status_update_time = time.time()

        # Process motor commands
        motor_message = None
        # Make sure that our queue isn't enormous
        if(motor_commands.qsize() > MAX_QUEUE_SIZE):
            logger.critical('Queue of motor messages is too large')

        try:
            # Clear out the queue
            while True:
                motor_message = motor_commands.get_nowait()
        except queue.Empty:
            pass

        if(motor_message is not None):
            try:
                motor_message = json.loads(motor_message.decode(encoding='UTF-8'))
            except Exception as e:
                logger.warning('Got malformed JSON motor message')
                logger.warning(repr(e))
                # Set this to None for the next checks
                motor_message = None

        if(motor_message is not None):
            if('v' in motor_message and 'w' in motor_message):
                last_motor_message = motor_message
                try:
                    robot.serial.write_motor_velocities(motor_message['v'], motor_message['w'])
                except gritsbotserial.ReadWriteError:
                    pass
                except gritsbotserial.ByteOverflow:
                    robot.serial.flush_serial()
            else:
                logger.warning('Got motor message ({}) with incorrect keys.'.format(motor_message))

        # Print out status data
        if((start_time - print_time) >= status_update_rate):
            logger.info('Status data ({})'.format(status_data))
            logger.info('Last motor message received ({})'.format(last_motor_message))
            print_time = time.time()

        # Sleep for whatever time is left at the end of the loop
        time.sleep(max(0, update_rate - (time.time() - start_time)))


if __name__ == '__main__':
    main()
