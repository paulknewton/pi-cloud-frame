import logging
import math

import smbus
from orientation import Compass

logger = logging.getLogger(__name__)


class Mpu6050(Compass):
    """
    Interface to MPU-6050 accelerometer/gyroscope.
    Code taken from http://blog.bitify.co.uk/2013/11/reading-data-from-mpu-6050-on-raspberry.html by Andy Birkett
    """

    # Power management registers
    power_mgmt_1 = 0x6b
    power_mgmt_2 = 0x6c

    def get_rotation(self):
        bus = smbus.SMBus(1)  # or bus = smbus.SMBus(1) for Revision 2 boards
        address = 0x68  # This is the address value read via the i2cdetect command

        # Now wake the 6050 up as it starts in sleep mode
        bus.write_byte_data(address, power_mgmt_1, 0)

        accel_xout = read_word_2c(0x3b)
        accel_yout = read_word_2c(0x3d)
        accel_zout = read_word_2c(0x3f)

        accel_xout_scaled = accel_xout / 16384.0
        accel_yout_scaled = accel_yout / 16384.0
        accel_zout_scaled = accel_zout / 16384.0

        logger.debug("accel_xout: ", accel_xout, " scaled: ", accel_xout_scaled)
        logger.debug("accel_yout: ", accel_yout, " scaled: ", accel_yout_scaled)
        logger.debug("accel_zout: ", accel_zout, " scaled: ", accel_zout_scaled)

        return get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)

    @staticmethod
    def read_byte(adr):
        return bus.read_byte_data(address, adr)

    @staticmethod
    def read_word(adr):
        high = bus.read_byte_data(address, adr)
        low = bus.read_byte_data(address, adr + 1)
        val = (high << 8) + low
        return val

    @staticmethod
    def read_word_2c(adr):
        val = read_word(adr)

        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val

    @staticmethod
    def dist(a, b):
        return math.sqrt((a * a) + (b * b))

    @staticmethod
    def get_y_rotation(x, y, z):
        radians = math.atan2(x, dist(y, z))

        return -math.degrees(radians)

    @staticmethod
    def get_x_rotation(x, y, z):
        radians = math.atan2(y, dist(x, z))

        return math.degrees(radians)
