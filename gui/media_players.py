import glob
import logging
import random
from abc import abstractmethod
from typing import List

import exifread
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QImage, QPainter

from gui.players import PhotoFrameContent
from utils import photo_utils

logger = logging.getLogger(__name__)


class AbstractMediaPlayer(PhotoFrameContent):
    """
    Abstract base class for all media players
    """

    def __init__(self, name, folder, photo_frame, shuffle):
        """
        Create a default abstract media player.
        All sub-classes should call this constructor.

        :param name: string used to refer to the media player
        :param folder: folder containing the media (images, video...)
        :param shuffle: toggle random slidedown
        :param photo_frame: reference to the photo frame
        """
        super().__init__(name, photo_frame)

        self._folder = folder
        self._shuffle = shuffle
        self._media_list = None
        self.current_media_index = None
        self.browsing_history = []

        self._refresh_media_list()

    def _refresh_media_list(self):
        """
        Re-load the media list from the filesystem

        :return: a list of filenames
        """
        logger.debug("Refreshing media list for %s in folder %s", self.get_name(), self.get_folder())
        self._media_list = glob.glob(self.get_folder() + "/*")

        # leave index unchanged if possible (to allow playlist to be refreshed without side-effect of jumping to start
        if self.current_media_index and self.current_media_index >= len(self._media_list):
            self.current_media_index = None
            logger.debug("Reset _current_media_index to None")
        logger.debug("Loaded photo list: %s", self._media_list)

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
        if None in [self._media_list, self.current_media_index]:
            # self.main_window.setText("Media Player %s: No media to show" % self.get_name())
            return None, None

        image_filename = self._media_list[self.current_media_index]
        with open(image_filename, 'rb') as f:
            return image_filename, exifread.process_file(f, details=False)

    def next(self):
        """
        Display the next media. If at the end of the playlist, jump to the start
        """

        def at_end(i, media_list):
            return i >= len(media_list) - 1

        def jump_to_start(_unused_i, _unused_media_list):
            return 0

        def move_to_next(i, _unused_media_list):
            return i + 1

        def random_jump(_unused_i, media_list):
            return random.randint(0, len(media_list) - 1)

        if self._shuffle:
            logger.debug("Getting random photo")
            return self._move(lambda x, y: False, random_jump, random_jump)

        logger.info("Moving to next photo")
        self._move(at_end, jump_to_start, move_to_next)

    def prev(self):
        """
        Display the previously visited media. Stop when we get to the start of the browsing history.
        """
        # remove current entry from history
        if self.browsing_history:
            self.browsing_history.pop()

        # jump to the previous entry (if any)
        if self.browsing_history:
            self.current_media_index = self.browsing_history[-1]
            self.show_current_media()
        else:
            logger.debug("No more browsing history")
            self.current_media_index = None

    def old_prev(self):
        """
        Display the previous media. If at the start of the playlist, jump to the end
        """

        def before_start(i, _unused_media_list):
            return i <= 0

        def jump_to_end(_unused_i, media_list):
            return len(media_list) - 1

        def move_to_prev(i, _unused_media_list):
            return i - 1

        return self._move(before_start, jump_to_end, move_to_prev)

    def paint_logo(self, pmap):
        """
        Overlay the logo on a pixmap
        :param pmap: the photo
        """
        painter = QPainter()
        painter.begin(pmap)
        painter.drawImage(pmap.width() - self.photo_frame.logo_small.width() - 40,
                          pmap.height() - self.photo_frame.logo_small.height() - 10, self.photo_frame.logo_small)
        painter.end()

    def _move(self, is_boundary, jump, move):
        self._refresh_media_list()

        invalid_media = True
        ctr = 0
        while invalid_media and ctr < len(self._media_list):
            # prevent looping forever in case no images match
            logger.debug("ctr = %d", ctr)

            logger.debug("_current_media_index = %s", self.current_media_index)
            logger.debug("length _media_list = %d", len(self._media_list))

            if self.current_media_index is None or is_boundary(self.current_media_index, self._media_list):
                logger.debug("Jumping to other end of media list")
                self.current_media_index = jump(self.current_media_index, self._media_list)
            else:
                logger.debug("Moving to neighbouring media item")
                self.current_media_index = move(self.current_media_index, self._media_list)

            invalid_media = not self.show_current_media()
            ctr += 1

        # update the browsing history
        self.browsing_history.append(self.current_media_index)


class VideoPlayer(AbstractMediaPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_main_widget(self):
        # TODO implement video player
        pass

    def show_current_media(self):
        pass

    def get_properties(self) -> List[str]:
        return ["not implemented"]

    def get_description(self) -> str:
        return "a video player"


class PhotoPlayer(AbstractMediaPlayer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.main_window = QtWidgets.QLabel()
        self.main_window.setAlignment(QtCore.Qt.AlignCenter)

    def get_main_widget(self):
        return self.main_window

    def show_current_media(self):
        logger.debug("Showing media %d", self.current_media_index)

        if not self._media_list:
            self.main_window.setText("Media Player %s: No media to show" % self.get_name())
            return True

        angle_to_rotate_photo = 0

        # load image from the file
        image_filename = self._media_list[self.current_media_index]
        logger.debug("Loading image %s", image_filename)

        # we alwways need this (even to discard incompatible network) so check now
        exif_orientation = photo_utils.get_file_exif_orientation(image_filename)

        # if frame rotation detection is supported, skip portrait network if frame is in landscape mode (and vice versa)
        if self.photo_frame.compass:

            is_portrait_frame_check = self.photo_frame.compass.is_portrait_frame()

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
            logger.debug("Frame rotated by %d", self.photo_frame.compass.get_rotation_simple())
            angle_to_rotate_photo = -self.photo_frame.compass.get_rotation_simple()

        # rotate the photo based on the photo EXIF rotation
        if exif_orientation:
            photo_rotation = photo_utils.get_exif_rotation_angle(exif_orientation)
            logger.debug("Photo rotated by %d", photo_rotation)
            angle_to_rotate_photo = angle_to_rotate_photo - photo_rotation

        image = QtGui.QImage(image_filename)
        if image:
            pmap = QtGui.QPixmap.fromImage(image)
            logger.debug("Rotating photo by %f", angle_to_rotate_photo)
            logger.debug("Scaling photo to %s", self.photo_frame.frame_size)
            pmap = pmap.transformed(QtGui.QTransform().rotate(angle_to_rotate_photo)).scaled(
                self.photo_frame.frame_size,
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation)

            # add the watermark (unrotate, watermark, rotate)
            pmap = pmap.transformed(QtGui.QTransform().rotate(-angle_to_rotate_photo))
            self.paint_logo(pmap)
            pmap = pmap.transformed(QtGui.QTransform().rotate(angle_to_rotate_photo))

            self.main_window.setPixmap(pmap)
            return True

        logger.info("Could not load image: %s", image_filename)
        return False

    def get_properties(self) -> List[str]:
        return [
            "folder = %s" % self.get_folder(),
            "# photos = %d" % len(self.get_playlist()),
            "shuffle = %s" % self._shuffle
        ]

    def get_description(self) -> str:
        return "a photo viewer for showing photo slideshows"