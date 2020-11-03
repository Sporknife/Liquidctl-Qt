from PyQt5 import QtWidgets, QtCore
from ui_widgets import main_widgets, left
from liquidctl_api import liquidctl_api
from threading import Thread, Event


class Handler(QtCore.QObject):
    apply_all_signal = QtCore.pyqtSignal(name="apply_settings")
    # list = [stack_page_index, updatable]
    setDeviceSignal_left = QtCore.pyqtSignal(list, name="set-device-left")
    setDeviceSignal_right = QtCore.pyqtSignal(name="set-device-right")

    def __init__(self, window_obj, info_obj):
        super().__init__()
        self.window = window_obj
        self.info = info_obj

    def applyAll(self):
        print("apply allsettings")

    def on_device_change(self, new_index):
        self.info.curr_dev_index = new_index
        self.setDeviceSignal_left.emit(self.info.curr_dev_info)
        self.setDeviceSignal_right.emit()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.info = Info(self)
        self._main_window_init()

    def _main_window_init(self):
        self.setWindowTitle("Liquidctl-Qt")
        self.setCentralWidget(self._layout())
        self.show()

    def _layout(self):
        central_widget = QtWidgets.QWidget()
        hbox = main_widgets.HBox()
        hbox.addWidget(self.info.main_left)
        central_widget.setLayout(hbox)
        return central_widget


class Info:
    def __init__(self, window_obj):
        self._variables()
        self.window = window_obj
        self._init()

    def _init(self):
        self._variables()
        self._liquidctl_api()
        self._main()
        self._left()

    def _liquidctl_api(self):
        self.curr_dev_index = 0
        self.liquidctl_api = liquidctl_api.LiquidctlApi()
        self.devices_dict = self.liquidctl_api.devices_dict
        self.devices_list = self.liquidctl_api.devices_list

    @property
    def curr_device_obj(self):
        return self.devices_list[self.curr_dev_index]

    @property
    def curr_dev_info(self):
        return [
            list(info)
            for info in self.curr_device_obj.device.hidinfo.items()
        ][:4]

    def _variables(self):
        self.profile_setting_dialogs = {}  # dialog widgets
        self.control_device_widgets = {}  # fan, pump widgets

    def _main(self):
        self.main_handler = Handler(self.window, self)

    def _left(self):
        self.main_left = left.MainLeft(self)

    def _right(self):
        pass
