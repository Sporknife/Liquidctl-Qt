# Liquidctl-Qt
**A Qt GUI for [liquidctl](https://github.com/jonasmalacofilho/liquidctl).**

## Current state
- Rewriting the entire backend.
- Feel free to add (led, fan) controllers keys to [this](https://github.com/Sporknife/Liquidctl-Qt/blob/master/devices_info/controllers.json) file. Template for (led, fan) controllers [here](https://github.com/Sporknife/Liquidctl-Qt/blob/master/devices.md#fanled-controllers). 

## Dependencies
* [Liquidctl](https://github.com/jonasmalacofilho/liquidctl) (and it's dependencies)
* Python3
* Python packages (if your on Linux try installing them via the package manager) 
	- [PyQt5](https://pypi.org/project/PyQt5/)

## App usage
- Describes how the app works and how you can use it.
### Profile naming rules
- Allowed characters: all letters and numbers + -, _
- Max name length: 20 characters
- Min name langth: 1 character
