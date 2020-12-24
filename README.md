# Liquidctl-Qt
**A Qt GUI for [liquidctl](https://github.com/jonasmalacofilho/liquidctl).**

## Current state
- Rewriting the entire backend which will in turn make the app more stable and easier to use.
- Feel free to add (led, fan) controllers keys to [this](https://github.com/Sporknife/Liquidctl-Qt/blob/master/devices_info/controllers.json) file.
- Device info templates can be found [here](https://github.com/Sporknife/Liquidctl-Qt/blob/master/devices.md)

## Dependencies
- I linked ArchLinux packages because i had problems with installing them with python package manager (pip).
* [Liquidctl](https://github.com/jonasmalacofilho/liquidctl) (and it's dependencies), -[ArchLinux package](https://archlinux.org/packages/community/any/liquidctl/).
* [Python3](https://www.python.org/), -[ArchLinux package](https://archlinux.org/packages/extra/x86_64/python/)
* Python packages (if your on Linux try installing them with the distro package manager) 
	- [PyQt5](https://pypi.org/project/PyQt5/), -[ArchLinux package](https://archlinux.org/packages/extra/x86_64/python-pyqt5/).

## App usage
- Describes how the app works and how you can use it.
### Profile naming rules
- Allowed characters: all letters and numbers + -, _
- Max name length: 20 characters
- Min name langth: 1 character
