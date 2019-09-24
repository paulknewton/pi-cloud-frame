import io

import pytest
from PIL import Image
from PIL import ImageChops
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QBuffer
from PyQt5.QtGui import QImage

from gui.config import Config
from gui.photo_app import PhotoFrame


@pytest.fixture
def window():
    window = PhotoFrame(Config("tests/test_config.yml"))
    return window


def pmap_to_pil_img(pmap):
    buffer = QBuffer()
    buffer.open(QBuffer.ReadWrite)

    img = QImage(pmap)
    img.save(buffer, "PNG")
    return Image.open(io.BytesIO(buffer.data()))


def test_player_splashscreen(qtbot, window):
    main_widget = window.get_current_player().get_main_widget()
    current_pmap = main_widget.pixmap()
    expected_pmap = QtGui.QPixmap.fromImage(QtGui.QImage("logo.png")).scaled(main_widget.size() / 2,
                                                                             QtCore.Qt.KeepAspectRatio,
                                                                             QtCore.Qt.SmoothTransformation)

    assert current_pmap.size() == expected_pmap.size()
    assert ImageChops.difference(pmap_to_pil_img(current_pmap), pmap_to_pil_img(expected_pmap)).getbbox() is None


def test_player_slideshow(qtbot, window):
    # wait for splashscreen to disappear
    qtbot.wait(4000)

    player = window.get_current_player()

    for photo in ["tests/test_media/photos/1.png", "tests/test_media/photos/2.png"]:
        current_pmap = player.get_main_widget().pixmap()
        expected_pmap = QtGui.QPixmap.fromImage(QtGui.QImage(photo)).scaled(
            player.get_main_widget().size(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation)

        player.paint_logo(expected_pmap)

        assert current_pmap.size() == expected_pmap.size()
        assert ImageChops.difference(pmap_to_pil_img(current_pmap), pmap_to_pil_img(expected_pmap)).getbbox() is None

        qtbot.wait(3000)

def test_exif():
    pass
