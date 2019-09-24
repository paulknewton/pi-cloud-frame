from PyQt5 import QtCore

import gui.media_players
from gui.config import Config
from gui.photo_app import PhotoFrame


# @pytest.fixture
# def setup():
#    window = PhotoFrame(Config("tests/test_config.yml"))
#


def test_change_players(qtbot):
    window = PhotoFrame(Config("tests/test_config.yml"))
    assert type(window.get_current_player()) == gui.media_players.PhotoPlayer
    assert window.get_current_player().get_name() == "Photo Player 1"

    # down
    qtbot.keyPress(window, QtCore.Qt.Key_Down)
    assert window.get_current_player().get_name() == "Photo Player 2"

    # up
    qtbot.keyPress(window, QtCore.Qt.Key_Up)
    assert window.get_current_player().get_name() == "Photo Player 1"


def test_cycle_players(qtbot):
    window = PhotoFrame(Config("tests/test_config.yml"))
    assert type(window.get_current_player()) == gui.media_players.PhotoPlayer
    assert window.get_current_player().get_name() == "Photo Player 1"

    # down x3
    qtbot.keyPress(window, QtCore.Qt.Key_Down)
    qtbot.keyPress(window, QtCore.Qt.Key_Down)
    qtbot.keyPress(window, QtCore.Qt.Key_Down)
    assert window.get_current_player().get_name() == "Photo Player 1"

    # up
    qtbot.keyPress(window, QtCore.Qt.Key_Up)
    assert window.get_current_player().get_name() == "Photo Player 3"

# def test_show_photos(qtbot):
#    qtbot.wait(5000)
