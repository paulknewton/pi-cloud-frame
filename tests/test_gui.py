import pytest
from PyQt5 import QtCore

import gui.media_players
from gui.config import Config
from gui.photo_app import PhotoFrame


@pytest.fixture
def window():
    window = PhotoFrame(Config("tests/test_config.yml"))
    return window


def test_change_players(qtbot, window):
    """
    Test navigation between multiple media players
    :param qtbot: fixture to trigger window events
    :param window: PhotoFrame widget
    """
    assert type(window.get_current_player()) == gui.media_players.PhotoPlayer
    player1 = window.get_current_player().get_name()

    # down
    qtbot.keyPress(window, QtCore.Qt.Key_Down)
    player2 = window.get_current_player().get_name()

    # up - return to original player
    qtbot.keyPress(window, QtCore.Qt.Key_Up)
    assert window.get_current_player().get_name() == player1


def test_cycle_players(qtbot, window):
    """
    Test that navigation beyond the end of the last media pleyer will jump to the first player (and vice versa)
    :param qtbot: fixture to trigger window events
    :param window: PhotoFrame widget
    """
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


def test_show_popup(qtbot, window):
    """
    Test key click to open popup menu
    :param qtbot: fixture to trigger window events
    :param window: PhotoFrame widget
    """
    assert window.popup is None

    qtbot.keyPress(window, QtCore.Qt.Key_Return)
    assert window.popup.isVisible()


def test_player_folder(qtbot, window):
    """
    Test method to retrieve playlist folder
    :param qtbot: fixture to trigger window events
    :param window: PhotoFrame widget
    """
    assert window.get_current_player().get_folder() == "tests/test_media/photos"


def test_player_playlist(qtbot, window):
    """
    Test loading of playlist from media folder
    :param qtbot: fixture to trigger window events
    :param window: PhotoFrame widget
    """
    media_folder = window.get_current_player().get_folder()
    expected_photos = [media_folder + "\\" + s for s in ["1.png", "2.png"]]

    assert expected_photos == window.get_current_player().get_playlist()


def test_player_empty_playlist(qtbot, window):
    """
    Test media player with no photos
    :param qtbot:
    :param window:
    :return:
    """
    # cycle to a media player with no photos
    qtbot.keyPress(window, QtCore.Qt.Key_Down)
    qtbot.keyPress(window, QtCore.Qt.Key_Down)
    player = window.get_current_player().get_name()

    assert window.get_current_player().get_playlist() == []
