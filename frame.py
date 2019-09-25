#! /usr/bin/env python3

import logging.config
import sys

import yaml
from PyQt5 import QtWidgets

from gui.photo_app import PhotoFrame
from utils.config import Config

FRAME_CONFIG = "config.yml"
LOG_CONFIG = "logging.yml"
with open(LOG_CONFIG, 'rt') as f:
    logging.config.dictConfig(yaml.safe_load(f.read()))

logger = logging.getLogger(__name__)


def main():
    """
    Create the photo frame application
    """
    sys._excepthook = sys.excepthook
    sys.excepthook = exception_hook

    app = QtWidgets.QApplication(sys.argv)

    config = Config(FRAME_CONFIG)

    try:
        window = PhotoFrame(config)
        window.raise_()
    except KeyError as exception:
        print("Error setting up frame: ", exception)
        sys.exit(1)

    app.exec_()


def exception_hook(exctype, value, traceback):
    """
    Handle exceptions in the Qt application. Prevents exceptions being consumed silently by Qt.
    :param exctype: the type of exception
    :param value: the exception contents
    :param traceback: the stack trace
    """
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


if __name__ == '__main__':
    main()
