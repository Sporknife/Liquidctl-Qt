from PyQt5 import QtWidgets, QtCore
from ui_widgets import (
    main_widgets,
    left,
    right,
)  # pylint: disable=unused-import
from liquidctl_api import liquidctl_api
from threading import Thread, Event


class Signals(QtCore.QObject):
    """This class contains signal/s"""

    device_changed_signal = QtCore.pyqtSignal(list, name="device-changed")


class Handler(QtCore.QObject):
    """Where main events are handled"""

    __slots__ = ("info",)

    def __init__(self, window_obj, info_obj):
        super().__init__()
        self.window = window_obj
        self.info = info_obj

    def on_device_change(self, new_index):
        self.info.dev_hw_inf_updater.stop()
        self.info.curr_dev_index = new_index
        self.info.signals.device_changed_signal.emit(
            [self.info.curr_dev_info, new_index]
        )
        self.info.main_right.stack_frame.stacked_widget.setCurrentIndex(
            new_index
        )
        self.info.dev_hw_inf_updater.start()

    def multi_settings(self):
        print("multi settings")

    def multi_apply(self):
        print("multi apply")


class MainWindow(QtWidgets.QMainWindow):
    __slots__ = ("info",)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.info = Info(self)
        self._main_window_init()

    def _main_window_init(self):
        self.setWindowTitle("Liquidctl-Qt")
        self.setCentralWidget(self._layout())

    def _layout(self):
        central_widget = QtWidgets.QWidget()
        hbox = main_widgets.HBox()
        hbox.addWidget(self.info.main_left)
        hbox.addWidget(self.info.main_right)
        central_widget.setLayout(hbox)
        return central_widget

    def closeEvent(self, close_event):  # pylint: disable=invalid-name
        dialog = main_widgets.DecisionDialog(self)
        if dialog.exec_():
            self.info.dev_hw_inf_updater.stop()
            close_event.accept()
        else:
            close_event.ignore()


class Info:
    __slots__ = (
        "control_device_widgets",
        "curr_dev_index",
        "DEVICES_DICT",
        "DEVICES_LIST",
        "liquidctl_api",
        "main_handler",
        "main_left",
        "main_right",
        "profile_setting_dialogs",
        "signals",
        "window",
        "dev_hw_inf_updater",
    )

    def __init__(self, window_obj):
        self.window = window_obj
        self._init()

    def _init(self):
        self._liquidctl_api()
        self._variables()
        self._main()
        self._left()
        self._right()

    def _liquidctl_api(self):
        self.liquidctl_api = liquidctl_api.LiquidctlApi()
        self.DEVICES_DICT = self.liquidctl_api.devices_dict  # pylint: disable=invalid-name
        self.DEVICES_LIST = self.liquidctl_api.devices_list  # pylint: disable=invalid-name

    @property
    def curr_device_obj(self):
        return self.DEVICES_LIST[self.curr_dev_index]

    @property
    def curr_dev_info(self):
        return [
            list(info)
            for info in self.curr_device_obj.device.hidinfo.items()
        ][:4]

    def _variables(self):
        self.curr_dev_index = 0
        self.profile_setting_dialogs = {}  # dialog widgets
        self.control_device_widgets = [
            [] for device in self.DEVICES_LIST
        ]

    def _main(self):
        self.dev_hw_inf_updater = InfoUpdater(self)
        self.main_handler = Handler(self.window, self)
        self.signals = Signals()

    def _left(self):
        self.main_left = left.MainLeft(self)

    def _right(self):
        self.main_right = right.MainRight(self)
        self.dev_hw_inf_updater.start()


class InfoUpdater:
    __slots__ = ("info", "pause", "widgets_created",
                 "do_update", "curr_active")

    def __init__(self, info, pause=4):
        self.info = info
        self.pause = pause
        self.do_update = None
        self.curr_active = [False for _ in self.info.DEVICES_LIST]

    def _add_widgets_dev_list(self, hw_name, dev_index):
        """
        adds widget name to device widget list
        """
        if isinstance(hw_name, str):
            self.info.control_device_widgets[
                dev_index
            ].append(hw_name)

        elif isinstance(hw_name, tuple):
            for name in hw_name:
                self.info.control_device_widgets[
                    dev_index
                ].append(name)

    def _add_unadded_widgets(self, parsed_info, curr_page, dev_index):
        """Checks for unadded hardware widgets"""
        for hw_name, hw_info in parsed_info.items():
            if (
                hw_name
                not in self.info.control_device_widgets[
                    dev_index]
            ):
                curr_page.insert_widget_signal.emit([hw_name, hw_info])
                self._add_widgets_dev_list(hw_name, dev_index)

    def _init(self, curr_page, dev_obj, dev_index):
        """
        creates and adds hw widgets for current device
        dev_obj = local current device object
        """
        parsed_info = None
        self.curr_active[dev_index] = True
        while not parsed_info:
            self.do_update.wait(1)
            parsed_info = self.info.liquidctl_api.to_dict(
                dev_obj.get_status()
            )
        curr_page.add_widgets_signal.emit(parsed_info)
        self._add_widgets_dev_list(tuple(parsed_info.keys()), dev_index)
        self.curr_active[dev_index] = False

    def _start(self, loc_to_update):
        """
        updates hw info of currently selected device
        loc_to_update = "local to update"
        curr_page = "page that start() was started on"
        """
        curr_page = (
            self.info.main_right.stack_frame.stacked_widget.currentWidget()
        )
        dev_obj = self.info.curr_device_obj
        dev_index = self.info.curr_dev_index

        if (
            not self.info.control_device_widgets[dev_index] and
            not self.curr_active[dev_index]
        ):
            self._init(curr_page, dev_obj, dev_index)
        while not loc_to_update.is_set():
            if not self.curr_active[dev_index]:
                parsed_info = self.info.liquidctl_api.to_dict(
                    dev_obj.get_status()
                )
                self._add_unadded_widgets(parsed_info, curr_page, dev_index)
                curr_page.update_dev_hw_info.emit(parsed_info)
            loc_to_update.wait(self.pause)

    def start(self):
        do_update = Event()
        self.do_update = do_update
        Thread(target=self._start, args=(do_update,)).start()

    def stop(self):
        self.do_update.set()

    @staticmethod
    def checker(line: list):
        if (
            (line[0].count(" ") == 1)
            and (not isinstance(line[1], int))
            and ("—" not in str(line[1]))
        ):
            if "Fan" in line[0]:
                return "fan"
        return False
