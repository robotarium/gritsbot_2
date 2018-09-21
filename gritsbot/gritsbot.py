import serial
import json
import vizier.node as node
import concurrent.futures as futures
import time
import argparse
from uuid import getnode

# TODO get rid of global variables
global s
s = serial.Serial('/dev/ttyACM0', 115200)
status_data = {}
motor_message = {'v': 0, 'w': 0}
motor_message_time = time.time()
# m = mi.MQTTInterface(host='192.168.1.12', port=1884)
e = futures.ThreadPoolExecutor()

# Proposed request packet structure
request = {'method': 'read', 'body': {'type': 'batt_volt'}}
request = {'method': 'read', 'body': {'type': 'charge_status'}}
request = {'method': 'write', 'body': {'v': 0, 'w': 0, 'type': 'motor'}}
request = {'method': 'write', 'body': {'type': 'led', 'left_led': [255, 0, 0], 'right_led': [0, 255, 0]}}

# Proposed response packet structure
response = {'status': 1, 'body': {'bat_volt': 4.3}}


def get_mac():
    hex_mac = hex(getnode())[2:].zfill(12)
    return ':'.join(x + y for x, y in zip(hex_mac[::2], hex_mac[1::2]))


def create_node_descriptor(end_point):

    node_descriptor = \
    {
        'end_point': end_point,
	    'links':
	{
		'/status': {'type': 'DATA'}
	},
	'requests':
	[
		{'link': 'matlab_api/'+end_point,
         'type': 'STREAM',
		 'required': 'false'}
	]
    }

    return node_descriptor

def create_request(method, body):
    return {'method': method, 'body': body}

def json_to_bytes(message):
    return json.dumps(message).encode('ASCII')

def bytes_to_json(message):
    return json.loads(message.decode('ASCII'))

def node_velocities_cb(data):
    # print('got motor data: ', data)
    global motor_message
    global motor_message_time
    motor_message = json.loads(data.decode(encoding='UTF-8'))
    motor_message_time = time.time()

def serial_request(method, body, timeout=1):
    """Makes a request on the serial line

    Args:
        method (str): Method for the request (read or write)
        body (dict): Body of the message
        timeout (double): timeout for serial read

    Returns:
        Json-formatted dict containing the body of the return message

    """

    global s

    msg = json_to_bytes(create_request(method, body))

    start = time.time()
    s.write(msg)

    start = time.time()
    # Read to wait for bytes to be available
    try:
        msg = s.read()
        # Once bytes are available, read the rest in.  We assume that the entire message is on
        # the line
        msg += s.read(s.in_waiting)
        result = bytes_to_json(msg)
    except Exception as e:
        print(repr(e))
        print('Unable to read from serial port')

    if('body' in result):
        #print('Got result: {}'.format(result))
        return result['body']
    else:
        print('Serial read error for type ({})'.format(body))

def serial_write_request(message_type, body={}):
    body['type'] = message_type
    return serial_request('write', body)

def serial_read_request(message_type, body={}):
    body['type'] = message_type
    return serial_request('read', body)

def read_battery_voltage():
    return serial_read_request('batt_volt')

def read_charging_status():
    return serial_read_request('charge_status')

def write_motor(v, w):
    return serial_write_request('motor', {'v': float(v), 'w': float(w)})

def write_left_led(left_led):
    return serial_write_request('led_left', {'left_led': left_led})

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("mac_list", help="JSON file containing MAC to id mapping")
    parser.add_argument("-port", type=int, help="MQTT Port", default=8080)
    parser.add_argument("-host", help="MQTT Host IP", default="localhost")
    parser.add_argument('-update_rate', type=float, help='Update rate for robot main loop', default=0.033)

    mac_address = get_mac()
    print('MAC address for robot is: ', mac_address)

    args = parser.parse_args()

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


    node_descriptor = create_node_descriptor(mac_list[mac_address])
    status_link = robot_id + '/status'
    input_link = 'matlab_api/' + robot_id

    # Initialize and start the robot's node
    robot_node = node.Node(args.host, args.port, node_descriptor)
    robot_node.start()

    # TODO: Change this based on the thing being tracked in MATLAB
    robot_node.subscribe_with_callback(input_link, node_velocities_cb)

    update_rate = args.update_rate
    global motor_message

    start = 0
    start_time = time.time()


    write_left_led([255, 0, 0])
    while True:

        battery_data = read_battery_voltage()
        charging_data = read_charging_status()

        status_data.update(battery_data)
        status_data.update(charging_data)

        robot_node.put(status_link, status_data)
        if((time.time() - motor_message_time) <= 0.1):
            write_motor(motor_message['v'], motor_message['w'])



        # Sleep for whatever time is left at the end of the loop
        time_now = time.time()
        print(time.time() - start_time)
        time.sleep(max(0, update_rate - (time.time() - start_time)))
        start_time = time.time()

if __name__ == '__main__':
    main()
