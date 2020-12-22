from PySide6 import QtCore, QtWidgets
from ui_widgets import (
    main_widgets,
    left,
    right
)
from liquidctl_api import liquidctl_api
import threading


class Handler(QtCore.QObject):
    # __slots__ = ("window",)

    # when user selects another device
    device_changed_signal = QtCore.Signal(dict)

    def __init__(self, window):
        super().__init__()
        self.window = window

    @QtCore.Slot(int)
    def on_device_changed(self, new_dev_index):
        self.window.info.dev_info_updater.stop()
        self.window.info.current_dev_index = new_dev_index
        self.device_changed_signal.emit(
            {
                "device_info": self.window.info.current_device_info,
                "device_index": new_dev_index
            }
        )
        self.window.info.dev_info_updater.start()


class MainWindow(QtWidgets.QMainWindow):
    # __slots__ = ("handler", "info")

    def __init__(self):
        super().__init__()
        self._init()

    def _init(self):
        self.handler = Handler(self)
        self.info = Info(self)
        self.setCentralWidget(self._layout())

    def _layout(self):
        central_widget = QtWidgets.QWidget()
        hbox = main_widgets.HBox()
        hbox.addWidget(self.info.main_left)
        hbox.addWidget(self.info.main_right)
        central_widget.setLayout(hbox)
        return central_widget

    def closeEvent(self, close_event):  # pylint: disable=invalid-name
        DIALOG_MSG = (  # pylint: disable=invalid-name
            "Would you like to exit the application\n" +
            "(and loose your unsaved/unapplied settings) ?"
        )
        dialog = main_widgets.DecisionDialog(self, DIALOG_MSG)
        self.hide()
        if dialog.exec_():
            self.info.dev_info_updater.stop()
            close_event.accept()
            self.close()
        else:
            close_event.ignore()
            self.show()


class Info:
    def __init__(self, window):
        self.window = window
        self._init()

    def _init(self):
        self._liquidctl_api()
        self._variables()
        self._main()
        self._left()
        self._right()
        # i have to do this (left.py, line: 44)
        self.main_left.set_layout()

    def _liquidctl_api(self):
        self.liquidctl_api = liquidctl_api.LiquidctlApi()
        # pylint: disable=invalid-name
        self.DEVICES_LIST = self.liquidctl_api.devices_list

    def _variables(self):
        self.control_device_widgets = [
            [] for device in self.DEVICES_LIST
        ]
        self.current_dev_index = 0

    def _main(self):
        self.main_handler = self.window.handler
        self.dev_info_updater = HwInfoUpdater(self, pause=6)

    def _left(self):
        self.main_left = left.MainLeft(self)

    def _right(self):
        self.main_right = right.MainRight(self)
        self.dev_info_updater.start()

    @property
    def current_device_obj(self):
        return self.DEVICES_LIST[self.current_dev_index]

    @property
    def current_device_info(self):
        return [
            list(info)
            for info in self.current_device_obj.device.hidinfo.items()
        ][:4]

    @property
    def profile_device_info(self):
        """Info used in a profile"""
        return {
            "name": self.current_device_obj.description,
            "vendor_id": self.current_device_obj.vendor_id,
            "product_id": self.current_device_obj.product_id
        }


class HwInfoUpdater:
    # __slots__ = ("info", "main_handler", "pause", "do_update", "curr_active")
    """Updater, creates hw widgets"""

    def __init__(self, info, pause):
        self._variables(info, pause)

    def _variables(self, info, pause):
        self.info = info
        self.main_handler = info.main_handler
        self.pause = pause
        self.do_update = None
        self.curr_active = [False for _ in self.info.DEVICES_LIST]

    def _add_widgets(self, hw_name, dev_index):
        """
        adds widget name to device widget list
        """
        if isinstance(hw_name, str):
            self.info.control_device_widgets[dev_index].append(hw_name)

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
                curr_page.insert_widget_signal.emit(hw_name, hw_info)
                self._add_widgets(hw_name, dev_index)

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
        self._add_widgets(tuple(parsed_info.keys()), dev_index)
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
        dev_obj = self.info.current_device_obj
        dev_index = self.info.current_dev_index

        if (
            not self.info.control_device_widgets[dev_index] and
            not self.curr_active[dev_index]
        ):
            self._init(curr_page, dev_obj, dev_index)
        while not loc_to_update.is_set():
            loc_to_update.wait(self.pause / 3)
            if not self.curr_active[dev_index]:
                parsed_info = self.info.liquidctl_api.to_dict(
                    dev_obj.get_status()
                )

                self._add_unadded_widgets(parsed_info, curr_page, dev_index)
                curr_page.update_dev_hw_signal.emit(parsed_info)
            loc_to_update.wait(self.pause / 3)
            loc_to_update.wait(self.pause / 3)

    def start(self):
        do_update = threading.Event()
        self.do_update = do_update
        threading.Thread(target=self._start, args=(do_update,)).start()

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
