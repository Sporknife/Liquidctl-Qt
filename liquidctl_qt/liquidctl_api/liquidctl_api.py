from liquidctl.driver import find_liquidctl_devices


class LiquidctlApi:
    """Simple "API" for accessing devices"""

    __slots__ = ("devices", "devices_list", "devices_dict")

    def __init__(self):
        self.devices_list = self._devices_list()
        self.devices_dict = self._devices_dict()

    def _devices_list(self):
        return list(find_liquidctl_devices())

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

    def _in_str(self, in_str, checked_str):
        if isinstance(in_str, str) and in_str in checked_str:
            return True
        elif isinstance(in_str, tuple):
            for string in in_str:
                if string in checked_str:
                    return True
        return False

    def disconnect_devices(self):
        for device in self.devices_list:
            device.disconnect()

    def get_devices(self, dev_id: str = None, dev_index: int = None):
        if dev_id:
            return [
                value[1] for value in self.devices_dict.values() if
                value[0] == dev_id
            ]

        if dev_index is not None:
            try:
                return self.devices_list[dev_index]
            except IndexError:
                return []
        return []

    def to_dict(self, dev_status):
        dev_hw_info = {}
        curr_hw = ""
        for line in dev_status:
            line = list(line)
            if (
                ("Fan" in line[0])
                and ("Noise" or "Firmware" not in line[0])
                and (("—" not in str(line[1])) and "" == line[2])
            ):
                curr_hw, mode = line[0:2]
                dev_hw_info[curr_hw] = {}
                dev_hw_info[curr_hw]["Mode"] = {
                    "value": mode, "measurement": ""}
                continue
            if (
                curr_hw in line[0] and "Fan" in curr_hw
            ):  # if "Fan x" is in current line so it gets the info about it
                if self._in_str(("current", "speed", "voltage"), line[0]):
                    new_info = line[0].replace(curr_hw, "").strip().capitalize()
                    data, measurement = line[1:3]
                    dev_hw_info[curr_hw][new_info] = {
                        "value": round(data, 2),
                        "measurement": measurement.upper(),
                    }
        return dev_hw_info

    def on_quit(self):
        for device in self.devices_list:
            device.disconnect()
