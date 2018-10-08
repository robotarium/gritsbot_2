import serial
import json
import logging
import threading
import concurrent.futures as futures
import time

global logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(module)s - %(message)s')
logger = logging.getLogger('root')
logger.setLevel(logging.DEBUG)


def _json_to_bytes(message):
    """Dumps json data to ASCII

    Raises:
        Exception: If the message cannot be JSON encoded.

    """

    return json.dumps(message).encode('ASCII')


def _bytes_to_json(message):
    """Converts from ASCII to JSON

    Raises:
        Exception: If the message cannot be JSON decoded.

    """

    return json.loads(message.decode('ASCII'))


class GritsbotSerial:

    def __init__(self, serial_dev='/dev/ttyACM0', baud_rate=500000, timeout=2):
        self.serial_dev = serial_dev
        self.baud_rate = baud_rate
        self.timeout = timeout
        self._executor = futures.ThreadPoolExecutor()

        # Serial-related attributes.  ALL OF THESE SHOULD BE CONTROLLED WHILE HOLDING THE LOCK
        self._serial_cv = threading.Condition()
        self._serial = None
        self._future = None
        self._stopped = False
        self._started = False
        self._needs_restart = True

        # Constants
        self.MAX_IN_WAITING = 500

    def serial_request(self, msg, timeout=5):
        """Makes a request on a serial line

        Args:
            msg: A JSON-encodable (by json.dumps) object

        Raises:
            RuntimeError: If the serial port has too many incoming bytes (speciefied by MAX_IN_WAITING).
            RuntimeError: If the serial port cannot be written to or read from.
            RuntimeError: If the serial port has not been initialized.

        Returns:
            JSON-formatted dict containing the return message.

        """

        with self._serial_cv:
            if(not self._started):
                error_msg = 'Serial connection must be started prior to calling this method.'
                logger.critical(error_msg)
                raise RuntimeError(error_msg)

            if(self._stopped):
                error_msg = 'Serial connection stopped!  Cannot use anymore.'
                logger.critical(error_msg)
                raise RuntimeError(error_msg)

            # Wait until the serial_task thread has restarted the serial device.
            while(self._needs_restart):
                if(not self._serial_cv.wait(timeout=timeout)):
                    # If the CV times out, it returns false
                    error_msg = 'Serial connection timed out!'
                    logger.critical(error_msg)
                    raise RuntimeError(error_msg)

            msg = _json_to_bytes(msg)

            try:
                self._serial.write(msg)
            except Exception as e:
                error_msg = 'Unable to write to the serial port.'
                logger.critical(error_msg)
                logger.critical(repr(e))

                # Signal the serial_task thread that the serial device should be restarted
                self._needs_restart = True
                self._serial_cv.notify_all()
                raise RuntimeError(error_msg)

            # Read to wait for bytes to be available
            try:
                msg = self._serial.read()
            except Exception as e:
                error_msg = 'Unable to read from serial port'
                logger.critical(error_msg)
                logger.critical(repr(e))

                # Signal the serial_task thread that the serial device should be restarted
                self._needs_restart = True
                self._serial_cv.notify_all()
                raise RuntimeError(error_msg)

            if(self._serial.in_waiting > self.MAX_IN_WAITING):
                error_msg = 'Too many incoming bytes waiting on serial port ({})'.format(self._serial.in_waiting)
                logger.warning(error_msg)

                # Signal the serial_task thread that the serial device should be restarted
                self._needs_restart = True
                self._serial_cv.notify_all()
                raise RuntimeError(error_msg)

            # Once bytes are available, read the rest in.  We assume that the entire message is on
            # the line
            try:
                msg += self._serial.read(self._serial.in_waiting)
            except Exception as e:
                error_msg = 'Unable to read from the serial port.'
                logger.critical(error_msg)
                logger.critical(repr(e))

                # Signal the serial_task thread that the serial device should be restarted
                self._needs_restart = True
                self._serial_cv.notify_all()
                raise RuntimeError(error_msg)

            result = None
            try:
                result = _bytes_to_json(msg)
            except Exception as e:
                logger.warning('Unable to parse JSON message from serial port')
                logger.warning(repr(e))

            return result

    def start(self, timeout=5):
        """Starts the serial line by attempting to establish a serial for the specified device.

        This method should be called prior to other methods of this class.

        Raises:
            RuntimeError: If the serial connection cannot be established within timeout.

        """

        def serial_task():
            while (not self._stopped):
                start_time = time.time()

                with self._serial_cv:
                    while (not self._needs_restart and not self._stopped):
                        self._serial_cv.wait()

                    if(self._stopped):
                        break
                    else:
                        # Need to restart serial
                        if(self._serial is not None):
                            self._serial.close()
                            self._serial = None

                        try:
                            self._serial = serial.Serial(self.serial_dev, self.baud_rate, timeout=self.timeout)
                            # If we succeeded, no longer need to restart serial
                            self._needs_restart = False
                            self._serial_cv.notify_all()
                        except Exception as e:
                            logger.critical('Could not get serial device ({})'.format(self.serial_dev))
                            logger.critical(repr(e))

                # Wait at least one second between retries
                time.sleep(max(0, 1 - (time.time() - start_time)))

        # Wait for initial connection
        with self._serial_cv:
            if(self._started):
                logger.critical('Cannot start the serial connection more than once!')
                raise RuntimeError()

            if(self._stopped):
                logger.critical('Cannot start the serial connection once stopped.')
                raise RuntimeError()

            # If it's already been started, we can't get to this part of the code
            self._started = True
            self._future = self._executor.submit(serial_task)

            # Wait to acquire the serial connection once
            while(self._needs_restart):
                if(not self._serial_cv.wait(timeout=timeout)):
                    logger.critical('Initial serial connection timed out.')
                    # If we're in this state, then we have the lock, and the serial_task thread cannot acquire it.
                    # However, if we're very unlucky, the serial device my have been acquired by the time we get here.  Either way,
                    # it should be safe to just call stop and exit.

                    # We can call self.stop here, since the underlying lock is reentrant
                    self.stop()
                    raise RuntimeError()

    def stop(self):
        """Stops the serial connection.

        Closes the underlying pyserial connection.  If the serial connection has not been started, does nothing.

        """

        # If we've previously started serial, stop it.
        with self._serial_cv:
            self._stopped = True
            self._serial_cv.notify_all()

            self._executor.shutdown()

            # If the serial connection was never started, don't shut it down
            if(self._started):
                if(self._serial is not None):
                    self._serial.close()
                    self._serial = None
