import logging
from abc import ABC, abstractmethod
from typing import List

from PyQt5.QtWidgets import QWidget

logger = logging.getLogger(__name__)


class PhotoFrameContent(ABC):

    def __init__(self, name: str, photo_frame):
        self._name = name
        self.photo_frame = photo_frame

    @abstractmethod
    def get_main_widget(self) -> QWidget:
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

    def get_name(self) -> str:
        """
        Get the name of the media player

        :return: textual name of the media player
        """
        return self._name

    def get_properties(self) -> List[str]:
        pass

    def get_description(self) -> str:
        pass
