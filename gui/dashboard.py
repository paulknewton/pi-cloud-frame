import logging
from typing import List

import psutil
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QSizePolicy
from hurry.filesize import size

import utils.orientation
from gui.photo_app import PhotoFrame
from gui.players import PhotoFrameContent

logger = logging.getLogger(__name__)


class FrameDashboard(PhotoFrameContent):

    def __init__(self, name: str, photo_frame: PhotoFrame):
        super().__init__(name, photo_frame)

        self.main_window = QtWidgets.QWidget(self.photo_frame)
        # self.main_window.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        # self.main_window.setFixedSize(self.photo_frame.frame_size)

        self.machine_text = None
        self.frame_text = None
        self.player_text = None

        self._build_ui()
        self._update()

    def _build_ui(self):
        # align each section in a centred, vertical column
        main_layout = QtWidgets.QGridLayout(self.main_window)
        main_layout.setAlignment(QtCore.Qt.AlignHCenter)
        self.main_window.setLayout(main_layout)

        no_vstretch_policy = QSizePolicy()
        no_vstretch_policy.setVerticalStretch(0)
        # no_vstretch_policy.setHorizontalPolicy(QSizePolicy.Fixed)

        # title
        # heading = QtWidgets.QLabel()
        #
        # heading.setAlignment(QtCore.Qt.AlignCenter)
        # heading.setText("<p><b>Dashboard</b>")
        # heading.setFixedWidth(self.photo_frame.frame_size.width() * 0.3)
        # heading.setSizePolicy(no_vstretch_policy)
        #main_layout.addWidget(heading, 0, 0, 0, 1)

        # machine info
        machine_group = QtWidgets.QFrame()
        machine_group.setFrameStyle(QtWidgets.QFrame.Panel)
        machine_layout = QtWidgets.QVBoxLayout(machine_group)
        machine_group.setLayout(machine_layout)
        machine_group.setSizePolicy(no_vstretch_policy)
        machine_group.setFixedWidth(self.photo_frame.frame_size.width() * 0.2)

        self.machine_text = QtWidgets.QLabel(machine_group)
        font = machine_group.font()
        font.setPointSize(font.pointSize() - 2)
        machine_group.setFont(font)
        self.machine_text.setAlignment(QtCore.Qt.AlignLeft)
        machine_layout.addWidget(self.machine_text)

        main_layout.addWidget(machine_group, 0, 0)

        # frame info
        frame_group = QtWidgets.QFrame()
        frame_group.setFrameStyle(QtWidgets.QFrame.Panel)
        frame_layout = QtWidgets.QVBoxLayout(frame_group)
        frame_group.setLayout(frame_layout)
        frame_group.setSizePolicy(no_vstretch_policy)
        frame_group.setFixedWidth(machine_group.size().width())

        self.frame_text = QtWidgets.QLabel(frame_group)
        font = frame_group.font()
        font.setPointSize(font.pointSize() - 2)
        frame_group.setFont(font)
        self.frame_text.setAlignment(QtCore.Qt.AlignLeft)
        frame_layout.addWidget(self.frame_text)

        main_layout.addWidget(frame_group, 0, 1)

        # list of players
        player_group = QtWidgets.QFrame()
        player_group.setFrameStyle(QtWidgets.QFrame.Panel)
        player_layout = QtWidgets.QVBoxLayout(player_group)
        player_group.setLayout(player_layout)

        self.player_text = QtWidgets.QLabel(player_group)
        self.player_text.setText("hello")
        font = self.player_text.font()
        font.setPointSize(font.pointSize() - 2)
        self.player_text.setFont(font)
        self.player_text.setAlignment(QtCore.Qt.AlignLeft)
        player_layout.addWidget(self.player_text)

        # add a scrollbar
        #scroll = QtWidgets.QScrollArea(player_group)
        #scroll.setWidget(self.player_text)

        main_layout.addWidget(player_group, 1, 0, 1, 2)

    def get_main_widget(self):
        return self.main_window

    def _update_machine_summary(self):
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        summary_entries = [
            "<b>CPU load:</b> %s%%" % psutil.cpu_percent(),
            # "<b>Total memory:</b> %s" % size(memory.total),
            "<b>Available memory:</b> %s" % size(memory.available),
            # "<b>Total disk space:</b> %s" % size(disk.total),
            "<b>Used disk space:</b> %s" % size(disk.used),
            "<b>Free disk space:</b> %s" % size(disk.free)
        ]

        if hasattr(psutil, "sensors_temperatures"):
            temp = psutil.sensors_temperatures()
            summary_entries.append("<b>CPU temp</b> %s" % temp)

        summary_text = "<br>".join(summary_entries)
        logger.debug(summary_text)

        self.machine_text.setText(summary_text)

    def _update_frame_summary(self):
        summary_entries = [
            "<b>Number of players:</b> %d" % len(self.photo_frame.players),
            "<b>Slideshow delay:</b> %d" % self.photo_frame.slideshow_delay,
            "<b>Root folder:</b> %s" % self.photo_frame.root_folder,
            "<b>Flip rotation:</b> %s" % self.photo_frame.flip_rotation
        ]

        if self.photo_frame.compass:
            summary_entries.append("<b>Compass:</b> %s" % self.photo_frame.compass.get_description())
        summary_text = "<br>".join(summary_entries)
        logger.debug(summary_text)

        # self.db_content.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        # self.db_content.setFixedSize(self.photo_frame.width() * 0.7, self.photo_frame.height())
        self.frame_text.setText(summary_text)

    def _update_player_list(self):
        player_list_entries = [self._get_player_entry(player) for player in self.photo_frame.players]
        player_list_text = "<br>".join(player_list_entries)
        logger.debug(player_list_text)
        self.player_text.setText(player_list_text)

    def _get_player_entry(self, player: PhotoFrameContent):
        properties = player.get_properties()
        properties_text: List[str] = []
        if properties:
            properties_text = ["<li>%s</li>" % p for p in properties]
        return "<b>%s</b> - %s<ul>" % (player.get_name(), player.get_description()) + "".join(properties_text) + "</ul>"

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
        return []

    def get_description(self) -> str:
        return "a system dashboard to show the current state of the photo frame"
