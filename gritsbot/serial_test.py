import serial
import concurrent.futures as futures
import time
import json
from uuid import getnode


s = serial.Serial('/dev/ttyACM0', 115200, timeout=10)

# Proposed request packet structure
request = {'method': 'read', 'body': {'type': 'batt_volt'}}
request = {'method': 'read', 'body': {'type': 'charge_status'}}
request = {'method': 'write', 'body': {'v': 0, 'w': 0, 'type': 'motor'}}
request = {'method': 'write', 'body': {'type': 'led_left', 'rgb': [255, 0, 0]}}

# Proposed response packet structure
response = {'status': 1, 'body': {'bat_volt': 4.3}}

def get_mac():
    hex_mac = hex(getnode())[2:].zfill(12)
    return ':'.join(x + y for x, y in zip(hex_mac[::2], hex_mac[1::2]))

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

    # Write request packet to serial.  Response will eventually be waiting
    s.write(msg)

    start = time.time()
    # Read to wait for bytes to be available

    msg = s.read()
    print('got msg at ', time.time() - start)

    try:
        # Once bytes are available, read the rest in.  We assume that the entire message is on
        # the line
        # TODO: Add timeout
        msg += s.read(s.in_waiting)
        #print('finished read at ', time.time() - start)
        result = bytes_to_json(msg)
    except Exception as e:
        print(repr(e))
        print('Unable to read from serial port')
        return {}


    ## The result of the future should be in the appropriate format
    #try:
    #    result = future_serial_read.result(timeout=timeout)
    #except Exception as ex:
    #    print(repr(ex))
    #    print('Serial read timed-out for type ({})'.format(message_type))

    if('body' in result):
        #print('Got result: {}'.format(result))
        return result['body']
    else:
        print('Serial read error for type ({})'.format(body))
        return {}

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

def write_angular_velocities(v, w):
    return serial_write_request('motor', {'v': float(v), 'w': float(w)})

def write_leds(left_led=[0, 0, 0], right_led=[0, 0, 0]):
    return serial_write_request('led', {'left_led': left_led, 'right_led': right_led})

def main():

    print('mac address ', get_mac())
    update_rate = 1
    status_data = {}

    start = 0
    start_time = time.time()
    while True:
        
        battery_data = read_battery_voltage()
        #print('took ', time.time() - start_time)
        test_time = time.time()
        charging_data = read_charging_status()
        #print('took ', time.time() - test_time)

        status_data.update(battery_data)
        status_data.update(charging_data)
        status_data['timestamp'] = time.time()


        print(status_data)

        # Sleep for whatever time is left at the end of the loop
        time_now = time.time()
        print(time_now - start_time)
        #print(max(0, update_rate - (time.time() - start_time)))
        time.sleep(max(0, update_rate - (time.time() - start_time)))
        start_time = time.time()


if __name__ == '__main__':
    main()
