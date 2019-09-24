import glob
import logging
from abc import ABC, abstractmethod

import exifread
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QImage, QPainter

from utils import photo_utils

logger = logging.getLogger(__name__)


class AbstractMediaPlayer(ABC):
    """
    Abstract base class for all media players
    """

    def __init__(self, name, folder, compass):
        """
        Create a default abstract media player.
        All sub-classes should call this constructor.

        :param name: string used to refer to the media player
        :param folder: folder containing the media (images, video...)
        """
        self._name = name
        self.compass = compass
        self._folder = folder
        self._media_list = None
        self._current_media_index = None

        # load logo
        self.logo_large = QImage("logo.png")
        self.logo_small = self.logo_large.scaledToWidth(50, QtCore.Qt.SmoothTransformation)

        self.refresh_media_list()

    @abstractmethod
    def get_main_widget(self):
        """
        Get the top-level widget of the media player

        :return: the top-level widget
        """

    def refresh_media_list(self):
        """
        Re-load the media list from the filesystem

        :return: a list of filenames
        """
        logger.debug("Refreshing media list for %s in folder %s", self.get_name(), self.get_folder())
        self._media_list = glob.glob(self.get_folder() + "/*")

        # leave index unchanged if possible (to allow playlist to be refreshed without side-effect of jumping to start
        if self._current_media_index and self._current_media_index >= len(self._media_list):
            self._current_media_index = None
            logger.debug("Reset _current_media_index to None")
        logger.debug("Loaded photo list: %s", self._media_list)

    def get_name(self):
        """
        Get the name of the media player

        :return: textual name of the media player
        """
        return self._name

    def get_folder(self):
        """
        Get the location of the folder containing the media

        :return: the folder name
        """
        return self._folder

    def get_playlist(self):
        """
        Get a list of media to be played by this media player

        :return: list of filenames
        """
        return self._media_list

    @abstractmethod
    def show_current_media(self):
        """
        Display the current media. Must be overridden by each sub-class.
        :return: True if the media can the loaded, otherwise False (missing file, incompatible frame rotation etc)
        """

    def get_current_media_exif(self):
        # make sure we have a list of media and a current pointer
        if not all([self._media_list, self._current_media_index]):
            # self.main_window.setText("Media Player %s: No media to show" % self.get_name())
            return None, None

        image_filename = self._media_list[self._current_media_index]
        with open(image_filename, 'rb') as f:
            return image_filename, exifread.process_file(f, details=False)

    def next(self):
        """
        Display the next media. If at the end of the playlist, jump to the start
        """

        def passed_end(i, l):
            return i >= len(l) - 1

        def jump_to_start(_unused_i, _unused_l):
            return 0

        def move_to_next(i):
            return i + 1

        return self._next_or_prev(passed_end, jump_to_start, move_to_next)

    def prev(self):
        """
        Display the previous media. If at the start of the playlist, jump to the end
        """

        def before_start(i, _unused_l):
            return i <= 0

        def jump_to_end(_unused_i, l):
            return len(l) - 1

        def move_to_prev(i):
            return i - 1

        return self._next_or_prev(before_start, jump_to_end, move_to_prev)

    def splash_screen(self):
        angle_to_rotate_photo = 0

        # detect if frame is rotated
        if self.compass:
            logger.debug("Frame rotated by %d", self.compass.get_rotation_simple())
            angle_to_rotate_photo = -self.compass.get_rotation_simple()

        self.main_window.setPixmap(QtGui.QPixmap.fromImage(
            self.logo_large.transformed(QtGui.QTransform().rotate(angle_to_rotate_photo))).scaled(
            self.get_main_widget().size() / 2,
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation))

    def paint_logo(self, pmap):
        """
        Overlay the logo on a pixmap
        :param pmap: the photo
        """
        painter = QPainter()
        painter.begin(pmap)
        painter.drawImage(pmap.width() - self.logo_small.width() - 40,
                          pmap.height() - self.logo_small.height() - 10, self.logo_small)
        painter.end()

    def _next_or_prev(self, is_boundary, jump, move):
        self.refresh_media_list()

        invalid_media = True
        ctr = 0
        while invalid_media and ctr < len(self._media_list):
            # prevent looping forever in case no images match
            logger.debug("ctr = %d", ctr)

            logger.debug("_current_media_index = %s", self._current_media_index)
            logger.debug("length _media_list = %d", len(self._media_list))
            if self._current_media_index is None or is_boundary(self._current_media_index, self._media_list):
                logger.debug("Jumping to other end of media list")
                self._current_media_index = jump(self._current_media_index, self._media_list)
            else:
                logger.debug("Moving to neighbouring media item")
                self._current_media_index = move(self._current_media_index)

            invalid_media = not self.show_current_media()
            ctr += 1


class VideoPlayer(AbstractMediaPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_main_widget(self):
        # TODO implement video player
        pass

    def show_current_media(self):
        pass


class PhotoPlayer(AbstractMediaPlayer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = QtWidgets.QLabel()
        self.main_window.setAlignment(QtCore.Qt.AlignCenter)

    def get_main_widget(self):
        return self.main_window

    def show_current_media(self):
        if not self._media_list:
            self.main_window.setText("Media Player %s: No media to show" % self.get_name())
            return True

        angle_to_rotate_photo = 0

        # load image from the file
        image_filename = self._media_list[self._current_media_index]
        logger.debug("Loading image %s", image_filename)

        # we alwways need this (even to discard incompatible network) so check now
        exif_orientation = photo_utils.get_file_exif_orientation(image_filename)

        # if frame rotation detection is supported, skip portrait network if frame is in landscape mode (and vice versa)
        if self.compass:

            is_portrait_frame_check = self.compass.is_portrait_frame()

            image = QImage(image_filename)
            if exif_orientation:
                is_portrait_image_check = photo_utils.is_portrait(image.width(), image.height(), exif_orientation)
            else:
                is_portrait_image_check = photo_utils.is_portrait(image.width(), image.height())

            logger.debug("Is frame in portrait mode? %s", is_portrait_frame_check)
            logger.debug("Is image in portrait mode? %s", is_portrait_image_check)

            # check compatibility of frame with photo rotation (must be the same)
            if is_portrait_frame_check != is_portrait_image_check:
                logging.debug("Frame rotation does not match photo rotation. Skipping %s.", image_filename)
                self.main_window.setText("Frame rotation does not match photo rotation. Skipping %s." % image_filename)
                return False

            # if we get here, the photo is compatible

            # rotate the photo based on the frame orientation
            logger.debug("Frame rotated by %d", self.compass.get_rotation_simple())
            angle_to_rotate_photo = -self.compass.get_rotation_simple()

        # rotate the photo based on the photo EXIF rotation
        if exif_orientation:
            photo_rotation = photo_utils.get_exif_rotation_angle(exif_orientation)
            logger.debug("Photo rotated by %d", photo_rotation)
            angle_to_rotate_photo = angle_to_rotate_photo - photo_rotation

        image = QtGui.QImage(image_filename)
        if image:
            image = image.transformed(QtGui.QTransform().rotate(angle_to_rotate_photo))
            pmap = QtGui.QPixmap.fromImage(image).scaled(
                self.get_main_widget().size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation)

            self.paint_logo(pmap)

            self.main_window.setPixmap(pmap)
            return True

        logger.info("Could not load image: %s", image_filename)
        return False
