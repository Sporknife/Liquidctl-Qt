from PyQt5 import QtWidgets, QtCore
from ui_widgets import main_widgets
import pandas as pd
import numpy as np


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
        return witems

    def reset_connect(self, witems, layout=False):
        """Connects widgets or widgets in a layout to reset signal"""
        if not layout:
            for widget in witems:
                self.reset_signal.connect(widget.reset)
        else:  # if witems is layout
            for i in range(witems.count()):
                widget = witems.itemAt(i).widget()
                self.reset_signal.connect(widget.reset)
        return witems


class WidgetAdder:
    """
    Add widget to layout and returns widget object
    to be saved in a variable
    """
    __slots__ = ("class_obj", "layout")

    def __init__(self, class_obj, layout_obj):
        self.class_obj = class_obj  # just pass "self"
        self.layout = layout_obj  # layout to which widgets should be added

    def witem_adder(self, name="", widget=None, item=None):
        # name = name for __settattr__
        # widget = widget object
        if widget:
            if name:
                self.class_obj.__setattr__(name, widget)
            self.layout.addWidget(widget)
            return widget
        elif item:
            if name:
                self.class_obj.__setattr__(name, item)
            self.layout.addItem(item)


class ProfileEditor(QtWidgets.QWidget):
    """Main widget"""
    __slots__ = ("signals",)

    """Steps signals"""
    add_step_signal = QtCore.pyqtSignal()  # add a step
    update_step_signal = QtCore.pyqtSignal()  # update current step
    remove_step_signal = QtCore.pyqtSignal()  # remove step
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
        witem_adder = WidgetAdder(self, vbox).witem_adder
        witem_adder(item=ProfileModeChooser(self))
        witem_adder("steps_viewer", widget=StepsViewer(self, model=None))
        vbox.addItem(StepControl(self))
        witem_adder("tempduty_sliders", item=TempDutySliders(self))
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
    """
    Allows you to view steps and their values
    """
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
        self.profile_editor.update_step_signal.connect(self.update_step)
        self.profile_editor.add_step_signal.connect(self.add_step)

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

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    # pylint: disable=invalid-name, unused-argument
    def currentChanged(self, current, previous):
        """when currently selected is changed by the program or user"""
        self.update_sliders()

    @QtCore.pyqtSlot()
    def add_step(self):
        """Inserts step accordingly to temperature"""
        temp, duty, df_new = self.get_info()
        iloc_with_temp = self.model().get_iloc(temp)
        DIALOG_MSG = (  # pylint: disable=invalid-name
            "There is a step with the same temprature" +
            "\nWould you like yo overwrite it?"
        )
        decision_dialog = main_widgets.DecisionDialog(DIALOG_MSG)

        # if a step with same temp. value exists and if so get user input
        if iloc_with_temp is not None and decision_dialog.exec_():
            self.model().updateRow(temp, duty, iloc_int=iloc_with_temp)
            self.selectRow(iloc_with_temp)  # sets active row
        else:
            iloc_for_row = self.model().get_iloc_for_row(temp)
            self.model().addRow(iloc_for_row, df_new)  # adds the new row
            self.selectRow(iloc_for_row)  # sets active row

    @QtCore.pyqtSlot()
    def update_step(self):
        """
        Updates currently selected step to values specified in sliders
        """
        temp, duty, _ = self.get_info()
        current_index = self.currentIndex()
        if current_index.isValid():
            current_row_iloc = current_index.row()
            DIALOG_MSG = (  # pylint: disable=invalid-name
                "There is a step with the same temprature" +
                "\nWould you like yo overwrite it?"
            )
            decision_dialog = main_widgets.DecisionDialog(DIALOG_MSG)
            iloc_with_temp = self.model().get_iloc(temp)

            # if a step with same temp. value exists and if so get user input
            if iloc_with_temp is not None and decision_dialog.exec_():
                # remove row with the same temp. value
                self.model().removeRow(iloc_with_temp)
                # update current row
                self.model().updateRow(temp, duty, iloc_int=current_row_iloc)
                self.selectRow(current_row_iloc)  # sets active row

            # if a step with the same temp. values doesn't exist
            else:
                self.model().updateRow(temp, duty, iloc_int=current_row_iloc)
                self.selectRow(self.model().get_iloc(temp))  # sets active row

    @QtCore.pyqtSlot()
    def remove_step(self):
        """Removes currently selected step"""
        if self.currentIndex().isValid():
            self.model().removeRow(
                self.currentIndex().row()
            )
            self.update_sliders()

    def get_info(self):
        """
        Returns temp, duty, and a new df for adding a new row in the original df
        """
        temp, duty = (
            self.profile_editor.tempduty_sliders.get_values()
        )
        df_new = pd.DataFrame(
            [[temp, duty]],
            columns=["Temperature", "Duty"],
            dtype=np.int8
        )
        return temp, duty, df_new

    def update_sliders(self):
        """
        Updates sliders by getting data from the DataFrame object
        """
        index_model = self.currentIndex()
        if index_model.isValid():
            temp, duty = self.model().df.iloc[index_model.row()].to_list()
            self.profile_editor.set_sliders_value_signal.emit(temp, duty)

    def index_at_pos(self, xpos, ypos):
        point = QtCore.QPoint(xpos, ypos)
        return self.indexAt(point)

    def _set_model(self):  # fixme: delete this !
        # this is for testing purposes only
        df = pd.DataFrame(
            [[i, i + 4] for i in range(0, 50)],
            columns=["Temperature", "Duty"],
            dtype=np.int8
        )
        self.setModel(TempDutyModel(df))


class TempDutyModel(QtCore.QAbstractTableModel):
    """
    Model that is using pandas.DataFrame
    """
    __slots__ = ("df",)

    def __init__(self, df):
        super().__init__()
        self.df = df

    # pylint doesn't detect the arg is used, pylint: disable=unused-argument
    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            value = self.df.iloc[index.row(), index.column()]
            return str(int(value))  # i need to do this when updating a value

    def rowCount(self, args):  # pylint: disable=invalid-name
        return self.df.shape[0]

    def columnCount(self, args):  # pylint: disable=invalid-name
        return self.df.shape[1]

    # pylint: disable=invalid-name
    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return str(self.df.columns[section])
            if orientation == QtCore.Qt.Vertical:
                return str(self.df.index[section])

    def removeRow(self, iloc):  # pylint: disable=invalid-name
        parent = QtCore.QModelIndex()
        self.beginRemoveRows(parent, iloc, iloc)
        self.df = self.df.drop(self.df.index[iloc])
        self.dataChanged.emit(parent, parent)
        self.endRemoveRows()

    # pylint: disable=invalid-name
    def addRow(self, iloc, df_new):
        self.beginInsertRows(QtCore.QModelIndex(), iloc, iloc)
        self.df = self.df.append(
            df_new, ignore_index=True).sort_values(by="Temperature")
        self.endInsertRows()

    def updateRow(self, temp, duty, loc_int=None, iloc_int=None):  # pylint: disable=invalid-name
        if loc_int is not None:
            self.df.loc[loc_int] = [temp, duty]
            self.df.sort_values(by="Temperature", inplace=True)
        elif iloc_int is not None:
            self.df.iloc[iloc_int] = [temp, duty]
            self.df.sort_values(by="Temperature", inplace=True)

    def get_loc(self, temp):
        """
        Returns loc (ID which multple rows can have) with a specific temp. value
        """
        loc = self.df.index[self.df["Temperature"] == temp].to_list()
        if loc:
            return loc[0]
        return None

    def get_iloc(self, temp):
        """
        Returns iloc (row number) with a specific temp. value
        """
        iloc = (self.df["Temperature"] == temp)
        if iloc.any():
            return iloc.to_list().index(True)
        return None

    def get_iloc_for_row(self, temp):
        """
        Gets iloc for not yet existing new row with a specific temp.
        It finds iloc where the row should be placed.
        """
        # list of all temps. higher than temp (from function arg)
        iloc_for_row_list = (self.df["Temperature"] > temp).to_list()
        try:
            return iloc_for_row_list.index(True)

        # if True is not found it means the row needed to be added is last row
        except ValueError:
            return self.rowCount(None)


class StepControl(main_widgets.VBox):
    """Allows inserting, updating, removing steps"""
    __slots__ = ("profile_editor", "header_label", "btn_layout")

    def __init__(self, prof_editor_obj: ProfileEditor):
        super().__init__()
        self.profile_editor = prof_editor_obj
        self._layout()
        self.profile_editor.signals.mode_connect(
            (self.header_label,)
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
        self.addItem(
            self.profile_editor.signals.mode_connect(
                self._ctrl_btns(),
                layout=True
            )
        )

    def _ctrl_btns(self):
        self.btn_layout = main_widgets.HBox()
        witem_adder = WidgetAdder(self, self.btn_layout)

        ADD_TOOLIP = "Add step"  # pylint: disable=invalid-name
        UPDATE_TOOLIP = "Apply values to current step"  # pylint: disable=invalid-name
        REMOVE_TOOLIP = "Remove/Delete current step"  # pylint: disable=invalid-name
        witem_adder.witem_adder(
            "add_btn",
            main_widgets.Button(
                text="Add",
                to_connect=self.profile_editor.add_step_signal.emit,
                tooltip=ADD_TOOLIP,
            )
        )
        witem_adder.witem_adder(
            "update_btn",
            main_widgets.Button(
                text="Update",
                to_connect=self.profile_editor.update_step_signal.emit,
                enabled=False,
                tooltip=UPDATE_TOOLIP,
            )
        )
        witem_adder.witem_adder(
            "remove_btn",
            main_widgets.Button(
                text="Remove",
                to_connect=self.profile_editor.remove_step_signal.emit,
                enabled=False,
                tooltip=REMOVE_TOOLIP,
            )
        )
        return self.btn_layout


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
        return temp, duty

    @QtCore.pyqtSlot(int, int)
    def set_values(self, temp, duty):
        self.temp_slider.setValue(temp)
        self.duty_slider.setValue(duty)

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
        witem_adder = WidgetAdder(self, hbox).witem_adder
        witem_adder(
            "save_btn",
            main_widgets.Button(
                text="Save",
                to_connect=self.save_profile,
                color=(0, 255, 0),
                tooltip="Save current settings to a profile."
            )
        )
        witem_adder(
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
        witem_adder(
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
