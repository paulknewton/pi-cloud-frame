from abc import ABC, abstractmethod


class Compass(ABC):
    """
    Sensor to detect rotation of a frame
    """

    def __init__(self):
        self._compass_angle = 90  # default - no rotation (landscape)

    @abstractmethod
    def get_rotation(self):
        """
        Get the angle the frame is currently rotated.
        The angle is not rounded.
        :return: the angle
        """
        pass

    def get_rotation_simple(self):
        """
        Return the angle of rotation, rounded to each quadrant of 90 degrees (0, 90, 180, 270).
        Actual angle may be -ve, but returned value is always 0 <= value < 360 (modulo 360)
        :return: the angle
        """
        angle = self.get_rotation()
        if angle == 0:
            return 0

        rounded = int((abs(angle) + 45) / 90) * 90 * int(angle / abs(angle))
        return rounded % 360

    def is_portrait_frame(self):
        """
        Check if the frame is rotated in portrait mode
        :return: True if portrait mode, False if landscape mode
        """
        return self.get_rotation_simple() % 180 == 90

    def is_landscape_frame(self):
        """
        Check if the frame is rotated in landscape mode
        :return: True if landscape mode, False if portrait mode
        """
        return not self.is_portrait_frame()
