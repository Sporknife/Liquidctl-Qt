from PySide6 import QtWidgets, QtCore
from ui_widgets import main_widgets, profile_widgets
import pandas as pd
import numpy as np
import utils
import exceptions
from liquidctl.error import NotSupportedByDevice


class Signals:
    """Connect signals to slots, add widgets to layout"""

    # __slots__ = ("mode_signal", "reset_signal")

    def __init__(self, mode_signal):
        self.mode_signal = mode_signal

    def mode_connect(self, witems=None, layout=None):
        """Connects widgets or widgets in a layout to mode changed signal"""
        if witems:
            if isinstance(witems, tuple):
                for widget in witems:
                    widget.setEnabled(False)
                    self.mode_signal.connect(widget.setEnabled)
            else:  # if only one widget is passed as witems
                witems.setEnabled(False)
                self.mode_signal.connect(witems.setEnabled)

        elif layout:
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                widget.setEnabled(False)
                self.mode_signal.connect(widget.setEnabled)

        else:
            raise exceptions.UnexpectedBehaviour(
                "none of the variables have a valid value")


class ProfileEditor(QtWidgets.QWidget):
    """Main widget for profile editor"""
    hide_dialog_signal = QtCore.Signal()
    show_dialog_signal = QtCore.Signal()

    # __slots__ = ("device_dict", "profile_handler", "signals")

    def __init__(self, main_dialog, name, device_dict: dict):
        super().__init__()
        self.setObjectName(name)
        self._init(main_dialog, device_dict)

    def _init(self, main_dialog, device_dict):
        self._variables(main_dialog, device_dict)
        self.setLayout(self._layout())
        self._load_first_profile()

    def _variables(self, main_dialog, device_dict):
        self.main_dialog = main_dialog
        self.device_dict = device_dict
        self.profile_handler = ProfileHandler(self)

    def _left(self):
        vbox = main_widgets.VBox()
        witem_adder = utils.WidgetAdder(self, vbox)
        witem_adder.item_adder(
            "profile_mode_chooser", ProfileModeChooser(self.profile_handler)
        )
        witem_adder.widget_adder("steps_editor", StepsViewEditor(self))
        witem_adder.item_adder(
            "step_control", StepControl(self.profile_handler))
        witem_adder.item_adder(
            "control_sliders", ControlSliders(self.profile_handler))
        witem_adder.item_adder(
            "profile_control", ProfileCtrl(self.profile_handler))
        return vbox

    def _right(self):
        vbox = main_widgets.VBox()
        witem_adder = utils.WidgetAdder(self, vbox)
        witem_adder.widget_adder(
            "graph_frame",
            profile_widgets.GraphFrame(self.profile_handler)
        )
        witem_adder.item_adder(
            "controls",
            profile_widgets.ProfileControls(self.profile_handler)
        )
        return vbox

    def _layout(self):
        hbox = main_widgets.HBox()
        hbox.addItem(self._left())
        hbox.addItem(self._right())

        return hbox


    def _load_first_profile(self):
        profile_name = self.profile_mode_chooser.curr_profile_name
        if profile_name:
            self.profile_handler.load_profile(profile_name)


class ProfileHandler(QtCore.QObject):
    """Used for main events like when a profile is saved, deleted, reloaded"""

    """Steps signals"""
    add_step_signal = QtCore.Signal()  # add a step
    update_step_signal = QtCore.Signal()  # update current step
    remove_step_signal = QtCore.Signal()  # remove step
    """Sliders signals"""
    set_sliders_value_signal = QtCore.Signal(int, int)
    """Profile signals"""
    # contains data about newly selected profile (if its static profile, etc.)
    load_profile_signal = QtCore.Signal(dict)  # when profile is switched
    mode_changed_signal = QtCore.Signal(bool)  # when static mode is changed
    delete_profile_signal = QtCore.Signal()  # remove current profile
    save_profile_signal = QtCore.Signal()
    # apply settings, reload the graph
    reload_graph_signal = QtCore.Signal()
    apply_settings_signal = QtCore.Signal()

    def __init__(self, profile_editor):
        super().__init__()
        self.profile_editor = profile_editor
        self.profiles = utils.Profiles()
        self.signals = Signals(self.mode_changed_signal)
        self._connect_signals()

    def _connect_signals(self):
        self.save_profile_signal.connect(self.save_profile)
        self.delete_profile_signal.connect(self.delete_profile)
        self.apply_settings_signal.connect(self.apply_settings)
        self.reload_graph_signal.connect(self.reload_graph)

    @QtCore.Slot()
    def save_profile(self):
        """
        Saves profile settings
        profile = {
            "name": str,
            "device_info": {
                "name": str,  # device name
                "vendor_id": str,  # device vendor id
                "product_id": str,  # device product id
            },
            "static_duty": int,  # int from 0 to 100 ELSE None
            "data_frame": pd.DataFrame, # DataFrame object ELSE None
        }
        """
        name_dialog = profile_widgets.ProfileNameDialog(
            main_dialog=self.profile_editor.main_dialog)
        self.profile_editor.hide_dialog_signal.emit()
        if name_dialog.exec_():
            profile_name = name_dialog.name
            profile_name_exists = bool(
                profile_name in self.profiles.duty_profiles.get_profiles()
            )
            DIALOG_MSG = "Override profile ?"  # pylint: disable=invalid-name
            # if a profile with the same name exists ask to override

            if profile_name_exists and not (
                main_widgets.DecisionDialog(
                    self.profile_editor.main_dialog, DIALOG_MSG).exec_()
            ):
                # if user selects to not override, it doesn't continue
                return
            self.profiles.duty_profiles.save_profile(
                self.profile_settings(profile_name)
            )
        self.profile_editor.show_dialog_signal.emit()

    @QtCore.Slot()
    def reload_profile(self):  # fixme: test me
        profile_name = (
            self.profile_editor.profile_mode_chooser.curr_profile_name
        )
        self.load_profile(profile_name)

    @QtCore.Slot()
    def delete_profile(self):  # fixme: test me
        self.profile_editor.profile_mode_chooser.remove_curr_profile()

    @QtCore.Slot()
    def load_profile(self, profile_name):
        static_mode = False
        profile_settings = self.profiles.duty_profiles.load_profile(
            profile_name
        )
        if profile_settings.get("static_duty") is not None:
            static_mode = True
        self.mode_changed_signal.emit(not static_mode)
        self.load_profile_signal.emit(profile_settings)

    def profile_settings(self, name) -> dict:
        if self.profile_editor.profile_mode_chooser.current_mode:
            _, duty = self.profile_editor.control_sliders.get_values()
            return {
                "name": name,
                "device_info": self.profile_editor.device_info,
                "static_duty": duty,
                "data_frame": None,
            }
        else:
            str_df = self.profile_editor.steps_editor.model_to_str()
            return {
                "name": name,
                "device_info": self.profile_editor.device_info,
                "static_duty": None,
                "data_frame": str_df,
            }

    @QtCore.Slot()
    def apply_settings(self):
        device_obj = self.profile_editor.device_dict.get("device_obj")
        hw_name = self.profile_editor.objectName()

        if self.profile_editor.profile_mode_chooser.current_mode:
            _, duty = self.profile_editor.control_sliders.get_values()
            self.profiles.duty_profiles.set_duty(
                device_obj,
                hw_name,
                static_duty=duty
            )
        else:
            try:
                self.profiles.duty_profiles.set_duty(
                    device_obj,
                    hw_name,
                    profile_df=self.profile_editor.steps_editor.model().df
                )
            except NotSupportedByDevice:
                profile_widgets.MsgDialog(
                    parent=self.profile_editor.main_dialog,
                    DIALOG_MSG="Your device does not support profiles."
                ).exec_()

    QtCore.Slot()
    def reload_graph(self):
        pass

    def decision_dialog(self, DIALOG_MSG):  # pylint: disable=invalid-name
        # self.profile_editor.hide_dialog_signal.emit()
        output = main_widgets.DecisionDialog(
            self.profile_editor.main_dialog,
            DIALOG_MSG,
            fixed_size=True
        ).exec_()
        # self.profile_editor.show_dialog_signal.emit()
        return output


class ProfileModeChooser(main_widgets.HBox):
    """Profile and its mode (static duty or not)"""

    # __slots__ = ("profile_handler",)

    def __init__(self, profile_handler):
        super().__init__()
        self.profile_handler = profile_handler
        self._layout()
        self.profile_handler.load_profile_signal.connect(self.set_settings)

    def _layout(self) -> main_widgets.HBox:
        witem_adder = utils.WidgetAdder(self, self)
        witem_adder.widget_adder("profile_chooser", widget=self._left())
        self.addSpacerItem(
            main_widgets.Spacer(
                h_pol=QtWidgets.QSizePolicy.Fixed,
                width=5,
            )
        )
        witem_adder.widget_adder("mode_chooser", widget=self._right())

    def _left(self):
        """ComboBox for profile selection"""
        return main_widgets.ComboBox(
            items=self.profile_handler.profiles.duty_profiles.get_profiles(),
            to_connect=self.change_profile,
        )

    def _right(self):
        """CheckBox for profile mode selection (static duty or not)"""
        return main_widgets.CheckBox(
            text="Fixed mode ?",
            to_connect=self.change_mode,
        )

    @property
    def curr_profile_name(self) -> str:
        return self.profile_chooser.currentText()

    @property
    def curr_index(self) -> int:
        return self.profile_chooser.currentIndex()

    @property
    def current_mode(self) -> bool:
        return self.mode_chooser.isChecked()

    def remove_curr_profile(self):
        self.removeItem(self.curr_index)

    def add_profile(self, profile_name: str):
        self.addItem(profile_name)
        self.setActivated(-1)

    @QtCore.Slot(int)
    def change_profile(self, *args):  # pylint: disable=unused-argument
        self.profile_handler.load_profile(self.curr_profile_name)

    @QtCore.Slot(bool)
    def change_mode(self, mode):
        self.profile_handler.mode_changed_signal.emit(not bool(mode))

    @QtCore.Slot(dict)
    def set_settings(self, profile_settings):
        static_mode = False
        if profile_settings.get("static_duty") is not None:
            static_mode = True
        self.mode_chooser.setChecked(static_mode)


class StepsViewEditor(QtWidgets.QTableView):
    """Allows you to view and add/update/remove steps"""

    # __slots__ = ("profile_editor", "profile_handler")

    def __init__(self, profile_editor):
        super().__init__()
        self.profile_editor = profile_editor
        self.profile_handler = profile_editor.profile_handler
        self._connect_signals()
        self._set_properties()
        self._set_init_model()

    def _connect_signals(self):
        self.profile_handler.load_profile_signal.connect(self.set_settings)
        """Connects signals to slots"""
        self.profile_handler.signals.mode_connect(witems=self)
        self.profile_handler.remove_step_signal.connect(self.remove_step)
        self.profile_handler.update_step_signal.connect(self.update_step)
        self.profile_handler.add_step_signal.connect(self.add_step)

    def _set_properties(self):
        """Sets widget properties"""
        self.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setShowGrid(False)
        self.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self.verticalHeader().setVisible(False)

    def _set_init_model(self):
        model = TempDutyModel(
            pd.DataFrame(
                [[-1, -1]],
                columns=["Temperature", "Duty"],
                dtype=np.int8
            )
        )
        self.setModel(model)
        self.model().removeRow(0)

    @QtCore.Slot(QtCore.QModelIndex, QtCore.QModelIndex)
    # pylint: disable=invalid-name, unused-argument
    def currentChanged(self, *args):
        self.update_sliders()

    @QtCore.Slot()
    def add_step(self):
        """Inserts step accordingly to temperature"""
        temp, duty, df_new = self.get_info()
        iloc_with_temp = self.model().get_iloc(temp)
        DIALOG_MSG = (  # pylint: disable=invalid-name
            "There is a step with the same temprature"
            + "\nWould you like yo overwrite it?"
        )

        # if a step with same temp. value exists and if so get user input
        if iloc_with_temp is not None:
            self.profile_editor.hide_dialog_signal.emit()
            if not self.profile_handler.decision_dialog(DIALOG_MSG):
                return
            self.profile_editor.show_dialog_signal.emit()
            self.model().updateRow(temp, duty, iloc_int=iloc_with_temp)
            self.selectRow(iloc_with_temp)  # sets active row

        else:
            iloc_for_row = self.model().get_iloc_for_row(temp)
            self.model().addRow(iloc_for_row, df_new)  # adds the new row
            self.selectRow(iloc_for_row)  # sets active row

    @QtCore.Slot()
    def update_step(self):
        """
        Updates currently selected step to values specified in sliders
        """
        temp, duty, _ = self.get_info()
        current_index = self.currentIndex()
        if current_index.isValid():
            current_row_iloc = current_index.row()
            DIALOG_MSG = (  # pylint: disable=invalid-name
                "There is a step with the same temprature"
                + "\nWould you like yo overwrite it?"
            )
            iloc_with_temp = self.model().get_iloc(temp)
            if current_row_iloc == iloc_with_temp:
                self.model().updateRow(temp, duty, iloc_int=current_row_iloc)

                # fixme: don't use this bs
                self.update_displayed_value(current_row_iloc)
                self.selectRow(current_row_iloc)  # sets active row

            elif (
                iloc_with_temp is not None and
                current_row_iloc != iloc_with_temp
                and main_widgets.DecisionDialog(
                    self.profile_editor.main_dialog,
                    DIALOG_MSG
                ).exec_()
            ):
                # remove row with the same temp. value
                self.model().removeRow(current_row_iloc)
                # update current row
                self.model().updateRow(temp, duty, iloc_int=iloc_with_temp)
                self.update_displayed_value(iloc_with_temp)
                self.selectRow(iloc_with_temp)  # sets active row

            elif iloc_with_temp is None:
                self.model().updateRow(temp, duty, iloc_int=current_row_iloc)
                # wont try to get the iloc before the row even exists
                # pylint: disable=invalid-name
                _iloc_with_temp = self.model().get_iloc(temp)
                self.update_displayed_value(_iloc_with_temp)
                self.selectRow(_iloc_with_temp)  # sets active row

            else:
                raise Exception("Something is wrong !")

    @QtCore.Slot()
    def remove_step(self):
        """Removes currently selected step"""
        if self.currentIndex().isValid():
            self.model().removeRow(self.currentIndex().row())
            self.update_sliders()

    def get_info(self):
        """
        Returns temp, duty, and a new df for adding a new row
        in the original df
        """
        temp, duty = self.profile_editor.control_sliders.get_values()
        df_new = pd.DataFrame(
            [[temp, duty]], columns=["Temperature", "Duty"], dtype=np.int8
        )
        return temp, duty, df_new

    def update_sliders(self):
        """
        Updates sliders by getting data from the DataFrame object
        """
        index_model = self.currentIndex()
        if index_model.isValid():
            temp, duty = self.model().df.iloc[index_model.row()].to_list()
            self.profile_handler.set_sliders_value_signal.emit(temp, duty)

    def update_displayed_value(self, current_row_iloc):
        """Stupid hack to instantly update the displayed value"""
        self.selectRow(current_row_iloc + 1)
        self.selectRow(current_row_iloc - 1)

    def model_to_str(self):
        return self.profile_handler.profiles.duty_profiles.frame_to_str(
            self.model().df
        )

    @QtCore.Slot(dict)
    def set_settings(self, profile_settings):
        if profile_settings.get("static_duty") is not None:
            model = TempDutyModel(
                pd.DataFrame(
                    [[-1, -1]],
                    columns=["Temperature", "Duty"],
                    dtype=np.int8
                )
            )
            model.removeRow(0)
        elif profile_settings.get("static_duty") is None:
            df = self.profile_handler.profiles.duty_profiles.str_to_frame(
                profile_settings.get("data_frame")
            )
            model = TempDutyModel(df)
        self.setModel(model)


class TempDutyModel(QtCore.QAbstractTableModel):
    """
    Model that is using pandas.DataFrame
    """

    # __slots__ = ("df",)

    def __init__(self, df):
        super().__init__()
        self.df = df

    # pylint doesn't detect the arg is used, pylint: disable=unused-argument
    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            value = self.df.iloc[index.row(), index.column()]
            return str(int(value))  # i need to do this when updating a value

    def rowCount(self, *args):  # pylint: disable=invalid-name
        return self.df.shape[0]

    def columnCount(self, *args):  # pylint: disable=invalid-name
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

    def addRow(self, iloc, df_new):  # pylint: disable=invalid-name
        self.beginInsertRows(QtCore.QModelIndex(), iloc, iloc)
        self.df = self.df.append(df_new, ignore_index=True).sort_values(
            by="Temperature"
        )
        self.endInsertRows()

    # pylint: disable=invalid-name
    def updateRow(self, temp, duty, loc_int=None, iloc_int=None):
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
        iloc = self.df["Temperature"] == temp
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
    """Allows adding, updating, removinf steps"""

    def __init__(self, profile_handler):
        super().__init__()
        self.profile_handler = profile_handler
        self._layout()

    def _layout(self):
        witem_adder = utils.WidgetAdder(self, self)
        witem_adder.widget_adder("header_label", self._header_label())
        self.addSpacerItem(
            main_widgets.Spacer(v_pol=QtWidgets.QSizePolicy.Fixed, height=5)
        )
        witem_adder.item_adder("button_btns_layout", self._ctrl_btns_layout())

    def _header_label(self):
        label = main_widgets.Label(
            text="Step Control",
            alignment=QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter,
            font_size=17,
        )
        return label

    def _ctrl_btns_layout(self):
        hbox = main_widgets.HBox()
        widget_adder = utils.WidgetAdder(self, hbox).widget_adder
        ADD_TOOLTIP = "Add step"  # pylint: disable=invalid-name
        UPDATE_TOOLTIP = "Apply values to current step"  # pylint: disable=invalid-name
        REMOVE_TOOLTIP = "Remove/Delete current step"  # pylint: disable=invalid-name

        widget_adder(
            "add_btn",
            main_widgets.Button(
                text="Add",
                to_connect=self.profile_handler.add_step_signal.emit,
                tooltip=ADD_TOOLTIP,
            ),
        )
        widget_adder(
            "update_btn",
            main_widgets.Button(
                text="Update",
                to_connect=self.profile_handler.update_step_signal.emit,
                enabled=False,
                tooltip=UPDATE_TOOLTIP,
            ),
        )
        widget_adder(
            "remove_btn",
            main_widgets.Button(
                text="Remove",
                to_connect=self.profile_handler.remove_step_signal.emit,
                enabled=False,
                tooltip=REMOVE_TOOLTIP,
            ),
        )
        self.profile_handler.signals.mode_connect(layout=hbox)
        return hbox


class ControlSliders(main_widgets.VBox):
    """Sliders for temperature & duty control"""

    def __init__(self, profile_handler):
        super().__init__()
        self.profile_handler = profile_handler
        self._layout()
        self.profile_handler.set_sliders_value_signal.connect(self.set_values)
        self.profile_handler.load_profile_signal.connect(self.set_settings)

    def _layout(self):
        self.addWitems(self._duty() + self._temp())

    def _duty(self) -> tuple:
        def header():
            hbox = main_widgets.HBox()
            header_label = self._header_label("Duty")
            self._duty_value_label = self._value_label("0 %")
            hbox.addWidgets((header_label, self._duty_value_label))
            return hbox

        self._duty_slider = main_widgets.Slider(
            to_connect=self._duty_slider_changed,
        )
        return (header(), self._duty_slider)

    def _temp(self) -> tuple:
        def header():
            hbox = main_widgets.HBox()
            header_label = self._header_label("Temperature")
            self._temp_value_label = self._value_label("0 °C")
            hbox.addWidgets((header_label, self._temp_value_label))
            return hbox

        self._temp_slider = main_widgets.Slider(
            to_connect=self._temp_slider_changed,
        )
        header_layout = header()
        self.profile_handler.signals.mode_connect(layout=header_layout)
        self.profile_handler.signals.mode_connect(witems=self._temp_slider)
        return header_layout, self._temp_slider

    def _header_label(self, text):
        return main_widgets.Label(text, font_size=15)

    def _value_label(self, text):
        return main_widgets.Label(
            text=text, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )

    @QtCore.Slot(int)
    def _temp_slider_changed(self, value):
        """When a user moves the temperature slider"""
        self._temp_value_label.setText(f"{value} °C")

    @QtCore.Slot(int)
    def _duty_slider_changed(self, value):
        """When a user moves the duty slider"""
        self._duty_value_label.setText(f"{value} %")

    def get_values(self):
        return self._temp_slider.value(), self._duty_slider.value()

    @QtCore.Slot(int, int)
    def set_values(self, temp=None, duty=None):
        if temp is not None:
            self._temp_slider.setValue(temp)
        if duty is not None:
            self._duty_slider.setValue(duty)

    @QtCore.Slot(dict)
    def set_settings(self, profile_settings):
        static_duty = profile_settings.get("static_duty")
        if static_duty is not None:
            self.set_values(duty=static_duty)


class ProfileCtrl(main_widgets.VBox):
    def __init__(self, profile_handler):
        super().__init__()
        self.profile_handler = profile_handler
        self._layout()

    def _layout(self):
        self.addWidget(
            main_widgets.Label(
                "Profile Control",
                alignment=QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter,
                font_size=17,
            )
        )
        self.addSpacerItem(
            main_widgets.Spacer(v_pol=QtWidgets.QSizePolicy.Fixed, height=5)
        )
        self.addItem(self._btn_layout())

    def _btn_layout(self):
        hbox = main_widgets.HBox()
        hbox.addWidget(
            main_widgets.Button(
                text="Save",
                to_connect=self.profile_handler.save_profile_signal.emit,
                color=(0, 255, 0),
                tooltip="Save current settings to a profile.",
            )
        )
        hbox.addWidget(
            main_widgets.Button(
                text="Reload",
                to_connect=self.profile_handler.reload_profile,
                color=(255, 80, 0),
                disabled_color=(127, 40, 0),
                enabled=False,
                tooltip="Reload currently selected profile",
            )
        )
        hbox.addWidget(
            main_widgets.Button(
                text="Delete",
                # to_connect=self.profile_handler.delete_profile_signal.emit,
                color=(255, 0, 0),
                disabled_color=(127, 0, 0),
                enabled=False,
                tooltip="Delete currently selected profile.",
            )
        )
        return hbox
