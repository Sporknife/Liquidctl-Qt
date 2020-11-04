from window import MainWindow
from ui_widgets import right, main_widgets
from PyQt5.QtWidgets import QApplication
import sys

select = input("main, right, ...")
if select == "main":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
