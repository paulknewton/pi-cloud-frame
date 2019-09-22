import logging
import math

import smbus
from utils import orientation

logger = logging.getLogger(__name__)


class Mpu6050(orientation.Compass):
    """
    Interface to MPU-6050 accelerometer/gyroscope.
    Code taken from http://blog.bitify.co.uk/2013/11/reading-data-from-mpu-6050-on-raspberry.html by Andy Birkett
    """

    # Power management registers
    power_mgmt_1 = 0x6b
    power_mgmt_2 = 0x6c

    bus = smbus.SMBus(1)  # or bus = smbus.SMBus(1) for Revision 2 boards
    address = 0x68  # This is the address value read via the i2cdetect command

    def get_rotation(self):
        return 88

        # Now wake the 6050 up as it starts in sleep mode
        Mpu6050.bus.write_byte_data(Mpu6050.address, Mpu6050.power_mgmt_1, 0)

        accel_xout = Mpu6050.read_word_2c(0x3b)
        accel_yout = Mpu6050.read_word_2c(0x3d)
        accel_zout = Mpu6050.read_word_2c(0x3f)

        accel_xout_scaled = accel_xout / 16384.0
        accel_yout_scaled = accel_yout / 16384.0
        accel_zout_scaled = accel_zout / 16384.0

        logger.debug("accel_xout: ", accel_xout, " scaled: ", accel_xout_scaled)
        logger.debug("accel_yout: ", accel_yout, " scaled: ", accel_yout_scaled)
        logger.debug("accel_zout: ", accel_zout, " scaled: ", accel_zout_scaled)

        return Mpu6050.get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)

    @staticmethod
    def read_byte(adr):
        return Mpu6050.bus.read_byte_data(Mpu6050.address, adr)

    @staticmethod
    def read_word(adr):
        high = Mpu6050.bus.read_byte_data(Mpu6050.address, adr)
        low = Mpu6050.bus.read_byte_data(Mpu6050.address, adr + 1)
        val = (high << 8) + low
        return val

    @staticmethod
    def read_word_2c(adr):
        val = Mpu6050.read_word(adr)

        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val

    @staticmethod
    def dist(a, b):
        return math.sqrt((a * a) + (b * b))

    @staticmethod
    def get_y_rotation(x, y, z):
        radians = math.atan2(x, Mpu6050.dist(y, z))

        return -math.degrees(radians)

    @staticmethod
    def get_x_rotation(x, y, z):
        radians = math.atan2(y, Mpu6050.dist(x, z))

        return math.degrees(radians)
