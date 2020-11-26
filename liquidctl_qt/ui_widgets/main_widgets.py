from PyQt5 import QtWidgets, QtCore, QtGui


class Button(QtWidgets.QPushButton):
    __slots__ = ("enabled_style",)

    def __init__(
        self,
        name: str = "",
        text: str = "",
        to_connect=None,
        color=(),  # when button enabled
        disabled_color=(),  # when button disabled
        font_size: int = 0,
        h_pol=QtWidgets.QSizePolicy.Preferred,
        v_pol=QtWidgets.QSizePolicy.Preferred,
        enabled=True,
        tooltip="",
    ):
        super().__init__()
        self.enabled_style = []
        if name:
            self.setObjectName(name)
        self.setText(text)
        if to_connect:
            self.clicked.connect(to_connect)
        if color:  # sets color for text and buttons border
            self.enabled_style.append(f"color: rgb{color};")
        if disabled_color:  # when button is disabled it uses this color
            self.setStyleSheet(
                "QPushButton:disabled {color: rgb"
                + str(disabled_color) + "}\n")
        if font_size:
            self.enabled_style.append(f"font-size: {font_size}px;")
        self.setSizePolicy(h_pol, v_pol)
        if not enabled:
            self.setEnabled(enabled)
        if tooltip:
            self.setToolTip(tooltip)
        if any((color, font_size)):
            self._enabled_set_style()

    def _enabled_set_style(self):
        """Sets style for enabled widget"""
        list_style = ["QPushButton {", "}"]
        [  # pylint: disable=expression-not-assigned
            list_style.insert(1, style) for style in self.enabled_style if style
        ]
        curr_style = self.styleSheet()
        self.setStyleSheet(curr_style + "\n".join(list_style))


class CheckBox(QtWidgets.QCheckBox):
    def __init__(
        self,
        name: str = "",
        text: str = "",
        checked: bool = True,
        h_pol=QtWidgets.QSizePolicy.Preferred,
        v_pol=QtWidgets.QSizePolicy.Preferred,
        to_connect=None,
    ):  # pylint: disable=dangerous-default-value
        super().__init__()

        if name:
            self.setObjectName(name)
        self.setText(text)
        if to_connect:
            self.stateChanged.connect(to_connect)
        self.setSizePolicy(h_pol, v_pol)
        self.setChecked(checked)


class ComboBox(QtWidgets.QComboBox):
    def __init__(
        self,
        name: str = "",
        items: list = [],
        h_pol=QtWidgets.QSizePolicy.Preferred,
        v_pol=QtWidgets.QSizePolicy.Preferred,
        to_connect=None,
    ):  # pylint: disable=dangerous-default-value
        super().__init__()
        if name:
            self.setObjectName(name)
        if items:
            self.addItems(items)
        self.setSizePolicy(h_pol, v_pol)
        if to_connect:
            self.currentIndexChanged.connect(to_connect)


class DecisionDialog(QtWidgets.QDialog):
    """Dialog for user action, Message + Y/N"""

    # pylint: disable=invalid-name
    def __init__(self, MSG_TEXT, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle("Decisions...")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.CustomizeWindowHint)
        self.setWindowFlags(
            self.windowFlags() &
            ~QtCore.Qt.WindowCloseButtonHint &
            ~QtCore.Qt.WindowContextHelpButtonHint
        )
        self.setLayout(self._layout(MSG_TEXT))
        width, height = int(self.width()), int(self.height())

        self.setMaximumSize(width, height)

    def _layout(self, MSG_TEXT):  # pylint: disable=invalid-name
        vbox = VBox()
        # pylint: disable=invalid-name
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
    Hardware widget that shows basic info about specific hardware
    and allows to change some settings
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
    __slots__ = ("text",)

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


class Slider(QtWidgets.QSlider):
    def __init__(
        self,
        name="",
        min_value=0,
        max_value=100,
        h_pol=QtWidgets.QSizePolicy.Preferred,
        v_pol=QtWidgets.QSizePolicy.Preferred,
        to_connect=None,
        enabled=True,
        orientation=QtCore.Qt.Horizontal
    ):
        super().__init__()
        if name:
            self.setObjectName(name)
        self.setValue(min_value)
        self.setMinimum(min_value)
        self.setMaximum(max_value)
        self.setSizePolicy(h_pol, v_pol)
        if to_connect:
            self.valueChanged.connect(to_connect)
        self.setOrientation(orientation)
        self.setEnabled(enabled)


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
