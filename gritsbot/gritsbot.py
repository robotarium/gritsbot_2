import serial
import json
import vizier.mqttinterface as mi
import concurrent.futures as futures
import queue


s = serial.Serial('/dev/ttyACM0', 9600)
m = mi.MQTTInterface(host='192.168.1.12', port=1884)
e = futures.ThreadPoolExecutor()

# Proposed packet structure
request = {'method': 'read', 'body': 'voltage'}
packet = {'method': 'write', 'body': {}}

response = {'status': 1, 'body': {}}


def write_job():
    while True:
        to_write = write_q.get()
        if(to_write):
            s.write(to_write()) 
        else:
            break

def read_job():
    while True:
        # Check if closed.  If closed, then exit the loop.  Probably need try/catch here as well
        to_read = s.read(s.inWaiting()).decode('ASCII')
        read_q.put(to_read)

def send_angular_velocities(wl, wr):

    # Doesn't require a handshake
    global s
    s.write(json.dumps({'wl': wl, 'wr': wr}).encode('ASCII'))

def read_battery_voltage():
    
    # Need to write request
    # read from serial
    def serial_read():
        global s
        # TODO: Check if this returns immediately if inWaiitng = 0
        return s.read(s.inWaiting())

    future_serial_read = e.submit(serial_read) 
    s.write() # Write motor packet
    return future_serial_read.result()

def main():

    read_battery_voltage()
    send_angular_velocities()
    


if __name__ == '__main__': 
    main()
