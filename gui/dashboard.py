import logging

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QSizePolicy

# import gui.photo_app
from gui.players import PhotoFrameContent
import utils.orientation

logger = logging.getLogger(__name__)


class FrameDashboard(PhotoFrameContent):

    def __init__(self, name: str, compass: utils.orientation.Compass, photo_frame):
        super().__init__(name, compass)
        self.photo_frame = photo_frame

        self.main_window = QtWidgets.QWidget(self.photo_frame)
        self.main_window.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.main_window.setFixedSize(self.photo_frame.frame_size)

        # Create a label to contain the dashboard text.
        # This is separate from the main window so it can be left-aligned, but centred
        self.db_content = QtWidgets.QLabel(self.main_window)
        self.db_content.setAlignment(QtCore.Qt.AlignCenter)

        # centre the label
        layout = QtWidgets.QGridLayout(self.main_window)
        layout.setAlignment(QtCore.Qt.AlignHCenter)
        self.main_window.setLayout(layout)
        layout.addWidget(self.db_content)

    def get_main_widget(self):
        return self.db_content

    def _update(self):
        dashboard_entries = [
                                "<b>Dashboard</b><p>",
                                "<hr>",
                                "<b>Number of players:</b> %d" % len(self.photo_frame.players),
                                "<b>Slideshow delay:</b> %d" % self.photo_frame.slideshow_delay,
                                "<b>Root folder:</b> %s" % self.photo_frame.root_folder,
                                "<b>Compass:</b> %s" % self.photo_frame.compass.get_description(),
                                "<b>Flip rotation:</b> %s" % self.photo_frame.flip_rotation,
                                "<hr>",
                                "<br><b>Player list:</b>",
                                "<ul>"
                            ] + \
                            ["<li><b>%s</b> : %s</li>" % (player.get_name(), player.get_description()) for player in
                             self.photo_frame.players]

        dashboard_text = "<br>".join(dashboard_entries)
        logger.debug(dashboard_text)

        # set size to only use part of the screen, and align left
        self.db_content.setAlignment(QtCore.Qt.AlignLeft)
        self.db_content.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.db_content.setFixedSize(self.photo_frame.width() * 0.7, self.photo_frame.height())
        self.db_content.setText(dashboard_text)

    def next(self):
        self._update()

    def prev(self):
        self._update()

    def get_description(self):
        return "-"
