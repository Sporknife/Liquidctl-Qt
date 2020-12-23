#!/usr/bin/env python

from PyQt5 import QtWidgets
from window import MainWindow
import sys

print("""
If you need ANY help or if you would report an issue use:
- The github page:\t\t https://github.com/Sporknife/Liquidctl-Qt
- Liquidctl's GitHub page:\t https://github.com/liquidctl/liquidctl
- Discord server:\t\t https://discord.gg/D4tegR
""")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()
