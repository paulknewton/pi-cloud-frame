from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSlot
import logging

logger = logging.getLogger(__name__)


class Popup(QDialog):
    def __init__(self):
        super().__init__()

        self.filename_label = None
        self.date_label = None
        self._build_UI()

    def show_image_details(self, filename, tags):
        #logger.debug("exif tags: %s", tags)

        self.filename_label.setText("Photo filename: %s" % filename)
        self.filename_label.adjustSize()
        self.date_label.setText("Date: %s" % tags["EXIF DateTimeOriginal"])
        self.date_label.adjustSize()

        self.show()

    def _build_UI(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignLeft)
        self.setLayout(layout)

        self.filename_label = QLabel(self)
        layout.addWidget(self.filename_label)

        self.date_label = QLabel(self)
        layout.addWidget(self.date_label)

        whatsapp_button = QPushButton("Send photo")
        whatsapp_button.clicked.connect(self.on_click)
        layout.addWidget(whatsapp_button)

    @pyqtSlot()
    def on_click(self):
        logger.info("PyQt5 button click. TODO")