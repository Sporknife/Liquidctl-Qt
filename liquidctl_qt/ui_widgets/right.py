from PyQt5 import QtWidgets, QtCore
from ui_widgets import main_widgets, control


class Stack(QtWidgets.QFrame):
    def __init__(self, info_obj):
        super().__init__()
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )
        self.info = info_obj
        self._style()
        self._layout()
        self.info.signals.device_changed_signal.connect(self.set_page)

    def _style(self):
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setLineWidth(1)

    def _layout(self):
        box = QtWidgets.QVBoxLayout()
        self.stacked_widget = main_widgets.StackedWidget()
        [
            self.stacked_widget.addWidget(StackPage())
            for device in self.info.devices_list
        ]
        box.addWidget(self.stacked_widget)
        self.setLayout(box)

    def add_pages(self):
        for dev_obj in self.info.devices_list:
            self.stacked_widget.addWidget(StackPage())

    @QtCore.pyqtSlot(list)
    def set_page(self, info_list):
        self.stacked_widget.setCurrentIndex(info_list[1])


class StackPage(QtWidgets.QScrollArea):
    update_dev_hw_info = QtCore.pyqtSignal(dict, name="info-updater")
    add_widgets_signal = QtCore.pyqtSignal(list, name="witem-adder")

    def __init__(self):
        super().__init__()
        self._init()
        self.add_widgets_signal.connect(self.add_widgets)

    def _init(self):
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setWidgetResizable(True)
        self.setWidget(self._layout())

    def _layout(self):
        widget = QtWidgets.QWidget()
        self.vbox = main_widgets.VBox()
        widget.setLayout(self.vbox)
        return widget

    @QtCore.pyqtSlot(list)
    def add_widgets(self, widgets_info):
        # widgets_info = [[widget_mode, hw_info], ["fan", hw_info]]
        for widget_info in widgets_info:
            if widget_info[0] == "fan":
                self.vbox.addWidget(
                    control.FanWidget(
                        widget_info[1],
                        widget_info[2],
                        lambda x="": print("profile button clicked !"),
                        self.update_dev_hw_info,
                    )
                )


class MainRight(QtWidgets.QWidget):
    def __init__(self, info_obj):
        super().__init__()
        self.info = info_obj
        self.setLayout(self._layout())

    def _layout(self):
        vbox = main_widgets.VBox()
        self.stack_frame = Stack(
            self.info,
        )
        vbox.addWidget(self.stack_frame)
        return vbox
