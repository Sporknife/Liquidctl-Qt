from PyQt5 import QtWidgets, QtCore
from ui_widgets import main_widgets


class Signals:
    """Connect signals to slots, add widgets to layout"""
    __slots__ = ("mode_signal", "reset_signal")

    def __init__(self, mode_signal, reset_signal):
        self.mode_signal = mode_signal
        self.reset_signal = reset_signal

    def mode_connect(self, witems, layout=False):
        """Connects widgets or widgets in a layout to mode changed signal"""
        if not layout:
            for widget in witems:
                widget.setEnabled(False)
                self.mode_signal.connect(widget.setEnabled)
        else:  # if witems is layout
            for i in range(witems.count()):
                widget = witems.itemAt(i).widget()
                widget.setEnabled(False)
                self.mode_signal.connect(widget.setEnabled)

    def reset_connect(self, witems, layout=False):
        """Connects widgets or widgets in a layout to reset signal"""
        if not layout:
            for widget in witems:
                self.reset_signal.connect(widget.reset)
        else:  # if witems is layout
            for i in range(witems.count()):
                widget = witems.itemAt(i).widget()
                self.reset_signal.connect(widget.reset)


class WidgetAdder:
    """
    Add widget to layout and returns widget object
    to be saved in a variable
    """
    __slots__ = ("class_obj", "layout")

    def __init__(self, class_obj, layout_obj):
        self.class_obj = class_obj  # just pass "self"
        self.layout = layout_obj  # layout to which widgets should be added

    def widget_adder(self, name: str, widget, add_var=True):
        # name = name for __settattr__
        # widget = widget object
        if add_var:
            self.class_obj.__setattr__(name, widget)
        self.layout.addWidget(widget)
        return widget


class ProfileEditor(QtWidgets.QWidget):
    """Main widget"""
    __slots__ = ("signals",)

    """Steps signals"""
    step_change_signal = QtCore.pyqtSignal(list)  # edits step values
    step_activated_signal = QtCore.pyqtSignal()  # enable step controls
    add_step_signal = QtCore.pyqtSignal(int)  # when a step is added
    remove_step_signal = QtCore.pyqtSignal()  # when a step is removed
    # enables/disables step ctrls when both sliders are changed
    step_ctrl_activate_signal = QtCore.pyqtSignal(dict)
    """Sliders signals"""
    set_sliders_value_signal = QtCore.pyqtSignal(int, int)

    """Profile signals"""
    # contains data about newly selected profile (if static profile, etc.)
    profile_changed_signal = QtCore.pyqtSignal(dict)  # when profile is changed
    reset_profile_singal = QtCore.pyqtSignal(dict)  # reload profile settings
    mode_change_signal = QtCore.pyqtSignal(bool)
    delete_profile_signal = QtCore.pyqtSignal(dict)  # remove a profile

    def __init__(self, name: str):
        super().__init__()
        self.signals = Signals(
            self.mode_change_signal, self.reset_profile_singal
        )
        self.setObjectName(name)
        self.setLayout(self._layout())

    def _layout(self):
        hbox = main_widgets.HBox()
        hbox.addItem(self._left())
        return hbox

    def _left(self):
        vbox = main_widgets.VBox()
        vbox.addItem(ProfileModeChooser(self))
        vbox.addWidget(StepsViewer(self, model=None))
        vbox.addItem(StepControl(self))
        vbox.addItem(TempDutySliders(self))
        vbox.addItem(ProfileCtrl(self))
        return vbox

    def _right(self):
        pass


class ProfileModeChooser(main_widgets.HBox):
    """Select the profile and its mode"""
    __slots__ = ("profile_editor", "combobox", "checkbox")

    def __init__(self, prof_editor_obj: ProfileEditor,):
        super().__init__()
        self.profile_editor = prof_editor_obj
        self._layout()

    def _layout(self):
        self.addWidget(self._left())
        self.addItem(
            main_widgets.Spacer(
                h_pol=QtWidgets.QSizePolicy.Fixed,
                width=5,
            )
        )
        self.addWidget(self._right())

    def _left(self):
        self.combobox = main_widgets.ComboBox(
            name="profile-chooser",
            items=[],
            to_connect=self.on_profile_change,
        )
        return self.combobox

    def _right(self):
        self.checkbox = main_widgets.CheckBox(
            text="Fixed mode ?",
            to_connect=self.change_mode,
        )
        return self.checkbox

    @QtCore.pyqtSlot(int)
    def on_profile_change(self, index):
        self.profile_editor.profile_changed_signal.emit(
            {
                "new_index": index,
                "name": self.combobox.currentText()
            }
        )

    @QtCore.pyqtSlot(int)
    def change_mode(self, mode):
        self.profile_editor.mode_change_signal.emit(not mode)


class StepsViewer(QtWidgets.QTableView):
    __slots__ = ("profile_editor",)

    def __init__(self, prof_editor_obj: ProfileEditor,
                 model: QtCore.QAbstractTableModel):
        super().__init__()
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Preferred,
            QtWidgets.QSizePolicy.Expanding,
        )
        self.profile_editor = prof_editor_obj
        self._set_model()

        # if model:
        # 	self.setModel(model)

        self._setter()
        self._connect_signals()

    def _connect_signals(self):
        self.profile_editor.signals.mode_connect((self,))
        self.profile_editor.remove_step_signal.connect(self.remove_step)

    def _save_models(self):  # fixme: impliment saving models in a dict
        pass

    def _setter(self):
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setShowGrid(False)
        self.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self.verticalHeader().setVisible(False)
        pass

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def currentChanged(self, current, previous):  # pylint: disable=invalid-name
        """when currently selected is changed by the program or user"""
        row = current.row()
        model = self.model()
        duty = int(model.data(model.index(row, 1), QtCore.Qt.DisplayRole))
        temp = int(model.data(model.index(row, 0), QtCore.Qt.DisplayRole))
        self.profile_editor.set_sliders_value_signal.emit(duty, temp)

    @QtCore.pyqtSlot(dict)
    def add_step(self, data):
        """Inserts step accordingly to temperature"""
        print("add step - StepsViewer.add_step")
        raise NotImplementedError

    @QtCore.pyqtSlot(dict)
    def update_step(self, data):
        """Updates currently selected step to values in the sliders"""
        print("add step - StepsViewer.update_step")

    @QtCore.pyqtSlot()
    def remove_step(self):
        """Removes currently selected step"""
        print("remove step - StepsViewer.update_step")
        raise NotImplementedError

    def _set_model(self):  # fixme: delete this !
        # this is for testing purposes only
        from pandas import DataFrame
        data_frame = DataFrame(
            [[i, i + 4] for i in range(0, 50)],
            columns=["Temperature", "Duty"]
        )
        self.setModel(TempDutyModel(data_frame, self))


class TempDutyModel(QtCore.QAbstractTableModel):
    """Model that is using pandas.DataFrame"""
    __slots__ = ("data_frame",)

    def __init__(self, data_frame, view):
        super().__init__()
        self.data_frame = data_frame

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            value = self.data_frame.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):  # pylint: disable=invalid-name
        return self.data_frame.shape[0]

    def columnCount(self, index):  # pylint: disable=invalid-name
        return self.data_frame.shape[1]

    # pylint: disable=invalid-name
    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return str(self.data_frame.columns[section])
            if orientation == QtCore.Qt.Vertical:
                return str(self.data_frame.index[section])

    def removeRow(self, row, parent):  # pylint: disable=invalid-name
        self.beginRemoveRows(parent, row, row)
        self.rowsAboutToBeRemoved.emit(parent, row, row)
        self.data_frame.index.delete(self.data_frame.iloc[row])
        self.dataChanged.emit(parent, parent)
        self.endRemoveRows()


class StepControl(main_widgets.VBox):
    """Allows inserting, updating, removing steps"""
    __slots__ = ("profile_editor", "header_label", "btn_layout")

    def __init__(self, prof_editor_obj: ProfileEditor):
        super().__init__()
        self.profile_editor = prof_editor_obj
        self._layout()
        self.profile_editor.signals.mode_connect(
            (self.header_label, self.add_btn)
        )

    def _layout(self):
        self.header_label = main_widgets.Label(
            text="Step Control",
            aligment=QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter,
            font_size=17
        )
        self.header_label.setEnabled(False)
        self.addWidget(self.header_label)
        self.addItem(
            main_widgets.Spacer(
                v_pol=QtWidgets.QSizePolicy.Fixed,
                height=10
            )
        )
        self.addItem(self._ctrl_btns())

    def _ctrl_btns(self):
        self.btn_layout = main_widgets.HBox()
        widget_adder = WidgetAdder(self, self.btn_layout)

        ADD_TOOLIP = "Add step"  # pylint: disable=invalid-name
        UPDATE_TOOLIP = "Apply values to current step"  # pylint: disable=invalid-name
        REMOVE_TOOLIP = "Remove/Delete current step"  # pylint: disable=invalid-name
        widget_adder.widget_adder(
            "add_btn",
            main_widgets.Button(
                text="Add",
                to_connect=self.add_step,
                tooltip=ADD_TOOLIP,
            )
        )
        widget_adder.widget_adder(
            "update_btn",
            main_widgets.Button(
                text="Update",
                to_connect=self.update_step,
                enabled=False,
                tooltip=UPDATE_TOOLIP,
            )
        )
        widget_adder.widget_adder(
            "remove_btn",
            main_widgets.Button(
                text="Remove",
                to_connect=self.remove_step,
                enabled=True,
                tooltip=REMOVE_TOOLIP,
            )
        )
        return self.btn_layout

    @QtCore.pyqtSlot()
    def add_step(self):
        """Add step"""
        print("add step !")

    @QtCore.pyqtSlot()
    def update_step(self):
        """Applies values from sliders to current step"""
        print("Update step settings")

    @QtCore.pyqtSlot()
    def remove_step(self):
        """Removes current step"""
        self.profile_editor.remove_step_signal.emit()


class TempDutySliders(main_widgets.VBox):
    """Sliders for defining temperature and duty"""
    __slots__ = (
        "profile_editor",
        "sliders_changed",
        "duty_value_label",
        "duty_slider",
        "temp_value_label",
        "temp_slider")

    def __init__(self, prof_editor_obj: ProfileEditor):
        super().__init__()
        self.profile_editor = prof_editor_obj
        # when slider is changed to enable step controls
        self.sliders_changed = {
            "duty": False,
            "temperature": False
        }
        self._layout()
        self.profile_editor.set_sliders_value_signal.connect(self.set_values)

    def _layout(self):
        self.addWitems(self._duty())
        self.addWitems(self._temp())

    def _duty(self):
        hbox = main_widgets.HBox()
        header_label = main_widgets.Label(text="Duty", font_size=15)
        self.duty_value_label = self._value_label("0 %",)
        hbox.addWidgets((header_label, self.duty_value_label))
        self.duty_slider = main_widgets.Slider(
            to_connect=self.duty_slider_changed,
            enabled=True
        )
        return (hbox, self.duty_slider)

    def _temp(self):
        hbox = main_widgets.HBox()
        header_label = main_widgets.Label(text="Temperature", font_size=15)
        self.temp_value_label = self._value_label("0 °C",)
        hbox.addWidgets((header_label, self.temp_value_label))
        self.temp_slider = main_widgets.Slider(
            to_connect=self.temp_slider_changed,
        )
        self.profile_editor.signals.mode_connect((
            header_label, self.temp_value_label, self.temp_slider
        ))
        return (hbox, self.temp_slider)

    def _value_label(self, text):
        return main_widgets.Label(
            text=text,
            aligment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )

    def get_values(self):
        """Returns values from both sliders (temp. and duty)"""
        duty = self.duty_slider.value()
        temp = self.temp_slider.value()
        return duty, temp

    @QtCore.pyqtSlot(int, int)
    def set_values(self, duty, temp):
        self.duty_slider.setValue(duty)
        self.temp_slider.setValue(temp)

    @QtCore.pyqtSlot(int)
    def duty_slider_changed(self, value):
        self.duty_value_label.setText(f"{value} %")
        self.sliders_changed["duty"] = True

    @QtCore.pyqtSlot(int)
    def temp_slider_changed(self, value):
        self.temp_value_label.setText(f"{value} °C")
        self.sliders_changed["temperature"] = True


class ProfileCtrl(main_widgets.VBox):
    """Remove, reload, reset a profile"""
    __slots__ = ("profile_editor",)

    def __init__(self, prof_editor_obj):
        super().__init__()
        self.profile_editor = prof_editor_obj
        self._layout()

    def _layout(self):
        self.addWidget(
            main_widgets.Label(
                text="Profile Control",
                font_size=17
            )
        )
        self.addItem(self._ctrl_btns_layout())

    def _ctrl_btns_layout(self):
        hbox = main_widgets.HBox()
        widget_adder = WidgetAdder(self, hbox)
        widget_adder.widget_adder(
            "save_btn",
            main_widgets.Button(
                text="Save",
                to_connect=self.save_profile,
                color=(0, 255, 0),
                tooltip="Save current settings to a profile."
            )
        )
        widget_adder.widget_adder(
            "reset_btn",
            main_widgets.Button(
                text="Reset",
                to_connect=self.reset_profile,
                color=(255, 80, 0),
                disabled_color=(127, 40, 0),
                enabled=False,
                tooltip="Reset settings and reload currently selected profile."
            )
        )
        widget_adder.widget_adder(
            "delete_btn",
            main_widgets.Button(
                text="Delete",
                to_connect=self.delete_profile,
                color=(255, 0, 0),
                disabled_color=(127, 0, 0),
                enabled=False,
                tooltip="Delete currently selected profile."
            )
        )
        return hbox

    @QtCore.pyqtSlot()
    def save_profile(self):
        raise NotImplementedError

    @QtCore.pyqtSlot()
    def reset_profile(self):
        raise NotImplementedError

    @QtCore.pyqtSlot()
    def delete_profile(self):
        raise NotImplementedError
