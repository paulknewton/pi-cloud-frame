import logging
import math

import smbus
from utils import orientation

logger = logging.getLogger(__name__)


class Mpu6050Compass(orientation.Compass):
    """
    Interface to MPU-6050 accelerometer/gyroscope.
    Code taken from http://blog.bitify.co.uk/2013/11/reading-data-from-mpu-6050-on-raspberry.html by Andy Birkett
    """

    # Power management registers
    power_mgmt_1 = 0x6b
    power_mgmt_2 = 0x6c

    bus = smbus.SMBus(1)  # or bus = smbus.SMBus(1) for Revision 2 boards
    address = 0x68  # This is the address value read via the i2cdetect command

    def __init__(self, flip=False):
        super().__init__(flip)

    def get_rotation(self):
        # Now wake the 6050 up as it starts in sleep mode
        Mpu6050Compass.bus.write_byte_data(Mpu6050Compass.address, Mpu6050Compass.power_mgmt_1, 0)

        accel_xout = Mpu6050Compass.read_word_2c(0x3b)
        accel_yout = Mpu6050Compass.read_word_2c(0x3d)
        accel_zout = Mpu6050Compass.read_word_2c(0x3f)

        accel_xout_scaled = accel_xout / 16384.0
        accel_yout_scaled = accel_yout / 16384.0
        accel_zout_scaled = accel_zout / 16384.0

        logger.debug("accel_xout: %f scaled: %f", accel_xout, accel_xout_scaled)
        logger.debug("accel_yout: %f scaled: %f", accel_yout, accel_yout_scaled)
        logger.debug("accel_zout: %f scaled: %f", accel_zout, accel_zout_scaled)

        return Mpu6050Compass.get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)

    @staticmethod
    def read_byte(adr):
        return Mpu6050Compass.bus.read_byte_data(Mpu6050Compass.address, adr)

    @staticmethod
    def read_word(adr):
        high = Mpu6050Compass.bus.read_byte_data(Mpu6050Compass.address, adr)
        low = Mpu6050Compass.bus.read_byte_data(Mpu6050Compass.address, adr + 1)
        val = (high << 8) + low
        return val

    @staticmethod
    def read_word_2c(adr):
        val = Mpu6050Compass.read_word(adr)

        if val >= 0x8000:
            return -((65535 - val) + 1)
        else:
            return val

    @staticmethod
    def dist(a, b):
        return math.sqrt((a * a) + (b * b))

    @staticmethod
    def get_y_rotation(x, y, z):
        radians = math.atan2(x, Mpu6050Compass.dist(y, z))

        return -math.degrees(radians)

    @staticmethod
    def get_x_rotation(x, y, z):
        radians = math.atan2(y, Mpu6050Compass.dist(x, z))

        return math.degrees(radians)

    def get_description(self) -> str:
        return "MPU-6050 accelerometer"
