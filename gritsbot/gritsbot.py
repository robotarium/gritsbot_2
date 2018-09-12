import serial
import json
import vizier.mqttinterface as mi
import vizier.node as node
import concurrent.futures as futures
import queue
import time
import argparse


s = serial.Serial('/dev/ttyACM0', 9600)
#m = mi.MQTTInterface(host='192.168.1.12', port=1884)
e = futures.ThreadPoolExecutor()

# Proposed request packet structure
request = {'method': 'read', 'body': {'type': 'bat_volt'}}
packet = {'method': 'write', 'body': {'v': 0, 'w': 0, 'type': 'motor'}}

# Proposed response packet structure
response = {'status': 1, 'body': {'bat_volt': 4.3}}

def create_request(method, body):
    return {'method': method, 'body': body}

def json_to_bytes(message):
    return json.dumps(message).encode('ASCII')

def bytes_to_json(message):
    return json.loads(message.decode('ASCII'))

def node_velocities_cb(data):
    global s

    msg = create_request('write', {'v': float(data['v']), 'w': float(data['w']), 'type': 'motor'})
    s.write(json_to_bytes(msg))

def send_angular_velocities(v, w):

    # Doesn't require a handshake
    global s
    msg = create_request('write', {'v': float(v), 'w': float(w), 'type': 'motor'})
    s.write(json_to_bytes(msg))

def read_battery_voltage():

    # Need to write request
    # read from serial
    def serial_read():
        global s
        # Read to wait for bytes to be available
        msg = s.read()
        # Once bytes are available, read the rest in.  We assume that the entire message is on
        # the line
        msg += s.read(s.in_waiting)
        return bytes_to_json(msg)

    future_serial_read = e.submit(serial_read)
    msg = create_request('read', {'type': 'bat_volt'})
    s.write(json_to_bytes(msg)) # Write request packet

    # The result of the future should be in the appropriate format
    result = future_serial_read.result()
    if('body' in result):
        print('Got result: {}'.format(result['body']))
    else:
        # Should be an error
        pass

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("node_descriptor", help=".json file node information")
    parser.add_argument("-port", type=int, help="MQTT Port", default=8080)
    parser.add_argument("-host", help="MQTT Host IP", default="localhost")
    parser.add_arugment('-update_rate', help='Update rate for robot main loop', default=0.016)

    args = parser.parse_args()

    node_descriptor = None
    try:
        f = open(args.node_descriptor, 'r')
        node_descriptor = json.load(f)
    except Exception as e:
        print(repr(e))
        print('Could not open file ({})'.format(args.node_descriptor))


    # Initialize and start the robot's node
    robot_node = node.Node(args.host, args.port, node_descriptor)
    robot_node.start()

    # TODO: Change this based on the thing being tracked in MATLAB
    robot_node.subscribe_with_callback('matlab_api/1', node_velocities_cb)

    start = 0
    start_time = time.time()
    while True:
        read_battery_voltage()

        # Sleep for whatever time is left at the end of the loop
        time_now = time.time()
        time.sleep(max(0, args.update_rate - (time_now - start_time)))
        start_time = time_now

        send_angular_velocities(start, 0.0)
        time.sleep(0.5)
        start = (start + 1) % 26


if __name__ == '__main__':
    main()
