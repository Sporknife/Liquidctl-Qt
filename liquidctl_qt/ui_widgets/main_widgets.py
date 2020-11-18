from PyQt5 import QtWidgets, QtCore, QtGui


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
    ):  # pylint: disable=dangerous-default-value
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

    @QtCore.pyqtSlot()
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
    ):  # pylint: disable=dangerous-default-value
        super().__init__()
        if name:
            self.setObjectName(name)
        if items:
            self.addItems(items)
        self.setSizePolicy(h_pol, v_pol)
        if to_connect:
            if pass_index:
                self.currentIndexChanged.connect(
                    lambda: to_connect(self.currentIndex())
                )
            else:
                self.currentIndexChanged(to_connect)
        if to_reset_event:
            to_reset_event.connect(self.reset)


class DecisionDialog(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Decisions...")
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint)
        self.setWindowFlags(
            self.windowFlags() &
            ~QtCore.Qt.WindowCloseButtonHint &
            ~QtCore.Qt.WindowContextHelpButtonHint &
            ~QtCore.Qt.WindowMinimizeButtonHint
        )
        self.setLayout(self._layout())
        width, height = int(self.width()), int(self.height())

        self.setMaximumSize(width, height)

    def _layout(self):
        vbox = VBox()
        # pylint: disable=invalid-name
        MSG_TEXT = (
            "Would you like to exit the application\n"
            + "(and loose your unsaved/unapplied settings) ?"
        )
        msg_label = Label(
            text=MSG_TEXT,
            aligment=QtCore.Qt.AlignCenter | QtCore.Qt.AlignCenter,
        )
        vbox.addWidget(msg_label)
        vbox.addWidget(self._buttons_box())
        return vbox

    def _buttons_box(self):
        buttons = (
            QtWidgets.QDialogButtonBox.No | QtWidgets.QDialogButtonBox.Yes
        )
        buttons_box = QtWidgets.QDialogButtonBox(buttons)
        buttons_box.accepted.connect(self.accept)
        buttons_box.rejected.connect(self.reject)
        return buttons_box

    @QtCore.pyqtSlot(QtGui.QCloseEvent)
    def closeEvent(self, close_event):  # pylint: disable=invalid-name
        close_event.reject()


class HardwareWidget(QtWidgets.QFrame):
    """
    Hardware widget that shows you basic info about specific hardware
    and allows you to change some settings
    """
    __slots__ = ("hw_info_obj",)

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

        class Top(HBox):  # pylint: disable=used-before-assignment
            def __init__(self, hw_name, settings_btn_to_cnct):
                super().__init__(self)
                self._layout(hw_name, settings_btn_to_cnct)

            def _layout(self, hw_name: str, settings_btn_to_cnct):
                label = Label(text=hw_name, font_size=22, font_weight=600)
                self.addWidget(label)
                self.addItem(
                    Spacer(
                        h_pol=QtWidgets.QSizePolicy.Expanding,
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
                    Spacer(h_pol=QtWidgets.QSizePolicy.Minimum),
                    0,
                    0,
                )
                self.addItem(
                    Spacer(h_pol=QtWidgets.QSizePolicy.Expanding),
                    0,
                    1,
                )
                self.addItem(
                    Spacer(h_pol=QtWidgets.QSizePolicy.Fixed),
                    0,
                    5,
                )
                self._set_labels(hw_info)

            def _set_labels(self, hw_info):
                """
                hw_info = {
                    'Mode': {'value': 'DC', 'measurement': ''},
                    'Current': {'value': 0.05, 'measurement': 'A'},
                    'Speed': {'value': 686, 'measurement': 'rpm'},
                    'Voltage': {'value': 4.38, 'measurement': 'V'}
                }
                """
                self.addItem(Spacer(), 1, 3)
                for i, info in enumerate(hw_info.keys()):
                    self.addWidget(Label(text=info), i, 1)
                    self.addWidget(
                        Label(
                            text=str(hw_info.get(info).get("value")),
                            aligment=QtCore.Qt.AlignRight
                            | QtCore.Qt.AlignVCenter,
                        ),
                        i,
                        2,
                    )
                    self.addWidget(
                        Label(
                            text=hw_info.get(info).get(("measurement")),
                            aligment=QtCore.Qt.AlignRight
                            | QtCore.Qt.AlignVCenter,
                        ),
                        i,
                        4,
                    )

            def update_info(self, hw_info):
                for i, info in enumerate(hw_info.keys()):
                    self.itemAtPosition(i, 2).widget().setText(
                        str(hw_info.get(info).get("value")
                        )
                    )
                    pass

        vbox = QtWidgets.QVBoxLayout()
        vbox.addItem(Top(hw_name, settings_btn_to_cnct))
        self.hw_info_obj = HwInfo(hw_info)
        vbox.addItem(self.hw_info_obj)
        self.setLayout(vbox)

    def update_info(self, info):
        self.hw_info_obj.update_info(info)


class HBox(QtWidgets.QHBoxLayout):
    def __init__(self, widget=None):
        super().__init__()
        self.setSpacing(6)
        if widget:
            self.addWidget(widget)

    def addWidgets(self, widgets):  # pylint: disable=invalid-name
        for widget in widgets:
            self.addWidget(widget)

    def addItems(self, items):  # pylint: disable=invalid-name
        for item in items:
            self.addItem(item)

    def addWitems(self, witems):  # pylint: disable=invalid-name
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
        aligment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter,
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

    @QtCore.pyqtSlot()
    def reset(self):
        self.setText(self.text)


class Line(QtWidgets.QFrame):
    def __init__(
        self,
        orient: str,
        h_size_pol = QtWidgets.QSizePolicy.Preferred,
        v_size_pol = QtWidgets.QSizePolicy.Preferred
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
        self.setSizePolicy(h_size_pol, v_size_pol)


class Slider(QtWidgets.QSlider):
    def __init__(
        self,
        name: str = "",
        orientation=QtCore.Qt.Horizontal,
        value: int = 0,
        h_size_pol = QtWidgets.QSizePolicy.Preferred,
        v_size_pol = QtWidgets.QSizePolicy.Preferred,
        to_connect=None,
        pass_value=False,
        min_max: list = [0, 100],
        to_reset_event=None,
        enabled=True,
    ):
        super().__init__()
        self.setObjectName(name)
        self.setOrientation(orientation)
        self.setValue(value)
        self.setSizePolicy(h_size_pol, v_size_pol)
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

    @QtCore.pyqtSlot()
    def reset(self):
        self.setValue(0)

    @QtCore.pyqtSlot(bool)
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

    def addWidgets(self, widgets):  # pylint: disable=invalid-name
        for widget in widgets:
            self.addWidget(widget)

    def addItems(self, items):  # pylint: disable=invalid-name
        for item in items:
            self.addItem(item)

    def addWitems(self, witems):  # pylint: disable=invalid-name
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
