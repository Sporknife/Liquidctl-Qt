from PySide6 import QtWidgets, QtCore
from ui_widgets import main_widgets
import string


class NameInput(QtWidgets.QLineEdit):
    """An implementati of user text input (used for name input)"""

    def __init__(
        self,
    ):
        super().__init__()

        self.setPlaceholderText("Type here")
        self.setDragEnabled(False)
        self.setMaxLength(20)


class ProfileNameDialog(main_widgets.Dialog):
    """Used for user input to name the profile"""

    def __init__(self, main_dialog):
        super().__init__(title="Profile Name Input", parent=main_dialog)
        self.setModal(True)
        self.setLayout(self._layout())
        self.adjust_size()

    def _layout(self):
        vbox = main_widgets.VBox()
        vbox.addItem(self._top())
        vbox.addItem(self._bottom())
        return vbox

    def _top(self):
        """label and text input"""
        vbox = main_widgets.VBox()

        def label():
            url_link = (
                '<a href="https://github.com/Sporknife/Liquidctl-Qt/' +
                'blob/master/README.md#profile-naming-rules">here.</a>'
            )
            label = main_widgets.Label(
                text=(
                    "Name of new profile. Check for blocked letters: " +
                    url_link
                ),
                font_size=16
            )

            label.setOpenExternalLinks(True)
            return label

        def text_input():
            """Widget for text input"""
            text_input = NameInput()
            text_input.textChanged.connect(self.content_changed)
            return text_input

        self._text_input = text_input()
        vbox.addWidgets((label(), self._text_input))
        return vbox

    def _bottom(self):
        """Contains ok and cancel buttons for decision control"""
        hbox = main_widgets.HBox()
        no_btn = main_widgets.Button(
            text="Cancel",
            to_connect=self.reject,
            tooltip="Don't save the profile and close the dialog",
        )

        self.yes_btn = main_widgets.Button(
            text="Save",
            to_connect=self.accept,
            enabled=False,
            tooltip="Save the profile"
        )
        spacer = main_widgets.Spacer(h_pol=QtWidgets.QSizePolicy.Expanding)
        hbox.addWitems((spacer, no_btn, self.yes_btn))
        return hbox

    def content_changed(self):
        if self.name_checker(self._text_input.text()):
            self.yes_btn.setEnabled(True)

        else:
            self.yes_btn.setEnabled(False)

    def name_checker(self, text):
        letters = list(string.ascii_letters + string.digits + "-_")
        if len(text) > 0:
            for char in text:
                if char not in letters:
                    return False
            return True
        return False

    @property
    def name(self):
        return self._text_input.text()

class ProfileControls(main_widgets.HBox):
    def __init__(self, profile_handler):
        super().__init__()
        self.profile_handler = profile_handler
        self._layout()

    def _layout(self):
        self.addSpacerItem(
            main_widgets.Spacer(
                h_pol=QtWidgets.QSizePolicy.Expanding,
                width=40,
            )
        )
        self._btns()

    def _btns(self):
        self.addWidget(
            main_widgets.Button(
                "Reload Graph",
                self.profile_handler.reload_graph_signal.emit,
                enabled=False,
                tooltip="Recreates the graph from current settings"
            )
        )
        self.addWidget(
            main_widgets.Button(
                "Apply settings",
                self.profile_handler.apply_settings_signal.emit,
                enabled=True,
                tooltip="Applies current settings"
            )
        )


class GraphFrame(QtWidgets.QFrame):
    def __init__(self, profile_handler):
        super().__init__()
        self.profile_handler = profile_handler
        self._style()

    def _style(self):
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Expanding
        )
        self.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setLineWidth(1)


class MsgDialog(main_widgets.Dialog):
    def __init__(self, parent, DIALOG_MSG):
        super().__init__("Message", parent)
        self.DIALOG_MSG = DIALOG_MSG  # pylint: disable=invalid-name
        self.setLayout(self._layout())
        self.adjust_size()

    def _layout(self):
        vbox = main_widgets.VBox()
        vbox.addWidget(
            main_widgets.Label(
            self.DIALOG_MSG,
            alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom
        ))
        vbox.addItem(self._btn_layout())
        return vbox

    def _btn_layout(self):
        hbox = main_widgets.HBox()
        hbox.addSpacerItem(
            main_widgets.Spacer(
                height=0,
                width=20,
                v_pol=QtWidgets.QSizePolicy.Ignored,
                h_pol=QtWidgets.QSizePolicy.Expanding
            )
        )
        hbox.addWidget(
            main_widgets.Button(
                text="OK",
                to_connect=self.close
            )
        )
        return hbox
