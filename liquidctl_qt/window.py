from PyQt5 import QtWidgets
from ui_widgets import left, right, main_widgets
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from liquidctl_api import liquidctl_api
from threading import Thread, Event


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Liquidctl")

    def _layout(self):
        pass

    def left(self):
        pass

    def right(self):
        pass
