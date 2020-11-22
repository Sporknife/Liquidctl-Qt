from PyQt5 import QtWidgets, QtCore
from ui_widgets import main_widgets


class DeviceSelector(main_widgets.ComboBox):
    def __init__(
        self,
        to_connect,
        items: tuple = [],
    ):
        super().__init__(
            name="device_selector",
            items=items,
            to_connect=to_connect,
        )


class DeviceInfo(QtWidgets.QGridLayout):
    def __init__(self, info_list: list, update_singnal: QtCore.pyqtSignal):
        super().__init__()
        self._add_labels(info_list)
        update_singnal.connect(self.update_info_labels)
        self.addItem(
            main_widgets.Spacer(
                h_pol=QtWidgets.QSizePolicy.Fixed,
                v_pol=QtWidgets.QSizePolicy.Preferred,
            ),
            0,
            1,
        )

    def _add_labels(self, info_list: list):
        for i, info in enumerate(info_list):
            type_label = main_widgets.Label(text=self.clean_text(info[0]))
            self.addWidget(type_label, i, 0)
            self.addWidget(self.value_label(info[1]), i, 3)

    def clean_text(self, text):
        return text.replace("_", " ").capitalize() + ":"

    def value_label(self, info):
        if isinstance(info, bytes):
            info = info.decode()
        return main_widgets.Label(text=str(info))

    @QtCore.pyqtSlot(list)
    def update_info_labels(self, info_list):
        for i, info in enumerate(info_list[0]):
            text = info[1]
            if isinstance(text, bytes):
                text = text.decode()
            value_label = self.itemAtPosition(i, 3)
            if value_label:
                widget = value_label.widget()
                widget.setText(str(text))


class MainLeft(QtWidgets.QWidget):
    __slots__ = ("device_selector", "device_info", "info")

    def __init__(self, info_obj):
        super().__init__()
        self.info = info_obj
        self._set_device_selector()
        self._set_device_info()
        self.setLayout(self.layout())

    def _set_device_selector(self):
        self.device_selector = DeviceSelector(
            self.info.main_handler.on_device_change,
            items=[device.description for device in self.info.DEVICES_LIST]
        )

    def _set_device_info(self):
        self.device_info = DeviceInfo(
            info_list=self.info.curr_dev_info,
            update_singnal=self.info.signals.device_changed_signal,
        )

    def layout(self):
        vbox = main_widgets.VBox()
        vbox.addWidget(self.device_selector)
        vbox.addItem(self.device_info)
        vbox.addItem(
            main_widgets.Spacer(v_pol=QtWidgets.QSizePolicy.Expanding)
        )
        return vbox
