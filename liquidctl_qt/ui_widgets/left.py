from PyQt5 import QtCore, QtWidgets
from ui_widgets import main_widgets
import utils


class DeviceSelector(main_widgets.ComboBox):
    """Allows selecting supported devices by Liquidctl"""

    def __init__(
        self,
        to_connect,
        items: tuple,
    ):
        super().__init__(
            items=items,
            to_connect=to_connect,
        )


class DeviceInfo(QtWidgets.QGridLayout):
    """Basic info about the currently selected device"""

    # __slots__ = ("info",)

    def __init__(self, info):
        super().__init__()
        self.info = info
        self._init()

    def _init(self):
        self._add_labels()
        self.addItem(
            main_widgets.Spacer(
                h_pol=QtWidgets.QSizePolicy.Fixed,
                height=0
            ),
            0,
            1,
        )
        self.info.main_handler.device_changed_signal.connect(
            self.update_info_labels)

    def _add_labels(self):
        for i, info in enumerate(self.info.current_device_info):
            type_label = main_widgets.Label(text=self._clean_text(info[0]))
            self.addWidget(type_label, i, 0)
            self.addWidget(self._value_label(info[1]), i, 3)

    def _clean_text(self, text) -> str:
        """removes certains things from string"""
        return text.replace("_", " ").capitalize() + ":"

    def _value_label(self, info):
        """creates label widget used for the value"""
        if isinstance(info, bytes):
            info = info.decode()
        return main_widgets.Label(text=str(info))

    @QtCore.pyqtSlot(dict)
    def update_info_labels(self, info_dict):
        """updates labels when selected device is changed"""
        for i, labels_text in enumerate(info_dict.get("device_info")):
            value_text = labels_text[1]
            if isinstance(value_text, bytes):
                value_text = value_text.decode()
            value_label = self.itemAtPosition(i, 3)
            if value_label:
                widget = value_label.widget()
                widget.setText(str(value_text))


class MainLeft(QtWidgets.QWidget):
    # __slots__ = ("info",)

    def __init__(self, info):
        super().__init__()
        self.info = info

    def set_layout(self):
        vbox = QtWidgets.QVBoxLayout()
        witem_adder = utils.WidgetAdder(self, vbox)
        witem_adder.widget_adder(
            "device_selector",
            DeviceSelector(
                self.info.main_handler.on_device_changed,
                items=[device.description for device in self.info.DEVICES_LIST]
            )
        )
        vbox.addSpacerItem(
            main_widgets.Spacer(
                v_pol=QtWidgets.QSizePolicy.Fixed,
                width=0,
                height=5
            )
        )
        vbox.addItem(DeviceInfo(self.info))
        vbox.addSpacerItem(
            main_widgets.Spacer(v_pol=QtWidgets.QSizePolicy.MinimumExpanding)
        )
        self.setLayout(vbox)
