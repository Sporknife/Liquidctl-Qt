from PyQt5 import QtWidgets, QtCore
from ui_widgets import main_widgets, control


class Stack(QtWidgets.QFrame):
    """Widget that contains StackedWidget"""
    __slots__ = ("info",)

    def __init__(self, info_obj):
        super().__init__()
        self.info = info_obj
        self._init()

    def _init(self):
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )
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
        self._add_pages()
        box.addWidget(self.stacked_widget)
        self.setLayout(box)

    def _add_pages(self):
        for _ in self.info.DEVICES_LIST:
            self.stacked_widget.addWidget(StackPage())

    @QtCore.pyqtSlot(dict)
    def set_page(self, info_dict):
        self.stacked_widget.setCurrentIndex(
            info_dict.get("device_index")
        )


class StackPage(QtWidgets.QScrollArea):
    """ScrollAre that allows to view multiple device hardware widgets"""
    __slots__ = ("vbox",)

    update_dev_hw_info = QtCore.pyqtSignal(dict, name="info-updater")
    add_widgets_signal = QtCore.pyqtSignal(dict, name="widgets-adder")
    insert_widget_signal = QtCore.pyqtSignal(list, name="widget-inserter")

    def __init__(self):
        super().__init__()
        self._init()
        self.add_widgets_signal.connect(self.add_widgets)
        self.insert_widget_signal.connect(self.insert_widget)

    def _init(self):
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setWidget(self._layout())

    def _layout(self):
        widget = QtWidgets.QWidget()
        self.vbox = main_widgets.VBox()
        widget.setLayout(self.vbox)
        return widget

    @QtCore.pyqtSlot(dict)
    def add_widgets(self, hw_info):
        for hw_name in hw_info.keys():
            if "Fan" in hw_name:
                self.vbox.addWidget(
                    control.FanWidget(
                        hw_name,
                        hw_info.get(hw_name),
                        lambda x="": print("profile button clicked !"),
                        self.update_dev_hw_info,
                    )
                )
        self.vbox.addItem(
            main_widgets.Spacer(v_pol=QtWidgets.QSizePolicy.Expanding)
        )

    @QtCore.pyqtSlot(list)
    def insert_widget(self, hw_data):
        hw_name = hw_data[0]
        hw_info = hw_data[1]
        if "Fan" in hw_name:
            self.vbox.insertWidget(
                0,
                control.FanWidget(
                    hw_name,
                    hw_info,
                    lambda x="": print("profile button clicked !"),
                    self.update_dev_hw_info,
                )
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
        vbox.addWidget(self.stack_frame)
        return vbox
