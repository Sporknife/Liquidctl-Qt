from PyQt5 import QtWidgets, QtCore
from ui_widgets import main_widgets, control


class Stack(QtWidgets.QFrame):
    """Frame that contains QStackedWidget"""

    def __init__(self, info):
        super().__init__()
        self.info = info
        self._init()

    def _init(self):
        self._style()
        self.setLayout(self._layout())
        self.info.main_handler.device_changed_signal.connect(
            self.set_page
        )

    def _style(self):
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setLineWidth(1)

    def _layout(self):
        box = main_widgets.VBox()
        self.stacked_widget = QtWidgets.QStackedWidget()
        self._add_pages()
        box.addWidget(self.stacked_widget)
        return box

    def _add_pages(self):
        for _ in self.info.DEVICES_LIST:
            self.stacked_widget.addWidget(StackPage(self.info))

    @QtCore.pyqtSlot(dict)
    def set_page(self, info_dict):
        self.stacked_widget.setCurrentIndex(
            info_dict.get("device_index")
        )


class StackPage(QtWidgets.QScrollArea):
    update_dev_hw_signal = QtCore.pyqtSignal(dict)
    add_widgets_signal = QtCore.pyqtSignal(dict)
    insert_widget_signal = QtCore.pyqtSignal(str, dict)

    def __init__(self, info):
        super().__init__()
        self.info = info
        self._init_()

    def _init_(self):
        self._connect_signals()
        self._style()
        self._layout()

    def _connect_signals(self):
        self.add_widgets_signal.connect(self.add_widgets)
        self.insert_widget_signal.connect(self.insert_widget)

    def _style(self):
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)

    def _layout(self):
        widget = QtWidgets.QWidget()
        self._vbox = main_widgets.VBox()
        widget.setLayout(self._vbox)
        self.setWidget(widget)

    @QtCore.pyqtSlot(dict)
    def add_widgets(self, dev_hw_info):
        for hw_name in dev_hw_info.keys():
            if "Fan" in hw_name:
                self._vbox.addWidget(
                    self.fan_widget(
                        fan_name=hw_name,
                        fan_info=dev_hw_info.get(hw_name),
                    )
                )
        self._vbox.addSpacerItem(
            main_widgets.Spacer(v_pol=QtWidgets.QSizePolicy.Expanding)
        )

    @QtCore.pyqtSlot(str, dict)
    def insert_widget(self, hw_name, hw_info):
        if "Fan" in hw_name:
            self._vbox.insertWidget(
                0,
                self.fan_widget(
                    hw_name,
                    hw_info
                )
            )

    def fan_widget(self, fan_name, fan_info):
        device_dict = {
            "device_obj": self.info.current_device_obj,
            "device_info": self.info.profile_device_info
        }

        def dialog(): return control.ProfileEditorDialog(
            fan_name, device_dict, self.info.window
        ).exec_()
        return control.FanWidget(
            fan_name=fan_name,
            fan_info=fan_info,
            to_connect=dialog,
            update_signal=self.update_dev_hw_signal

        )


class MainRight(QtWidgets.QWidget):
    """Main class & widget for right side"""
    __slots__ = ("info", "stack_frame")

    def __init__(self, info_obj):
        super().__init__()
        self.info = info_obj
        self.setLayout(self._layout())

    def _layout(self):
        vbox = main_widgets.VBox()
        self.stack_frame = Stack(
            self.info,
        )

        self.stacked_widget = self.stack_frame.stacked_widget
        vbox.addWidget(self.stack_frame)
        return vbox
