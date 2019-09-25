import collections
import logging
import os
import sys

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QFont, QImage
from PyQt5.QtWidgets import QDialog, QLabel, QGridLayout, QPushButton

from gui.media_players import VideoPlayer, PhotoPlayer
from utils import photo_utils

logger = logging.getLogger(__name__)


class Popup(QDialog):
    def __init__(self, frame, font_size):
        super().__init__()
        self.frame = frame  # to access methods on the photo frame

        self.font_size = font_size
        self.setWindowModality(Qt.NonModal)
        self.setWindowFlag(Qt.FramelessWindowHint)

        self.labels = ["Filename:", "Date:", "Location:"]  # static labels
        # list of QLabel widgets, each corresponding to a static label
        self.value_widgets = None
        self._build_ui()

        # ref to current filename (used to delete files)
        self._current_filename = None

    def show_image_details(self, filename, exif_tags):
        """
        Display meta information about the selected photo in the popup dialog.

        :param filename: filename of the photo
        :param exif_tags: dictionary of EXIF tags for the photo
        """
        logger.debug("Filename: %s", self._current_filename)
        self._current_filename = filename
        if not filename:
            filename = "<unknown>"
        self.value_widgets[0].setText(filename)

        # extract EXIF data (set default values in case the information cannot be found)
        logger.debug("exif tags: %s", exif_tags)
        date = location = "<unknown>"

        if isinstance(exif_tags, collections.Mapping):
            long_ref = long = lat_ref = lat = ""
            if "EXIF DateTimeOriginal" in exif_tags.keys():
                date = str(exif_tags["EXIF DateTimeOriginal"])

            if "GPS GPSLatitudeRef" in exif_tags.keys():
                lat_ref = exif_tags["GPS GPSLatitudeRef"]

            if "GPS GPSLatitude" in exif_tags.keys():
                lat = exif_tags["GPS GPSLatitude"]

            if "GPS GPSLongitudeRef" in exif_tags.keys():
                long_ref = exif_tags["GPS GPSLongitudeRef"]

            if "GPS GPSLongitude" in exif_tags.keys():
                long = exif_tags["GPS GPSLongitude"]

            # if we have GPS data, reverse lookup address
            if all([lat, lat_ref, long, long_ref]):
                lat_d, lat_m, lat_s = tuple(lat.values)
                long_d, long_m, long_s = tuple(long.values)
                location = photo_utils.get_gps_location(lat_d.num / lat_d.den, lat_m.num / lat_m.den,
                                                        lat_s.num / lat_s.den,
                                                        lat_ref, long_d.num / long_d.den, long_m.num / long_m.den,
                                                        long_s.num / long_s.den, long_ref)

                # reformat lines
                location = "\n".join(location.split(", "))

        self.value_widgets[1].setText(date)
        self.value_widgets[2].setText(location)
        # self.date_label.adjustSize()
        self.show()

    def _build_ui(self):
        layout = QGridLayout(self)
        self.value_widgets = []

        # font used in popup dialog
        font_roman = QFont()
        font_roman.setPointSize(self.font_size)
        font_bold = QFont()
        font_bold.setPointSize(self.font_size)
        font_bold.setBold(True)

        # centred logo
        logo_label = QLabel(self)
        logo = QImage("logo_small.png")#.scaledToWidth(100, QtCore.Qt.SmoothTransformation)
        logo_label.setPixmap(QtGui.QPixmap.fromImage(logo))
        layout.addWidget(logo_label, 0, 0, 1, -1, QtCore.Qt.AlignCenter)  # span 2 columns

        # create labels and empty values
        for y, label in enumerate(self.labels):
            label_widget = QLabel(label, self)
            label_widget.setAlignment(QtCore.Qt.AlignRight)
            label_widget.setFont(font_bold)
            layout.addWidget(label_widget, y + 1, 0)

            value_widget = QLabel(self)
            value_widget.setFont(font_roman)
            layout.addWidget(value_widget, y + 1, 1)
            self.value_widgets.append(value_widget)

        delete_button = QPushButton("Delete photo", self)
        delete_button.clicked.connect(self.on_click)

        layout.addWidget(delete_button, len(self.labels), 0, 1, -1)  # span 2 columns

    @pyqtSlot()
    def on_click(self):
        """
        Callback for delete button. Remove the selected photo from the disk and close the popup.
        """
        if not self._current_filename:
            logger.error("Filename not defined. Cannot remove it.")
            return

        logger.info("Deleting %s", self._current_filename)
        os.remove(self._current_filename)
        self.close()
        self.frame.get_current_player().next()


class PhotoFrame(QtWidgets.QMainWindow):
    def __init__(self, config):
        super(PhotoFrame, self).__init__()

        # instance variables to be read from config file
        self.slideshow_delay = None
        self.media_folder = None
        self.font_size = None
        self.compass = None
        self.flip_rotation = None
        self.rotation = None

        self.players = None
        self.current_player_index = 0

        # read values from the config file
        self.config = config
        self._setup_general_config()

        # setup an accelerometer if frame rotation enable
        if self.compass == "mpu6050":
            from utils.mpu6050 import Mpu6050Compass
            self.compass = Mpu6050Compass(self.flip_rotation)
        elif self.compass == "fixed":
            from utils.orientation import Compass
            self.compass = Compass(self.rotation, self.flip_rotation)
        else:
            self.compass = None

        self._setup_players()
        self._build_ui()
        self.popup = None

        # start timer
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self._timer_callback)
        timer.start(self.slideshow_delay)

        # go...
        self.showFullScreen()
        self.get_current_player().splash_screen()

    def _setup_general_config(self):
        """
        Read config values from config.yml file
        """
        frame_config = self.config.get_config_value("frame", self.config.root)
        if not frame_config:
            raise KeyError("Could not find section 'frame' in config file. Exiting")

        self.slideshow_delay = int(self.config.get_config_value("slideshow_delay", frame_config))
        logger.info("Slideshow delay = %d", self.slideshow_delay)

        self.media_folder = self.config.get_config_value("media_folder", frame_config)
        logger.info("Media folder = %s", self.media_folder)

        self.font_size = int(self.config.get_config_value("font", frame_config))
        logger.info("Font size = %d", self.font_size)

        self.compass = self.config.get_config_value("compass", frame_config)
        logger.info("Compass = %s", self.compass)

        self.rotation = self.config.get_config_value("rotation", frame_config)
        logger.info("Rotation = %d", self.rotation)

        self.flip_rotation = self.config.get_config_value("flip_rotation", frame_config)
        logger.info("Flip Rotation = %s", self.flip_rotation)

    def _setup_players(self):
        """
        Factory method to create the set of media players

        :return: a list of AbstractMediaPlayer instances
        """
        players_config = self.config.get_config_value("players", self.config.root)
        if not players_config:
            raise KeyError("Could not find section 'players' in config file. Exiting")

        self.players = []

        # iterate through each entry, creating a corresponding media player
        for item in players_config:
            if players_config[item]["type"] == "photo_player":
                player = PhotoPlayer(item, self.media_folder + "/" + players_config[item]["folder"], self.compass)
            if players_config[item]["type"] == "video_player":
                player = VideoPlayer(item, self.media_folder + "/" + players_config[item]["folder"], self.compass)

            logger.info("Creating player %s", player.get_name())
            self.players.append(player)
        self.current_player_index = 0

    def next_player(self):
        """
        Switch to the next media player. If at the end of the player list, jump to the start
        """
        logger.debug("current_player_index = %d", self.current_player_index)
        logger.debug("length player_list = %d", len(self.players))
        if self.current_player_index >= len(self.players) - 1:
            logger.debug("Starting at beginning of media")
            new_index = 0
        else:
            new_index = self.current_player_index + 1

        self._set_player_by_index(new_index)
        return self.get_current_player()

    def prev_player(self):
        """
        Switch to the previous media player. If at the end of the player list, jump to the start
        """
        logger.debug("current_player_index = %d", self.current_player_index)
        logger.debug("length player_list = %d", len(self.players))
        if self.current_player_index <= 0:
            logger.debug("Starting at end of players")
            new_index = len(self.players) - 1
        else:
            new_index = self.current_player_index - 1

        self._set_player_by_index(new_index)
        return self.get_current_player()

    def get_current_player(self):
        """
        Get a reference to the current media player

        :return: the current media player
        """
        return self.players[self.current_player_index]

    def _timer_callback(self):
        self.get_current_player().next()

    def _build_ui(self):
        # setup UI - use a QStackedWidget to avoid widgets being destroyed
        self.stack = QtWidgets.QStackedWidget(self)
        for p in self.players:
            player_widget = p.get_main_widget()

            # If the media player returns a widget, add it. Else create a dummy 'not implemented' widget
            if player_widget:
                player_widget.setParent(self)
                self.stack.addWidget(player_widget)
            else:
                not_implemented = QtWidgets.QLabel("Media Player %s: Not yet implemented" % p.get_name(), self)
                not_implemented.setAlignment(QtCore.Qt.AlignCenter)
                self.stack.addWidget(not_implemented)
        self.setCentralWidget(self.stack)

    def _set_player_by_index(self, index):
        new_player = self.players[index]
        logger.debug("Changing to player index %d (%s)", index, new_player.get_name())
        self.stack.setCurrentIndex(index)
        self.current_player_index = index
        # new_player.show_current_media()

    def mousePressEvent(self, mouse):
        """
        Handle mouse clicks

        :param mouse: the mouse event
        """

        # close the popup (if open)
        if self.popup and self.popup.isVisible():
            self.popup.hide()

        # get the width/height of the screen, and the mouse click lco-ords
        width, height = self.size().width(), self.size().height()
        x, y = mouse.pos().x(), mouse.pos().y()

        # flip click areas if frame is rotated
        if self.compass and self.compass.is_portrait_frame():
            x, y = y, x

        # click on left/right borders = prev/next image
        if x >= width * 0.8:
            self.get_current_player().next()
        elif x <= width * 0.2:
            self.get_current_player().prev()

        # click on the top/bottom borders = prev/next media player
        elif y >= height * 0.8:
            self.next_player().next()
        elif y <= height * 0.2:
            self.prev_player().next()

        # click in the centre = raise popup showing photo information
        else:
            self._popup()

    def keyPressEvent(self, key):
        """
        Handle key-presses

        :param key: the pressed key
        """
        key_press = key.key()
        if key_press == QtCore.Qt.Key_Escape:  # escape = exit
            self.close()
            sys.exit(0)

        if key_press == QtCore.Qt.Key_Left:  # left = prev image
            self.get_current_player().prev()

        if key_press == QtCore.Qt.Key_Right:  # right = next image
            self.get_current_player().next()

        if key_press == QtCore.Qt.Key_Up:  # up = next media player
            self.prev_player()

        if key_press in [Qt.Key_Enter, Qt.Key_Return]:  # space = reload image list
            self._popup()

        if key_press == QtCore.Qt.Key_Down:  # down = next player
            self.next_player()

    def refresh_current_playlist(self):
        logger.info("Refreshing media list for %s", self.get_current_player().get_name())
        self.get_current_player().refresh_media_list()

    def _popup(self):
        logger.debug("Open popup")
        if not self.popup:
            self.popup = Popup(self, self.font_size)

        filename, exif = self.get_current_player().get_current_media_exif()  # filename and EXIF may be none
        self.popup.show_image_details(filename, exif)
