from PyQt5 import QtWidgets, QtCore
from ui_widgets import main_widgets


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
        self.add_pages()
        box.addWidget(self.stacked_widget)
        self.setLayout(box)

    def add_pages(self):
        for dev_obj in self.info.devices_list:
            self.stacked_widget.addWidget(StackPage())

    @QtCore.pyqtSlot(list)
    def set_page(self, info_list):
        self.stacked_widget.setCurrentIndex(info_list[1])


class StackPage(QtWidgets.QScrollArea):
    def __init__(self):
        super().__init__()
        self._init()

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

    def add_witem(self, witems):
        witems = list(witems)
        for witem in witems:
            self.vbox.addWitem(witem)


class MainRight(QtWidgets.QWidget):
    def __init__(self, info_obj):
        super().__init__()
        self.info = info_obj
        self.setLayout(self._layout())
        info_obj.dev_hw_inf_updater.start()

    def _layout(self):
        vbox = main_widgets.VBox()
        vbox.addWidget(
            Stack(
                self.info,
            )
        )
        return vbox
