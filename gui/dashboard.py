from hurry.filesize import size
import psutil
import logging
from typing import List

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QSizePolicy

import utils.orientation
from gui.players import PhotoFrameContent

logger = logging.getLogger(__name__)


class FrameDashboard(PhotoFrameContent):

    def __init__(self, name: str, compass: utils.orientation.Compass, photo_frame):
        super().__init__(name, compass)
        self.photo_frame = photo_frame

        self.main_window = QtWidgets.QWidget(self.photo_frame)
        # self.main_window.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        # self.main_window.setFixedSize(self.photo_frame.frame_size)

        self.machine_summary_widget = None
        self.frame_summary_widget = None
        self.player_list_widget = None

        self._build_ui()
        self._update()

    def _build_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self.main_window)
        main_layout.setAlignment(QtCore.Qt.AlignHCenter)
        self.main_window.setLayout(main_layout)

        no_vstretch_policy = QSizePolicy()
        no_vstretch_policy.setVerticalStretch(0)
        # no_vstretch_policy.setHorizontalPolicy(QSizePolicy.Fixed)

        heading = QtWidgets.QLabel(self.main_window)
        heading.setAlignment(QtCore.Qt.AlignCenter)
        heading.setText("<p><b>Dashboard</b><p><hr>")
        heading.setFixedWidth(self.photo_frame.frame_size.width() * 0.7)
        heading.setSizePolicy(no_vstretch_policy)
        main_layout.addWidget(heading)

        machine_summary_widget = QtWidgets.QFrame()
        machine_summary_widget.setFrameStyle(QtWidgets.QFrame.Panel)
        machine_summary_widget_layout = QtWidgets.QVBoxLayout(machine_summary_widget)
        machine_summary_widget.setLayout(machine_summary_widget_layout)
        machine_summary_widget.setSizePolicy(no_vstretch_policy)
        machine_summary_widget.setFixedWidth(self.photo_frame.frame_size.width() * 0.7)

        self.machine_summary_widget = QtWidgets.QLabel(machine_summary_widget)
        self.machine_summary_widget.setAlignment(QtCore.Qt.AlignLeft)
        machine_summary_widget_layout.addWidget(self.machine_summary_widget)

        main_layout.addWidget(machine_summary_widget)

        frame_summary_widget = QtWidgets.QFrame()
        frame_summary_widget.setFrameStyle(QtWidgets.QFrame.Panel)
        frame_summary_widget_layout = QtWidgets.QVBoxLayout(frame_summary_widget)
        frame_summary_widget.setLayout(frame_summary_widget_layout)
        frame_summary_widget.setSizePolicy(no_vstretch_policy)
        frame_summary_widget.setFixedWidth(self.photo_frame.frame_size.width() * 0.7)

        self.frame_summary_widget = QtWidgets.QLabel(frame_summary_widget)
        self.frame_summary_widget.setAlignment(QtCore.Qt.AlignLeft)
        frame_summary_widget_layout.addWidget(self.frame_summary_widget)

        main_layout.addWidget(frame_summary_widget)

        player_frame = QtWidgets.QFrame()
        player_frame.setFrameStyle(QtWidgets.QFrame.Panel)
        player_frame_layout = QtWidgets.QVBoxLayout(player_frame)
        player_frame.setLayout(player_frame_layout)

        self.player_list_widget = QtWidgets.QLabel(player_frame)
        self.player_list_widget.setAlignment(QtCore.Qt.AlignLeft)
        player_frame_layout.addWidget(self.player_list_widget)

        main_layout.addWidget(player_frame)

    def get_main_widget(self):
        return self.main_window

    def _update_machine_summary(self):
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        summary_entries = [
            "<b>CPU load:</b> %s%%" % psutil.cpu_percent(),
            "<b>Total memory:</b> %s" % size(memory.total),
            "<b>Available memory:</b> %s" % size(memory.available),
            "<b>Total disk space:</b> %s" % size(disk.total),
            "<b>Used disk space:</b> %s" % size(disk.used),
            "<b>Free disk space:</b> %s" % size(disk.free)
        ]

        if hasattr(psutil, "sensors_temperatures"):
            temp = psutil.sensors_temperatures()
            summary_entries.append(["<b>CPU temp</b> %s" % temp])

        summary_text = "<br>".join(summary_entries)
        logger.info(summary_text)

        self.machine_summary_widget.setText(summary_text)

    def _update_frame_summary(self):
        summary_entries = [
            "<b>Number of players:</b> %d" % len(self.photo_frame.players),
            "<b>Slideshow delay:</b> %d" % self.photo_frame.slideshow_delay,
            "<b>Root folder:</b> %s" % self.photo_frame.root_folder,
            "<b>Compass:</b> %s" % self.photo_frame.compass.get_description(),
            "<b>Flip rotation:</b> %s" % self.photo_frame.flip_rotation
        ]
        summary_text = "<br>".join(summary_entries)
        logger.debug(summary_text)

        # self.db_content.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        # self.db_content.setFixedSize(self.photo_frame.width() * 0.7, self.photo_frame.height())
        self.frame_summary_widget.setText(summary_text)

    def _update_player_list(self):
        player_list_entries = ["<b>Player list:</b>"] + [self._get_player_entry(player) for player in
                                                         self.photo_frame.players]
        player_list_text = "<br>".join(player_list_entries)
        logger.debug(player_list_text)
        self.player_list_widget.setText(player_list_text)

    def _get_player_entry(self, player: PhotoFrameContent):
        properties = ["<li>%s</li>" % p for p in player.get_properties()]
        return "<b>%s</b> - %s<ul>" % (player.get_name(), player.get_description()) + "".join(properties) + "</ul>"

    def _update(self):
        logger.debug("Updating dashboard")
        self._update_machine_summary()
        self._update_frame_summary()
        self._update_player_list()

    def next(self):
        self._update()

    def prev(self):
        self._update()

    def get_properties(self) -> List[str]:
        return ["-"]

    def get_description(self) -> str:
        return "a system dashboard to show the current state of the photo frame"
