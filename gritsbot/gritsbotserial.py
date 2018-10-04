import serial
import json
import logging

global logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)

# Proposed request packet structure
request = {'method': 'read', 'body': {'type': 'batt_volt'}}
request = {'method': 'read', 'body': {'type': 'charge_status'}}
request = {'method': 'write', 'body': {'v': 0, 'w': 0, 'type': 'motor'}}
request = {'method': 'write', 'body': {'type': 'led_left', 'rgb': [255, 0, 0]}}
reqest = {'method': 'write', 'body': {'type': 'led_right', 'rgb': [255, 0, 0]}}
# Proposed response packet structure
response = {'status': 1, 'body': {'bat_volt': 4.3}}


def _json_to_bytes(message):
    return json.dumps(message).encode('ASCII')


def _bytes_to_json(message):
    return json.loads(message.decode('ASCII'))


def _create_request(method, body):
        return {'method': method, 'body': body}


class ReadWriteError(Exception):
    pass


class DeviceError(Exception):
    pass


class ByteOverflow(Exception):
    pass


class GritsbotSerial:

    def __init__(self, serial_dev='/dev/ttyACM0', baud_rate=115200, timeout=1):
        self.serial_dev = serial_dev
        self.baud_rate = baud_rate
        self.timeout = timeout

        # To hold future serial device
        self._serial = None

        # Constants
        self.MAX_IN_WAITING = 500

    def _serial_request(self, method, body):
        """Makes a request on a serial line

        Args:
            method (str): Method for the request (read or write).
            body (dict): Body of the message.
            timeout (double): timeout for serial read.

        Raises:
            ReadWriteError: If the serial port cannot be read from or written to.
            ByteOverflow: If the serial port has too many incoming bytes (speciefied by MAX_IN_WAITING)

        Returns:
            Json-formatted dict containing the body of the return message.
        """
        msg = _json_to_bytes(_create_request(method, body))

        try:
            self._serial.write(msg)
        except Exception as e:
            logger.critical('Unable to write to serial port.')
            logger.critical(repr(e))
            raise ReadWriteError

        # Read to wait for bytes to be available
        try:
            msg = self._serial.read()
        except Exception as e:
            logger.critical(repr(e))
            logger.critical('Unable to read from serial port')
            raise ReadWriteError

        if(self._serial.in_waiting > self.MAX_IN_WAITING):
            logger.warning('Too many incoming bytes waiting on serial port ({})'.format(self._serial.in_waiting))
            raise ByteOverflow

        try:
            # Once bytes are available, read the rest in.  We assume that the entire message is on
            # the line
            msg += self._serial.read(self._serial.in_waiting)
        except Exception as e:
            logger.critical('Unable to read from serial port')
            logger.critical(repr(e))
            raise ReadWriteError

        try:
            result = _bytes_to_json(msg)
        except Exception as e:
            logger.warning('Unable to parse JSON message from serial port')
            logger.warning(repr(e))

        if('body' in result):
            return result['body']
        else:
            logger.critical('Body not in response from serial')

    def _serial_write_request(self, message_type, body={}):
        body['type'] = message_type
        return self._serial_request('write', body)

    def _serial_read_request(self, message_type, body={}):
        body['type'] = message_type
        return self._serial_request('read', body)

    def start(self):
        try:
            self._serial = serial.Serial(self.serial_dev, self.baud_rate, timeout=self.timeout)
        except Exception as e:
            logger.critical('Could not get serial device ({})'.format(self.serial_dev))
            logger.critical(repr(e))
            raise DeviceError

    def stop(self):
        self._serial.close()

    def read_battery_voltage(self):
        return self._serial_read_request('batt_volt')

    def read_charging_status(self):
        return self._serial_read_request('charge_status')

    def write_motor_velocities(self, v, w):
        return self._serial_write_request('motor', {'v': float(v), 'w': float(w)})

    def write_left_led(self, left_led):
        return self._serial_write_request('led_left', {'rgb': left_led})

    def flush_serial(self):
        self._serial.reset_input_buffer()
        self._serial.reset_output_buffer()


def main():

    import time

    gs = GritsbotSerial('/dev/ttyACM0', 115200)
    gs.start()

    while True:
        result = gs.read_battery_voltage()
        print(result)
        time.sleep(1)


if __name__ == '__main__':
    main()
