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
    player1 = window.get_current_player().get_name()

    # down
    qtbot.keyPress(window, QtCore.Qt.Key_Down)
    player2 = window.get_current_player().get_name()

    # up - return to original player
    qtbot.keyPress(window, QtCore.Qt.Key_Up)
    assert window.get_current_player().get_name() == player1


def test_cycle_players(qtbot):
    window = PhotoFrame(Config("tests/test_config.yml"))

    player1 = window.get_current_player().get_name()

    # down x3 - return back to the same player
    qtbot.keyPress(window, QtCore.Qt.Key_Down)
    qtbot.keyPress(window, QtCore.Qt.Key_Down)
    player3 = window.get_current_player().get_name()
    qtbot.keyPress(window, QtCore.Qt.Key_Down)
    assert window.get_current_player().get_name() == player1

    # up - cycle back to the end
    qtbot.keyPress(window, QtCore.Qt.Key_Up)
    assert window.get_current_player().get_name() == player3

# def test_show_photos(qtbot):
#    qtbot.wait(5000)
