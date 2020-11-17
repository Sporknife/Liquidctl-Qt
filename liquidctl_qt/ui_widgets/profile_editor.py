from PyQt5 import QtWidgets, QtCore
from ui_widgets import main_widgets


class Signals(QtCore.QObject):
    """Contains necressary signals for profile widget"""
    mode_change_signal = QtCore.pyqtSignal(bool, name="mode-changed")
    profile_changed = QtCore.pyqtSignal(list, name="mode-changed")
    remove_profile_signal = QtCore.pyqtSignal(name="update-values")
    reset_signal = QtCore.pyqtSignal(name="reset-settings")

    def widget_connect(self, to_change_widgets, signal, enabled=True):
        if not isinstance(to_change_widgets, tuple):
            self._connect_signal(to_change_widgets, signal)
            to_change_widgets.setEnabled(enabled)
            return

        for widget in to_change_widgets:
            self._connect_signal(widget, signal)

    def _connect_signal(self, widget, signal):
        signal.connect(widget.setEnabled)


class ProfileEditor(QtWidgets.QWidget):
    # when a step is added/edited
    step_changed_signal = QtCore.pyqtSignal(list)  # [step_int, [temp, duty]]
    on_step_clicked_signal = QtCore.pyqtSignal(int)  # when a step is clicked on
    on_step_add_signal = QtCore.pyqtSignal(int)  # when a step is added
    on_step_remove_signal = QtCore.pyqtSignal(int)  # when a step is remoed
    profile_changed_signal = QtCore.pyqtSignal()  # when profile is changed
    # contains data about newly selected profile (if static profile, etc.)
    on_profile_change_signal = QtCore.pyqtSignal(dict)

    def __init__(self, name: str, signals_obj):
        super().__init__()
        self.signals = signals_obj
        self.setObjectName(name)

    def _layout(self):
        hbox = main_widgets.HBox()

    def _left(self):
        vbox = main_widgets.VBox()

    def _right(self):
        pass

    @QtCore.pyqtSlot()
    def on_step_change(self, step_info):
        """
        when a step is changed
        """
        step_index = step_info[0]
        temp, duty = step_info[1]

class ProfileModeChooser(main_widgets.HBox):
    """
    Select the profile and its mode
    """

    def __init__(self, prof_editor_obj):
        super().__init__()
        self.prof_editor = prof_editor_obj
        self._layout()

    def _layout(self):
        self.addWidget(self._left())
        self.addItem(
            main_widgets.Spacer(
                QtWidgets.QSizePolicy.Minimum,
                QtWidgets.QSizePolicy.Fixed,
                5,
            )
        )
        self.addWidget(self._right())

    def _left(self):
        return main_widgets.ComboBox(
            name="profile-chooser",
            items=[],
            to_connect=self.on_profile_change,
            pass_index=True,
        )

    def _right(self):
        pass

    @QtCore.pyqtSlot(int)
    def on_profile_change(self, index):
        print("profile changed !")
