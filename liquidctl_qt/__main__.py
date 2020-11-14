#!/usr/bin/env python3

from PyQt5 import QtWidgets
from window import MainWindow
import sys

to_print = """
Hello to Liquidctl-Qt !
If you need ANY help or if you would report an issue use:
-The github page:\t https://github.com/Sporknife/Liquidctl-Qt
-Discord server:\t https://discord.gg/D4tegR
"""
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    app.exec_()
