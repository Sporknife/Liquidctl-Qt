from PyQt5 import QtCore, QtWidgets
from ui_widgets import main_widgets, profile_editor


class FanWidget(main_widgets.HardwareWidget):
    """Fan widget which Displays basic info"""
    def __init__(
        self,
        fan_name: str,
        fan_info: list,
        to_connect,
        update_signal: QtCore.pyqtSignal,
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
    def __init__(self, name: str):
        super().__init__()
        self.setModal(True)
        self.setWindowTitle(name)
        layout = main_widgets.HBox()
        layout.addWidget(profile_editor.ProfileEditor(name, ""))
        self.setLayout(layout)


class LiquidWidget(QtWidgets.QWidget):
    def __init__(self, name: str, signals_obj):
        super().__init__()
        self.signals = signals_obj
        self.setObjectName(name)
