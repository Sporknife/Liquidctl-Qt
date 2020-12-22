from PySide6 import QtWidgets
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
