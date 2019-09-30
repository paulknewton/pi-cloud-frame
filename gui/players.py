import logging
from abc import ABC, abstractmethod

from PyQt5 import QtCore, QtGui

logger = logging.getLogger(__name__)


class PhotoFrameContent(ABC):

    def __init__(self, name, photo_frame):
        self._name = name
        self.photo_frame = photo_frame

    @abstractmethod
    def get_main_widget(self):
        """
        Get the top-level widget of the media player

        :return: the top-level widget
        """

    @abstractmethod
    def next(self):
        pass

    @abstractmethod
    def prev(self):
        pass

    def get_name(self):
        """
        Get the name of the media player

        :return: textual name of the media player
        """
        return self._name

    def splash_screen(self):
        angle_to_rotate_photo = 0

        # detect if frame is rotated
        if self.photo_frame.compass:
            logger.debug("Frame rotated by %d", self.photo_frame.compass.get_rotation_simple())
            angle_to_rotate_photo = -self.photo_frame.compass.get_rotation_simple()

        logger.debug("Rotating photo by %f", angle_to_rotate_photo)
        self.get_main_widget().setPixmap(QtGui.QPixmap.fromImage(
            self.photo_frame.logo_large.transformed(QtGui.QTransform().rotate(angle_to_rotate_photo))).scaled(
            self.photo_frame.frame_size / 2,
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation))

    @staticmethod
    def get_properties(self):
        pass

    @staticmethod
    def get_description(self):
        pass
