import logging
from abc import ABC, abstractmethod

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

    @staticmethod
    def get_properties(self):
        pass

    @staticmethod
    def get_description(self):
        pass
