# Liquidctl-Qt
**A Qt GUI for [liquidctl](https://github.com/jonasmalacofilho/liquidctl).**

## Current state
> Currently i am working on profile widget. Fan widget are added and info updated.

## Current status
* [ ] Backend
	- [x] Simple liquidctl api for the application
	- [ ] Legacy devices
	- [ ] Utils (making it save & load profiles properly)

* [ ] Complete widgets
	- [x] Main window
	- [x] Fan widget (those that are in the list)
		- [x] The one in the list with information
		* [ ] Fan profile changer/editor
			- [x] Dialog
			* [ ] Widget
				- [x] ProfileModeChooser - choose profile and mode (static/profile)
				- [x] Steps viewer (QTableView) - view steps ordered by temp.
				- [x] Step editor - add/edit/delete a step in steps viewer
				- [ ] Profile controls - save/delete or reset settings (reset settings to current profile)
	- [ ] Led widget

* [ ] App working
	- [x] App acutally works and displays widgets properly, etc.
	- [ ] Has all the features I and others want ? *nope! half way there !*

## Dependencies
* [Liquidctl](https://github.com/jonasmalacofilho/liquidctl) (and it's dependencies)
* Python3
* Python packages
	- [PyQt5](https://pypi.org/project/PyQt5/)
	- [notify-send](https://pypi.org/project/notify-send/)
