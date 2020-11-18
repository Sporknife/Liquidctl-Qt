from os import path
from glob import glob

# from pandas import DataFrame, read_json
# from numpy import int8 as np_int8


class Profiles:
    def __init__(self):
        self.profiles_paths = glob(
            path.join(
                "/".join(path.dirname(path.abspath(__name__))).rsplit("/")[
                    :-1
                ],
                "profiles/*.lcp",
            )
        )
        self.profiles = {}  # stores pandas.DataFrame object's


class DutyProfiles:
    def __init__(self, paths: list):
        self.paths = paths

    def load_profiles(self):
        pass

    def create_profile(self):
        raise NotImplementedError


class LedProfiles:
    def __init__(self, paths: list):
        self.paths = paths

    def load_profiles(self):
        print(self.root_path)

    def create_profile(self):
        raise NotImplementedError
