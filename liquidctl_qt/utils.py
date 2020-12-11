from os import path, makedirs, remove
from glob import glob
import pandas as pd
import numpy as np
import json


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
        PROJECT_ROOT_NAME = "Liquidctl-Qt"  # pylint: disable=invalid-name
        self.PROFILES_ROOT = path.expanduser("~/.config/Liquidctl-Qt/")
        self.duty_profiles = DutyProfiles(self, self.DUTY_PATH)
        self.led_profiles = LedProfiles(self, self.LED_PATH)

    @property
    def DUTY_PATH(self):  # pylint: disable=invalid-name
        return path.join(
            self.PROFILES_ROOT, "DutyProfiles"
        )

    @property
    def LED_PATH(self):  # pylint: disable=invalid-name
        return path.join(
            self.PROFILES_ROOT, "LedProfiles"
        )

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
    __slots__ = ("ROOT_PATH", "profiles")

    def __init__(self, profiles_obj, path):
        self.ROOT_PATH = path
        self.profiles = {}
        profiles_obj.mkdirs(self.ROOT_PATH)

    def get_profiles(self): # fixme: check if it works
        return glob(path.join(self.ROOT_PATH, "*.json"))

    def load_profile(self, profile_name: str): # fixme: check if it works
        """
        Returns a dict obj representing profile settings
        """
        profile_name = profile_name + ".json"
        with open(path.join(self.ROOT_PATH, profile_name), "r") as profile_file:
            return json.loads(profile_file.read())

    def save_profile(self, profile_settings: dict): # fixme: check if it works
        """
        Saves profile settings
        profile = {
            "name": str,
            "device_info": {
                "name": str,  # device name
                "vendor_id": str,  # device vendor id
                "product_id": str,  # device product id
            },
            "static": bool,  # if duty is static - True OR False
            "static_duty": int,  # int from 0 to 100 ELSE None
            "data_frame": pd.DataFrame, # DataFrame object ELSE None
        }
        """
        with open(
            path.join(
                self.ROOT_PATH, profile_settings.get("name")+".json"), "w") as profile_file:
            profile_file.write(json.dumps(profile_settings))

    def remove_profile(self, profile_name: str): # fixme: check if it works
        remove(path.join(self.ROOT_PATH, profile_name+".json"))



    def str_to_frame(self, data_frame_str: str):
        """
        Converts a DataFrame saved in a string back into a DataFrame object
        """
        return pd.DataFrame.from_csv(
            data_frame_str.replace(";", "\n"),
            orient="columns",
            dtype=np.int8
        )

    def frame_to_str(self, df):
        """
        Converts numpy array from DataFrame to a single line dict string
        """
        return df.to_csv().replace("\n", ";")


class LedProfiles:
    __slots__ = ("ROOT_PATH", "profiles")

    def __init__(self, profiles_obj, path):
        self.ROOT_PATH = path
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
