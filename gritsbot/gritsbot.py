import serial
import json
import vizier.mqttinterface as mi
import concurrent.futures as futures
import queue
import time


s = serial.Serial('/dev/ttyACM0', 9600)
#m = mi.MQTTInterface(host='192.168.1.12', port=1884)
e = futures.ThreadPoolExecutor()

# 0 -- read 
# 1 -- write

# Proposed request packet structure
request = {'method': 'write', 'body': {'type': 'bat_volt'}}
packet = {'method': 'read', 'body': {'v': 0, 'w': 0, 'type': 'motor'}}

# Proposed response packet structure
response = {'status': 1, 'body': {'bat_volt': 4.3}}

def create_request(method, body):
    return {'method': method, 'body': body}

def json_to_bytes(message):
    return json.dumps(message).encode('ASCII') 

def bytes_to_json(message):
    return json.loads(message.decode('ASCII'))

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
    start = 0
    while True:
        read_battery_voltage()
        send_angular_velocities(start, 0.0)
        time.sleep(0.5)
        start = (start + 1) % 26

if __name__ == '__main__': 
    main()
