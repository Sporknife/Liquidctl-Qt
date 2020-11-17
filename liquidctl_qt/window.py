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
        self.info.main_right.stack_frame.stacked_widget.setCurrentIndex(
            new_index
        )
        self.info.signals.device_changed_signal.emit(
            [self.info.curr_dev_info, new_index]
        )
        self.info.dev_hw_inf_updater.start()

    def multi_settings(self):
        print("multi settings")

    def multi_apply(self):
        print("multi apply")


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.info = Info(self)
        self._main_window_init()

    def _main_window_init(self):
        self.setWindowTitle("Liquidctl-Qt")
        self.show()
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
        self.DEVICES_DICT = self.liquidctl_api.devices_dict # pylint: disable=invalid-name
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
    __slots__ = ("info", "pause", "widgets_created", "do_update")

    def __init__(self, info, pause=3):
        self.info = info
        self.pause = pause
        self.do_update = None

    def _add_widget_dev_list(self, widget_name):
        """
        adds widget name to device widget list
        """
        self.info.control_device_widgets[self.info.curr_dev_index].append(
            widget_name
        )

    def _init(self, curr_page, loc_curr_dev_obj):
        """
        creates and adds hw widgets for current device
        loc_curr_dev_obj = local curr device object
        """
        parsed_info = None
        while not parsed_info:
            self.do_update.wait(1)
            parsed_info = self.info_parser(
                loc_curr_dev_obj.get_status()
            )
        widgets_creation_data = []
        for widget_name, hw_info in parsed_info.items():
            if "Fan" in widget_name:
                widgets_creation_data.append(["fan", widget_name, hw_info])
                self._add_widget_dev_list(widget_name)
        curr_page.add_widgets_signal.emit(widgets_creation_data)

    def _start(self, loc_to_update, curr_page):
        """
        updates hw info of currently selected device
        loc_to_update = "local to update"
        curr_page = "page that start() was started on"
        """
        curr_dev_obj = self.info.curr_device_obj

        if not self.info.control_device_widgets[self.info.curr_dev_index]:
            self._init(curr_page, curr_dev_obj)
        while not loc_to_update.is_set():
            parsed_info = self.info_parser(
               curr_dev_obj.get_status()
            )
            for widget_name, hw_info in parsed_info.items():
                if (
                    widget_name
                    not in self.info.control_device_widgets[
                        self.info.curr_dev_index
                    ]
                ):
                    curr_page.insert_widget_signal.emit(
                        [["fan", widget_name, hw_info]]
                    )
                    self._add_widget_dev_list(widget_name)
            curr_page.update_dev_hw_info.emit(parsed_info)
            loc_to_update.wait(self.pause)

    def start(self):
        do_update = Event()
        curr_page = (
            self.info.main_right.stack_frame.stacked_widget.currentWidget()
        )
        self.do_update = do_update
        Thread(target=self._start, args=(do_update, curr_page)).start()

    def stop(self):
        self.do_update.set()

    def info_parser(self, dev_status):
        hw_info = {}
        for i, line in enumerate(dev_status):
            line = list(line)
            header_line = InfoUpdater.checker(line)
            if header_line == "fan":
                mode = line[1]
                current = dev_status[i+1][1]
                speed = dev_status[i + 2][1]
                voltage = dev_status[i + 3][1]
                power = current * voltage
                hw_info[line[0]] = [
                    ["Mode", mode, ""],
                    ["Power consumption", power, "W"],
                    ["Current", current, "A"],
                    ["Speed", speed, "RPM"],
                    ["Voltage", voltage, "V"],
                ]
        return hw_info

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
