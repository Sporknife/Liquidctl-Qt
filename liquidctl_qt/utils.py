from os import path, makedirs, fsencode
from glob import glob

from pandas import DataFrame
from numpy import int8 as np_int8


class Profiles:
    """Main class for creating, deleting, editing profiles"""
    __slots__ = (
        "PROFILES_ROOT",
        "profiles",
        "duty_profile",
        "led_profile",
        "DUTY_PATH",
        "LED_PATH")

    def __init__(self):
        PROJECT_ROOT_NAME = "Liquidctl-Qt"  # pylint: disable=invalid-name
        self.PROFILES_ROOT = path.join(   # pylint: disable=invalid-name
            path.abspath(path.dirname(__file__)).split(
                PROJECT_ROOT_NAME)[0],
            PROJECT_ROOT_NAME + "/Profiles"
        )
        self.makedirs(self.PROFILES_ROOT)
        self.profiles = {}  # stores pandas.DataFrame objects
        self.duty_profile = DutyProfiles(self)
        self.led_profile = LedProfiles(self)

    def _duty_profiles(self):
        self.DUTY_PATH = path.join(  # pylint: disable=invalid-name
            self.PROFILES_ROOT, "DutyProfiles"
        )
        self.profiles.makedirs(self.DUTY_PATH)

    def _led_profiles(self):
        self.LED_PATH = path.join(  # pylint: disable=invalid-name
            self.profiles.PROFILES_ROOT, "LedProfiles"
        )
        self.profiles.makedirs(self.LED_PATH)

    def makedirs(self, str_path: str):
        if path.exists(path.normpath(str_path)):
            return
        makedirs(str_path)


class DutyProfiles:
    def __init__(self, profiles_obj: Profiles):
        self.profiles = profiles_obj

    def load_profiles(self):
        pass

    def create_profile(self):
        raise NotImplementedError

    def str_to_frame(self, data_frame_str: str):
        """DataFrame dict in a str converted into DataFrame object"""
        return DataFrame.from_dict(
            data_frame_str,
            orient="columns",
            dtype=np_int8
        )

    def frame_to_str(self, data_frame):
        """converts numpy array from DataFrame to a single line dict string"""
        return data_frame.to_dict()


class LedProfiles:
    def __init__(self, profiles_obj: Profiles):
        self.profiles = profiles_obj

    def load_profiles(self):
        print(self.root_path)

    def create_profile(self):
        raise NotImplementedError
