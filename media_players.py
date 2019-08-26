import exifread
import glob
import logging
from abc import ABC, abstractmethod

from PyQt5 import QtWidgets, QtCore, QtGui

logger = logging.getLogger(__name__)


class AbstractMediaPlayer(ABC):
    """
    Abstract base class for all media players
    """

    def __init__(self, name, folder):
        """
        Create a default abstract media player.
        All sub-classes should call this parent constructor.

        :param name: string used to refer to the media player
        :param folder: folder containing the media (images, video...)
        """
        self._name = name
        self._folder = folder
        self._media_list = None
        self._current_media_index = None

        self.refresh_media_list()

    @abstractmethod
    def get_main_widget(self):
        """
        Get the top-level widget of the media player

        :return: the top-level widget
        """
        pass

    def refresh_media_list(self):
        """
        Re-load the media list from the filesystem

        :return: a list of filenames
        """
        logger.debug("Refreshing media list for %s in folder %s", self.get_name(), self.get_folder())
        self._media_list = glob.glob(self.get_folder() + "/*")

        # leave index unchanged if possible (to allow playlist to be refreshed without side-effect of jumping to start
        if not self._current_media_index or self._current_media_index >= len(self._media_list):
            self._current_media_index = 0
            logger.debug("Reset _current_media_index to 0")
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
        Display the current media
        """
        pass

    def get_current_media_exif(self):
        if not self._media_list:
            self.main_window.setText("Media Player %s: No media to show" % self.get_name())
            return

        image_filename = self._media_list[self._current_media_index]
        with open(image_filename, 'rb') as f:
            return image_filename, exifread.process_file(f, details=False)

    def next(self):
        """
        Display the next media. If at the end of the playlist, jump to the start
        """
        self.refresh_media_list()

        logger.debug("_current_media_index = %d", self._current_media_index)
        logger.debug("length _media_list = %d", len(self._media_list))
        if self._current_media_index >= len(self._media_list) - 1:
            logger.debug("Starting at beginning of media")
            self._current_media_index = 0
        else:
            self._current_media_index += 1
            logger.debug("Setting _current_media_index to %d", self._current_media_index)
        self.show_current_media()

    def prev(self):
        """
        Display the previous media. If at the start of the playlist, jump to the end
        """
        self.refresh_media_list()

        if self._current_media_index <= 0:
            logger.debug("Starting at end of media")
            self._current_media_index = len(self._media_list) - 1
        else:
            self._current_media_index -= 1
        self.show_current_media()


class VideoPlayer(AbstractMediaPlayer):
    def __init__(self, name, folder):
        super().__init__(name, folder)

    def get_main_widget(self):
        # TODO implement video player
        pass

    def show_current_media(self):
        # TODO implement video player
        pass


class PhotoPlayer(AbstractMediaPlayer):

    def __init__(self, name, folder):
        super().__init__(name, folder)
        self.main_window = QtWidgets.QLabel()
        self.main_window.setAlignment(QtCore.Qt.AlignCenter)

    def get_main_widget(self):
        return self.main_window

    def show_current_media(self):
        if not self._media_list:
            self.main_window.setText("Media Player %s: No media to show" % self.get_name())
            return

        image_filename = self._media_list[self._current_media_index]
        logger.debug("Showing image %s", image_filename)
        image = QtGui.QImage(image_filename)
        if image:
            pmap = QtGui.QPixmap.fromImage(image)
            self.main_window.setPixmap(pmap.scaled(
                self.get_main_widget().size(),
                QtCore.Qt.KeepAspectRatio,
                QtCore.Qt.SmoothTransformation))
        else:
            logger.info("Could not load image: %s", image_filename)
