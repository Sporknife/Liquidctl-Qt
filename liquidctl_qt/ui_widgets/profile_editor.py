from PyQt5 import QtWidgets, QtCore
from ui_widgets import main_widgets


class ProfileEditorDialog(QtWidgets.QDialog):
    def __init__(self, name: str):
        super().__init__()
        self.setModal(True)
        self.setWindowTitle(name)
        layout = main_widgets.HBox()
        layout.addWidget(ProfileEditor(name, ""))
        self.setLayout(layout)


class LiquidWidget(QtWidgets.QWidget):
    def __init__(self, name: str, signals_obj):
        super().__init__()
        self.signals = signals_obj


class ProfileEditor(QtWidgets.QWidget):
    def __init__(self, name: str, signals_obj):
        super().__init__()
        self.signals = signals_obj

    def _layout(self):
        hbox = main_widgets.HBox()

    def _left(self):
        vbox = main_widgets.VBox()


class ProfileModeChooser(main_widgets.HBox):
    """
    Select the profile and its mode
    """

    def __init__(self, prof_editor_obj):
        super().__init__()
        self.prof_editor = prof_editor_obj
        self._layout()

    def _layout(self):
        self.addWidget(self._left())
        self.addItem(
            main_widgets.Spacer(
                QtWidgets.QSizePolicy.Minimum,
                QtWidgets.QSizePolicy.Fixed,
                5,
            )
        )
        self.addWidget(self._right())

    def _left(self):
        return main_widgets.ComboBox(
            name="profile-chooser",
            items=[],
            to_connect=self.on_profile_change,
            pass_index=True,
        )

    def _right(self):
        pass

    @QtCore.pyqtSlot(int)
    def on_profile_change(self, int):
        print("profile changed !")
