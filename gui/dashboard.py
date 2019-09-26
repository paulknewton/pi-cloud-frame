import logging

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QSizePolicy

import gui.photo_app
from gui.players import PhotoFrameContent
import utils.orientation

logger = logging.getLogger(__name__)


class FrameDashboard(PhotoFrameContent):

    def __init__(self, name: str, compass: utils.orientation.Compass, photo_frame: gui.photo_app.PhotoFrame):
        super().__init__(name, compass)
        self.photo_frame = photo_frame

        self.main_window = QtWidgets.QLabel()
        # Need to set the alignment here even if a layout is used further down
        # because the splash screen is set on the label directly
        self.main_window.setAlignment(QtCore.Qt.AlignCenter)

        # Create a label to contain the dashboard text.
        # This is separate from the main window so it can be lef-aligned, but centred
        self.db_content = QtWidgets.QLabel()
        self.db_content.setAlignment(QtCore.Qt.AlignLeft)

        # size should not be dependent on the text label
        self.db_content.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.db_content.setFixedSize(self.photo_frame.width() / 2, self.photo_frame.height())

        # centre the label
        layout = QtWidgets.QVBoxLayout(self.photo_frame)
        layout.setAlignment(QtCore.Qt.AlignHCenter)
        self.main_window.setLayout(layout)
        layout.addWidget(self.db_content)

    def get_main_widget(self):
        # return the main window because this is used for the splash screen
        return self.main_window

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
        logger.info(dashboard_text)

        # clear the splash screen from the main window (if any)
        self.main_window.clear()

        self.db_content.setText(dashboard_text)

    def next(self):
        self._update()

    def prev(self):
        self._update()

    def get_description(self):
        return "-"
