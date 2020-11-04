from random import randint

"""
Fake devices to test the app
"""


class FanDevice:
    __slots__ = (
        "description",
        "address",
        "serial_number",
    )

    def __init__(self, data):
        self.description = data[0]
        self.address = data[1]
        self.serial_number = "fake-serial"

    def connect(self):
        print("connected:", self.description)

    def disconnect(self):
        print("disconnected:", self.description)

    def get_status(self):
        ran_int = randint(25, 100)
        return [
            ("Fan 1", "DC", ""),
            ("Fan 1 current", 0.05, "A"),
            ("Fan 1 speed", ran_int, "rpm"),
            ("Fan 1 voltage", 4.51, "V"),
            ("Fan 2", "DC", ""),
            ("Fan 2 current", 0.05, "A"),
            ("Fan 2 speed", ran_int, "rpm"),
            ("Fan 2 voltage", 4.38, "V"),
            ("Fan 3", "DC", ""),
            ("Fan 3 current", 0.05, "A"),
            ("Fan 3 speed", ran_int, "rpm"),
            ("Fan 3 voltage", 4.38, "V"),
            ("Fan 4", "—", ""),
            ("Fan 5", "—", ""),
            ("Fan 6", "—", ""),
            ("Firmware version", "1.0.4", ""),
            ("Noise level", 106, "dB"),
        ]

    def initialize(self):
        print("initialized: ", self.description)

    class device:
        ran_int = randint(25, 100)
        hidinfo = {
            "path": b"/dev/hidraw9",
            "vendor_id": 1000,
            "product_id": "ran_int",
            "serial_number": "ow;iejoigj",
            "release_number": ran_int,
            "manufacturer_string": "NZXT.-Inc.",
            "product_string": "NZXT USB Device",
            "usage_page": ran_int,
            "usage": ran_int,
            "interface_number": ran_int,
        }
