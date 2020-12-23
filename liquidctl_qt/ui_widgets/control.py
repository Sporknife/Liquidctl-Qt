from PyQt5 import QtCore, QtWidgets
from ui_widgets import main_widgets, profile_editor


class FanWidget(main_widgets.HardwareWidget):
    """Fan widget which Displays basic info"""

    def __init__(
        self,
        fan_name: str,
        fan_info: list,
        to_connect,
        update_signal,
    ):
        super().__init__(
            hw_name=fan_name,
            hw_info=fan_info,
            settings_btn_to_cnct=to_connect,
        )
        self.name = fan_name
        update_signal.connect(self.on_update)

    @QtCore.pyqtSlot(dict)
    def on_update(self, dev_hw_info):
        hw_info = dev_hw_info.get(self.name)
        if hw_info:
            self.update_info(hw_info)


class ProfileEditorDialog(QtWidgets.QDialog):
    def __init__(self, name: str, curr_dev_dict: dict, main_window):
        super().__init__(parent=main_window)
        self.setModal(True)
        self.setWindowTitle(name)
        self.setLayout(self._layout(name, curr_dev_dict))
        self._connect()

    def _layout(self, name, curr_dev_dict):
        layout = QtWidgets.QVBoxLayout()
        self._profile_editor = profile_editor.ProfileEditor(
            self, name, curr_dev_dict)
        layout.addWidget(self._profile_editor)
        return layout

    def _connect(self):
        self._profile_editor.hide_dialog_signal.connect(self.hide)
        self._profile_editor.show_dialog_signal.connect(self.show)
