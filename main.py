import logging
import sys

from PySide6 import QtWidgets
from components.windown import Windown

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

if __name__ == '__main__':

    app = QtWidgets.QApplication([])

    windown = Windown()
    windown.resize(800, 400)
    windown.show()

    sys.exit(app.exec())

