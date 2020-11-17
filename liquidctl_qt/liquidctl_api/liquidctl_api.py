from liquidctl.driver import find_liquidctl_devices
from liquidctl_api import fake_devices


class LiquidctlApi:
    __slots__ = ("devices", "devices_list", "devices_dict")

    def __init__(self):
        self.devices_list = self._devices_list()
        self.devices_dict = self._devices_dict()

    def _devices_list(self):
        devices = list(find_liquidctl_devices())
        # fake devices
        devices.append(
            fake_devices.FanDevice(
                [
                    "Fake-Device-1",
                    "fake-address-1",
                ]
            )
        )
        devices.append(
            fake_devices.FanDevice(
                [
                    "Fake-Device-2",
                    "fake-address-2",
                ]
            )
        )
        return devices

    def _devices_dict(self):
        self._initialize_connect()
        devices_dict = {
            dev_obj.description: [
                dev_obj.serial_number,
                dev_obj,
            ]
            for dev_obj in self.devices_list
        }
        return devices_dict

    def _initialize_connect(self):
        for device in self.devices_list:
            device.disconnect()
            device.connect()
            device.initialize()

    def disconnect_devices(self):
        for device in self.devices_list:
            device.disconnect()

    def get_devices(self, dev_id: str = None, dev_index: int = None):
        if dev_id:
            return [
                value[1]
                for value in self.devices_dict.values()
                if value[0] == dev_id
            ]

        if dev_index is not None:
            try:
                return self.devices_list[dev_index]
            except IndexError:
                return []
        return []

    def on_quit(self):
        for device in self.devices_list:
            device.disconnect()
