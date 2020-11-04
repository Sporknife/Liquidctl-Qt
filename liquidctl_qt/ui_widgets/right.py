from PyQt5 import QtWidgets, QtCore
from ui_widgets import main_widgets


class Stack(QtWidgets.QFrame):
    def __init__(self, pages, devChanged_signal):
        super().__init__()
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )
        box = QtWidgets.QVBoxLayout()
        box.addWidget(self.stack(pages))
        self.setLayout(box)
        devChanged_signal.connect(self.set_page)

    def stack(self, pages):
        self.stack_widget = QtWidgets.QStackedWidget()
        if pages:
            for page in pages:
                self.stack_widget.addWidget(page)
        return self.stack_widget

    def add_pages(self, pages):
        for page in pages:
            self.stack_widget.addWidget(page)

    @QtCore.pyqtSlot(list)
    def set_page(self, info_list):
        self.stack_widget.setCurrentIndex(info_list[1])


class Controls(main_widgets.HBox):
    def __init__(self, multi_ctrl_to_cnct, apply_to_cnct):
        super().__init__()
        self._multi_ctrl_to_cnct = multi_ctrl_to_cnct
        self._apply_to_cnct = apply_to_cnct
        self._layout()

    def _multi_control_btn(self):
        btn = main_widgets.Button(
            "multi_control",
            "Multi Settings",
            self._multi_ctrl_to_cnct,
        )
        return btn

    def _multi_apply_btn(self):
        btn = main_widgets.Button(
            "multi_apply",
            "Apply All",
            self._apply_to_cnct,
        )
        return btn

    def _layout(self):
        self.addWidget(self._multi_control_btn())
        self.addItem(
            main_widgets.Spacer(h_pol=QtWidgets.QSizePolicy.Expanding)
        )
        self.addWidget(self._multi_apply_btn())


class MainRight(QtWidgets.QWidget):
    def __init__(self, info_obj):
        super().__init__()
        self.info = info_obj
        self.setLayout(self._layout())

    def _layout(self):
        vbox = main_widgets.VBox()
        self.controls = Controls(
            self.info.main_handler.multi_settings,
            self.info.main_handler.multi_apply,
        )
        vbox.addWidget(
            Stack([], self.info.main_handler.DeviceChanged_signal)
        )
        vbox.addItem(self.controls)
        return vbox
