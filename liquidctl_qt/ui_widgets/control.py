from PyQt5 import QtWidgets, QtCore
from ui_widgets import main_widgets


class FanWidget(main_widgets.HardwareWidget):
    def __init__(self, fan_name: str, hw_info, to_connect, update_signal):
        super().__init__(
            hw_name=fan_name,
            hw_info=hw_info,
            settings_btn_to_cnct=to_connect,
        )
        self.name = fan_name
        # self.update_signal.connect(self.on_update())

    @QtCore.pyqtSlot(dict)
    def on_update(self, dev_hw_info):
        hw_info = dev_hw_info.get(self.name)
        self.update_hw_info(hw_info)


class Signals(QtCore.QObject):
    mode_change_signal = QtCore.pyqtSignal(bool, name="mode-changed")
    profile_changed = QtCore.pyqtSignal(list, name="mode-changed")
    remove_profile_signal = QtCore.pyqtSignal(name="update-values")
    reset_signal = QtCore.pyqtSignal(name="reset-settings")
    new_step_signal = QtCore.pyqtSignal(name="new-step")
    remove_step_signal = QtCore.pyqtSignal(name="remove-step")

    def __init__(self):
        super().__init__()

    def connect(self, to_change_widgets, signal, enabled=True):
        if not isinstance(to_change_widgets, tuple):
            self._connect_signal(to_change_widgets, signal)
            to_change_widgets.setEnabled(False)
            return

        for widget in to_change_widgets:
            self._connect_signal(widget, signal)

    def _connect_signal(self, widget, signal):
        signal.connect(lambda mode: widget.setEnabled(mode))
        widget.setEnabled(False)

    def set_signals(self):
        self.__class__.mode_change_signal
