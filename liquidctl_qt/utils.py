from os import path, makedirs, remove
from glob import glob
import pandas as pd
import json
from io import StringIO


class Profiles:
    """
    Main class for creating, deleting, editing profiles
    """

    __slots__ = (
        "PROFILES_ROOT",
        "profiles",
        "duty_profiles",
        "led_profiles",
    )

    def __init__(self):
        self._init()

    def _init(self):
        # pylint: disable=invalid-name
        self.PROFILES_ROOT = path.expanduser("~/.config/Liquidctl-Qt/")
        self.duty_profiles = DutyProfiles(self, self.DUTY_PATH)
        self.led_profiles = LedProfiles(self, self.LED_PATH)

    @property
    def DUTY_PATH(self):  # pylint: disable=invalid-name
        return path.join(self.PROFILES_ROOT, "DutyProfiles")

    @property
    def LED_PATH(self):  # pylint: disable=invalid-name
        return path.join(self.PROFILES_ROOT, "LedProfiles")

    def mkdirs(self, str_path: str):
        if path.exists(path.normpath(str_path)):
            return
        makedirs(str_path)

    def file_exists(self, profiles_obj, profile_name):
        """
        Check if a profile exists by checking if a file with profile_name as
        name in the ROOT_PATH of profiles_obj
        """
        if path.exists(path.join(profiles_obj.ROOT_PATH, profile_name)):
            return True
        return False


class DutyProfiles:
    """Save, delete, edit duty profiles"""
    __slots__ = ("ROOT_PATH", "profiles")

    def __init__(self, profiles_obj, profiles_path):
        self.ROOT_PATH = profiles_path  # pylint: disable=invalid-name
        self.profiles = {}
        profiles_obj.mkdirs(self.ROOT_PATH)

    def get_profiles(self):  # fixme: check if it works
        profiles = []
        for profile_file_path in glob(path.join(self.ROOT_PATH, "*.json")):
            profiles.append(profile_file_path.split("/")[-1].split(".")[0])
        return profiles

    def load_profile(self, profile_name: str):  # fixme: check if it works
        """
        Returns a dict obj representing profile settings
        """
        profile_file_name = profile_name + ".json"
        with open(path.join(
                self.ROOT_PATH, profile_file_name), "r") as profile_file:
            return json.loads(profile_file.read())

    def save_profile(self, profile_settings: dict):  # fixme: check if it works
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
        with open(
            path.join(
                self.ROOT_PATH, profile_settings.get("name") + ".json"), "w"
        ) as profile_file:
            profile_file.write(json.dumps(profile_settings))

    def remove_profile(self, profile_name: str):  # fixme: check if it works
        profile_file_name = profile_name + ".json"
        remove(path.join(self.ROOT_PATH, profile_file_name))

    def str_to_frame(self, data_frame_str: str):
        """
        Converts a DataFrame saved in a string back into a DataFrame object
        """
        return pd.read_csv(StringIO(data_frame_str.replace(";", "\n")))

    def frame_to_str(self, df):
        """
        Converts numpy array from DataFrame to a single line dict string
        """
        str_df = df.to_csv(
            header=["Temperature", "Duty"],
            index=False,
        ).replace("\n", ";")
        if str_df[0] == ",":
            return str_df[1:]
        return str_df

    def set_duty(self, device_obj, hw_name, static_duty=None, profile_df=None):
        hw_name = hw_name.replace(" ", "").lower()
        if static_duty is not None:
            device_obj.set_fixed_speed(hw_name, static_duty)

        if profile_df:
            pass


class LedProfiles:
    """Save, delete, edit led profiles"""
    __slots__ = ("ROOT_PATH", "profiles")

    def __init__(self, profiles_obj, profiles_path):
        self.ROOT_PATH = profiles_path  # pylint: disable=invalid-name
        self.profiles = {}
        profiles_obj.mkdirs(self.ROOT_PATH)

    @property
    def profiles_paths(self):
        """
        Returns all profile names
        """
        globbed = glob(path.join(self.ROOT_PATH, "*.lclp"))
        if globbed:
            return globbed
        return None

    def load_profiles(self):
        pass

    def create_profile(self):
        pass


class WidgetAdder:
    """
    Add widget to layout and returns widget object
    to be saved in a variable
    """

    # __slots__ = ("class_obj", "layout")

    def __init__(self, class_obj, layout_obj):
        self.class_obj = class_obj
        self.layout = layout_obj  # layout to which widgets should be added

    def widget_adder(self, name="", widget=None):
        if name:
            self.class_obj.__setattr__(name, widget)
        self.layout.addWidget(widget)
        return widget

    def item_adder(self, name="", item=None):
        if name:
            self.class_obj.__setattr__(name, item)
        self.layout.addItem(item)
        return item
