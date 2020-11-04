from os import path
from glob import glob
from ui_widgets import main_widgets as widgets

# from pandas import DataFrame, read_json
# from numpy import int8 as np_int8


class DutyProfiles:
    def __init__(self):
        self.root_path = path.dirname(path.abspath(__name__))
        self.profiles = []  # stores pandas.DataFrame object's

    def load_profiles(self):
        pass

    def get_profiles(self):
        pass


class LedProfiles:
    def __init__(self):
        self.root_path = path.dirname(path.abspath(__name__))

    def get_profiles(self):
        pass

    def load_profiles(self):
        print(self.root_path)

    def create_profile(self, name: str, values: dict = {}):
        pass
