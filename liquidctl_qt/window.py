from PyQt5 import QtWidgets, QtCore, QtGui
from ui_widgets import main_widgets, left, right, control
from liquidctl_api import liquidctl_api
from threading import Thread, Event


class Signals(QtCore.QObject):
    device_changed_signal = QtCore.pyqtSignal(list, name="device-changed")

    def __init__(self):
        super().__init__()


class Handler(QtCore.QObject):
    __slots__ = "info"

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


class DecisionDialog(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Decisions...")
        self.setModal(True)
        self.setLayout(self._layout())
        width, height = int(self.width()), int(self.height())

        self.setMaximumSize(width, height)

    def _layout(self):
        vbox = main_widgets.VBox()
        msg_label = main_widgets.Label(
            text="Would you like to exit the application\n(and loose your unsaved/unapplied settings) ?",
            aligment=QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter,
        )
        vbox.addWidget(msg_label)
        vbox.addWidget(self._buttons_box())
        return vbox

    def _buttons_box(self):
        buttons = (
            QtWidgets.QDialogButtonBox.No | QtWidgets.QDialogButtonBox.Yes
        )
        buttons_box = QtWidgets.QDialogButtonBox(buttons)
        buttons_box.accepted.connect(self.accept)
        buttons_box.rejected.connect(self.reject)
        return buttons_box

    def closeEvent(self, close_event):
        self.reject()


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
        hbox.addWidget(self.info.main_right)
        central_widget.setLayout(hbox)
        return central_widget

    def closeEvent(self, close_event):
        dialog = DecisionDialog(self)
        if dialog.exec_():
            self.info.dev_hw_inf_updater.stop()
            close_event.accept()
        else:
            close_event.ignore()


class Info:
    __slots__ = (
        "control_device_widgets",
        "curr_dev_index",
        "devices_dict",
        "devices_list",
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
        self.curr_dev_index = 0
        self.profile_setting_dialogs = {}  # dialog widgets
        self.control_device_widgets = [
            [] for device in self.devices_list
        ]  # fan, pump widgets

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

    def __init__(self, info, pause=2):
        self.info = info
        self.pause = pause
        self.widgets_created = []
        self.do_update = None

    def _init(self, curr_page):
        """
        creates and adds hw widgets for current device
        """
        self.widgets_created.append(self.info.curr_dev_index)

        _parsed_info = None
        while not _parsed_info:
            self.do_update.wait(1)
            _parsed_info = self.info_parser(
                self.info.curr_device_obj.get_status()
            )
        widgets_creation_data = []
        for widget_name, hw_info in _parsed_info.items():
            if "Fan" in widget_name:
                widgets_creation_data.append(["fan", widget_name, hw_info])
            self.info.control_device_widgets[
                self.info.curr_dev_index
            ].append(widget_name)
        curr_page.add_widgets_signal.emit(widgets_creation_data)

    def _start(self, loc_to_update):
        """
        updates hw info of currently selected device
        """
        curr_page = (
            self.info.main_right.stack_frame.stacked_widget.currentWidget()
        )
        if self.info.curr_dev_index not in self.widgets_created:
            self._init(curr_page)
        while not loc_to_update.is_set():
            parsed_info = self.info_parser(
                self.info.curr_device_obj.get_status()
            )
            for widget_name, hw_info in parsed_info.items():
                if (
                    widget_name
                    not in self.info.control_device_widgets[
                        self.info.curr_dev_index
                    ]
                ):
                    curr_page.add_widgets_signal.emit(
                        [["fan", widget_name, hw_info]]
                    )
                    self.info.control_device_widgets[
                        self.info.curr_dev_index
                    ].append(widget_name)
            curr_page.update_dev_hw_info.emit(parsed_info)
            loc_to_update.wait(self.pause)

    def start(self):
        do_update = Event()
        self.do_update = do_update
        Thread(target=self._start, args=(do_update,)).start()

    def stop(self):
        self.do_update.set()

    def info_parser(self, dev_status):
        hw_info = {}
        for i, line in enumerate(dev_status):
            line = list(line)
            header_line = InfoUpdater.checker(line)
            if header_line == "fan":
                mode = line[1]
                current = str(dev_status[i + 1][1])
                speed = str(dev_status[i + 2][1])
                voltage = str(round(dev_status[i + 3][1], 2))
                hw_info[line[0]] = [
                    ["Mode", mode, ""],
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
