from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSlot


class Button(QtWidgets.QPushButton):
    def __init__(
        self,
        name: str = "",
        text: str = "",
        to_connect=None,
        font_color: str = "",
        button_color: str = "",
        font_size: int = 0,
        h_pol=QtWidgets.QSizePolicy.Preferred,
        v_pol=QtWidgets.QSizePolicy.Preferred,
        enabled=True,
    ):
        super().__init__()
        if name:
            self.setObjectName(name)
        self.setText(text)
        if to_connect:
            self.clicked.connect(to_connect)
        if font_color:
            style = f"color: rgb{font_color};\n"
            self.setStyleSheet(style)
        if button_color:
            style = (
                self.styleSheet() + f"border-color: rgb{button_color};\n"
            )
            self.setStyleSheet(style)
        if font_size:
            style = self.styleSheet() + f"font-size: {font_size}px;\n"
            self.setStyleSheet(style)
        self.setSizePolicy(h_pol, v_pol)
        if not enabled:
            self.setEnabled(enabled)


class CheckBox(QtWidgets.QCheckBox):
    def __init__(
        self,
        name: str = "",
        text: str = "",
        checked: bool = True,
        to_connect=None,
        pass_status: bool = False,
        size_policy: list = [
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Preferred,
        ],
        to_reset_event=None,
    ):
        super().__init__()
        if name:
            self.setObjectName(name)
        self.setText(text)
        self.checked = checked
        if to_connect:
            if pass_status:
                self.stateChanged.connect(
                    lambda: to_connect(self.isChecked())
                )
            else:
                self.stateChanged.connect(to_connect)
        if size_policy:
            self.setSizePolicy(size_policy[0], size_policy[1])
        self.setChecked(checked)
        if to_reset_event:
            to_reset_event.connect(self.reset)

    @pyqtSlot()
    def reset(self):
        self.setChecked(self.checked)


class ComboBox(QtWidgets.QComboBox):
    def __init__(
        self,
        name: str = "",
        items: list = [],
        h_pol=QtWidgets.QSizePolicy.Preferred,
        v_pol=QtWidgets.QSizePolicy.Preferred,
        to_connect=None,
        pass_index=False,
        to_reset_event=None,
    ):
        super().__init__()
        if name:
            self.setObjectName(name)
        if items:
            self.addItems(items)
        self.setSizePolicy(h_pol, v_pol)
        if to_connect:
            if pass_value:
                self.currentIndexChanged.connect(
                    lambda: to_connect(self.currentIndex())
                )
            else:
                self.currentIndexChanged(to_connect)
        if to_reset_event:
            to_reset_event.connect(self.reset)


class HardwareWidget(QtWidgets.QFrame):
    __slots__ = "hw_info_obj"

    def __init__(
        self,
        hw_name: str,
        hw_info: list,
        settings_btn_to_cnct,
    ):
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setLineWidth(1)

        class Top(HBox):
            def __init__(self, hw_name, settings_btn_to_cnct):
                super().__init__(self)
                self._layout(hw_name, settings_btn_to_cnct)

            def _layout(self, hw_name: str, settings_btn_to_cnct):
                label = Label(text=hw_name, font_size=22, font_weight=600)
                self.addWidget(label)
                self.addItem(
                    Spacer(
                        h_pol=QtWidgets.QSizePolicy().Expanding,
                    )
                )
                if settings_btn_to_cnct:
                    prof_settings = Button("Profile Settings")
                    prof_settings.clicked.connect(
                        lambda: settings_btn_to_cnct(hw_name)
                    )
                    self.addWidget(prof_settings)

        class HwInfo(QtWidgets.QGridLayout):
            def __init__(self, hw_info):
                super().__init__()
                self.addItem(
                    Spacer(h_pol=QtWidgets.QSizePolicy().Minimum),
                    0,
                    0,
                )
                self.addItem(
                    Spacer(h_pol=QtWidgets.QSizePolicy().Expanding),
                    0,
                    1,
                )
                self._set_labels(hw_info)

            def _set_labels(self, hw_info):
                """
                hw_info = (
                    ["Current", 0.5, "A"],
                    ["Speed", 100, "rpm"],
                    ...
                )
                """
                self.addItem(Spacer(), 1, 3)
                for i, _hw_info in enumerate(hw_info):
                    self.addWidget(Label(text=_hw_info[0]), i, 1)
                    self.addWidget(
                        Label(
                            text=_hw_info[1],
                            aligment=Qt.AlignRight | Qt.AlignVCenter,
                        ),
                        i,
                        2,
                    )
                    self.addWidget(
                        Label(
                            text=_hw_info[2],
                            aligment=Qt.AlignRight | Qt.AlignVCenter,
                        ),
                        i,
                        4,
                    )

            def update_info(self, hw_info):
                for i, _hw_info in enumerate(hw_info):
                    self.itemAtPosition(i, 2).widget().setText(_hw_info[1])

        vbox = QtWidgets.QVBoxLayout()
        vbox.addItem(Top(hw_name, settings_btn_to_cnct))
        self.hw_info_obj = HwInfo(hw_info)
        vbox.addItem(self.hw_info_obj)
        self.setLayout(vbox)

    def update_hw_info(self, _hw_info):
        self.hw_info_obj.update_info(_hw_info)


class HBox(QtWidgets.QHBoxLayout):
    def __init__(self, widget=None):
        super().__init__()
        self.setSpacing(6)
        if widget:
            self.addWidget(widget)

    def addWidgets(self, widgets):
        for widget in widgets:
            self.addWidget(widget)

    def addItems(self, items):
        for item in items:
            self.addItem(item)

    def addWitems(self, witems):
        """
        add widget or item
        """
        try:
            for witem in witems:
                self._add_witem(witem)
        except TypeError:
            self._add_witem(witems)  # if only one object provided

    def _add_witem(self, witem):
        if isinstance(witem, QtWidgets.QLayoutItem):
            self.addItem(witem)
        else:
            self.addWidget(witem)


class Label(QtWidgets.QLabel):
    def __init__(
        self,
        name: str = "",
        text: str = "",
        aligment=Qt.AlignLeft | Qt.AlignVCenter,
        font_size: int = 0,
        font_weight: int = 0,
        enabled=True,
    ):
        super().__init__()
        if name:
            self.setObjectName(name)
        self.text = str(text)
        self.setText(self.text)
        if aligment:
            self.setAlignment(aligment)
        if font_size:
            style = str(f"font-size: {font_size}px;\n")
            self.setStyleSheet(style)
        if font_weight:
            self.setStyleSheet(
                self.styleSheet() + f"font-weight: {font_weight};"
            )
        if not enabled:
            self.setEnabled(enabled)

    @pyqtSlot()
    def reset(self):
        self.setText(self.text)


class Line(QtWidgets.QFrame):
    def __init__(
        self,
        orient: str,
        size_policy: list = [
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Preferred,
        ],
    ):
        """
        orient = h/v
        """
        super().__init__()
        if orient == "h":
            self.setFrameShape(QtWidgets.QFrame.HLine)
        else:
            self.setFrameShape(QtWidgets.QFrame.VLine)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        if size_policy:
            self.setSizePolicy(size_policy[0], size_policy[1])


class Slider(QtWidgets.QSlider):
    def __init__(
        self,
        name: str = "",
        orientation=None,
        value: int = 0,
        size_policy: list = [
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Preferred,
        ],
        to_connect=None,
        pass_value=False,
        min_max: list = [0, 100],
        to_reset_event=None,
        enabled=True,
    ):
        super().__init__()
        if name:
            self.setObjectName(name)
        if orientation:
            self.setOrientation(orientation)
        self.setValue(value)
        if size_policy:
            self.setSizePolicy(size_policy[0], size_policy[1])
        if to_connect:
            if pass_value:
                self.valueChanged.connect(lambda: to_connect(self.value()))
            else:
                self.valueChanged.connect(to_connect)
        self.setMinimum(min_max[0])
        self.setMaximum(min_max[1])

        if to_reset_event:
            print("connected reset event")
            to_reset_event.connect(self.reset)

        if not enabled:

            self.setEnabled(enabled)

    @pyqtSlot()
    def reset(self):
        self.setValue(0)

    @pyqtSlot(bool)
    def mode(self, mode):
        self.setEnabled(mode)


class Spacer(QtWidgets.QSpacerItem):
    def __init__(
        self,
        h_pol=QtWidgets.QSizePolicy.Preferred,
        v_pol=QtWidgets.QSizePolicy.Preferred,
        width=40,
        height=20,
    ):
        super().__init__(width, height, h_pol, v_pol)


class StackedWidget(QtWidgets.QStackedWidget):
    def __init__(
        self,
        pages=[],
    ):
        super().__init__()
        print("main_widgets.Stack, add animations")

    def set_page(self, index: int):
        self.setCurrentIndex(index)


class VBox(QtWidgets.QVBoxLayout):
    def __init__(self, widget=None):
        super().__init__()
        self.setSpacing(6)
        if widget:
            self.addWidget(widget)

    def addWidgets(self, widgets):
        for widget in widgets:
            self.addWidget(widget)

    def addItems(self, items):
        for item in items:
            self.addItem(item)

    def addWitems(self, witems):
        """
        add widget or item
        """
        try:
            for witem in witems:
                self._add_witem(witem)
        except TypeError:
            self._add_witem(witems)  # if only one object provided

    def _add_witem(self, witem):
        if isinstance(witem, QtWidgets.QLayoutItem):
            self.addItem(witem)
        else:
            self.addWidget(witem)
