from os import path
from glob import glob
from ui_widgets import main_widgets as widgets


class DutyProfiles:
    def __init__(self):
        self.root_path = path.dirname(path.abspath(__name__))

    @property
    def profiles(self):
        profiles: list = glob(path.join(self.root_path, "profiles/fan/*"))
        return profiles

    def add_profiles(self, combobox: widgets.ComboBox = None):
        combobox.addItems(self.profiles)

    def create_profile(self, name: str, values: dict = {}):
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
