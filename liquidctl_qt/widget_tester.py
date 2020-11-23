from window import MainWindow
from ui_widgets import control
from PyQt5.QtWidgets import QApplication
import sys

select = input("main, profile, fan: ")
if select == "main":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()

elif select == "profile":
    app = QApplication(sys.argv)
    window = control.ProfileEditorDialog("test fan")
    window.open()
    app.exec_()

elif select == "fan":
    app = QApplication(sys.argv)
    window = control.FanWidget(
        "test name",
        [
            ["mode", "-"],
            ["current", "- A"],
            ["speed", "- rpm"],
            ["voltage", "- V"],
        ],
        lambda x: print("clicked"),
        None,
    )
    window.show()
    app.exec_()
