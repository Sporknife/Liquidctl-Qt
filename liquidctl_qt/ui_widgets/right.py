from PyQt5 import QtWidgets, QtCore
from ui_widgets import main_widgets


class Stack(QtWidgets.QFrame):
    def __init__(self, pages, devChanged_signal):
        super().__init__()
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding,
        )
        self._style()
        self._layout(pages)
        devChanged_signal.connect(self.set_page)

    def _style(self):
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setLineWidth(1)

    def _layout(self, pages):
        box = QtWidgets.QVBoxLayout()
        box.addWidget(self._stacked_widget(pages))
        self.setLayout(box)

    def _stacked_widget(self, pages):
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
    def __init__(self, multi_ctrl_to_cnct):
        super().__init__()
        self._multi_ctrl_to_cnct = multi_ctrl_to_cnct
        self._layout()

    def _multi_control_btn(self):
        btn = main_widgets.Button(
            "multi_control",
            "Multi Settings",
            self._multi_ctrl_to_cnct,
            enabled=False,
        )
        btn.setToolTip("Configure multiple hardware devices")
        btn.setToolTipDuration(0.5)
        return btn

    def _layout(self):
        self.addItem(
            main_widgets.Spacer(h_pol=QtWidgets.QSizePolicy.Expanding)
        )
        self.addWidget(self._multi_control_btn())


class MainRight(QtWidgets.QWidget):
    def __init__(self, info_obj):
        super().__init__()
        self.info = info_obj
        self.setLayout(self._layout())

    def _layout(self):
        vbox = main_widgets.VBox()
        self.controls = Controls(
            self.info.main_handler.multi_settings,
        )
        vbox.addWidget(
            Stack(
                pages=[],
                devChanged_signal=self.info.main_handler.DeviceChanged_signal,
            )
        )
        vbox.addItem(self.controls)
        return vbox
