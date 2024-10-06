
# Clarity Apps - Project Intro

## Table of Contents
- [Introduction](#introduction)
- [App Descriptions](#app-descriptions)
	  - [Clarity Wiki](#clarity-wiki)
	  - [Clarity Explorer](#clarity-explorer)
	  - [Clarity Editor](#clarity-editor)
	  - [Clarity Clips](#clarity-clips)
	  - [Clarity Calendar](#clarity-calendar)
	  - [Clarity TimeKeeper](#clarity-timekeeper)
	  - [Clarity Finances](#clarity-finances)
- [Installation](#installation)
	  - [Download links](#download-links)	
	  - [Download Bundled App version](#download-bundled-app-version)
	  - [Bypassing macOS Gatekeeper warnings](#bypassing-macos-gatekeeper-warnings)
	  - [Building from Source](#building-from-source)
    	- [Download the source code](#download-the-source-code)
    	- [Set up Virtual Environment](#set-up-virtual-environment)
    	- [Install Dependencies](#install-dependencies)
    	- [Running the apps](#running-the-apps)
    	- [Creating the .app version with PyInstaller](#creating-the-app-version-with-pyinstaller)
- [Usage](#usage)
	  - [Clarity Wiki](#clarity-wiki-1)
	  - [Clarity Explorer](#clarity-explorer-1)
	  - [Clarity Editor](#clarity-editor-1)
	  - [Clarity Clips](#clarity-clips-1)
	  - [Clarity Calendar](#clarity-calendar-1)
	  - [Clarity TimeKeeper](#clarity-timekeeper-1)
	  - [Clarity Finances](#clarity-finances-1)
- [Roadmap for future development](#roadmap-for-future-development)
	  - [Planned features](#planned-features)
	  - [Contributions for future developments](#contributions-for-future-developments)
- [License](#license)


## Introduction

ClarityOne is a project focused on developing small, simple, and useful apps with a clear philosophy: **do one thing well**. The aim is to offer polished and efficient tools that address specific user needs without unnecessary complexity.

While these apps  are labeled as v1, they are still in the prototype stage. The goal is to release refined versions (v2) by the end of this year. 

These apps are intended to be functional ***only in a macOS environment***. Presently, there is no plan to develop Linux or Windows versions nor is any mobile version on the cards, but interested users are welcome to contribute if they would like to do so. The main feature to watch out for is system tray interactions in Clipboard, and also storage locations (presently, the apps use local storage in appropriate folders in ~/Library/Application Support, which is a macOS specific location.
Each app is designed with simplicity in mind and is described briefly below.

## App Descriptions

Basic descriptions are provided below; more detailed usage guidelines are provided subsequently in this document.

### Clarity Wiki

A minimalist personal knowledge base and note-taking application. It allows users to create and manage notes in Markdown format, with a live preview. It supports a multi-wiki system for organizing notes, includes a powerful tag management system, and exports notes in HTML or PDF.

### Clarity Explorer

A file management system that organizes files by project views, regardless of physical file locations. It supports file previews, tag-based file filtering, and project-specific file management. 

### Clarity Editor

A distraction-free text editor focused on writing, with essential formatting tools and support for multiple formats (HTML, Markdown, PDF, plain text, etc.). It provides a clean interface for users who value simplicity in their writing environment.

### Clarity Clips

A clipboard manager that records clipboard entries, allowing users to search, tag, and organize clipboard history. It supports exporting the clipboard history for backup or external use.

### Clarity Calendar

A simple, distraction-free calendar app for managing events and tasks. It supports reminders, priority levels for tasks, and export functionality in JSON format.

### Clarity TimeKeeper

A companion app to Calendar (but which functions as a standalone app), TimeKeeper is time-tracking app that logs activities in a weekly grid layout, allowing users to monitor and optimize their daily activities. It features reporting tools for generating daily, weekly, or monthly summaries. This is meant especially for users to track how well their own time-blocking techniques are working for them.

### Clarity Finances

A financial management app meant for freelancers or small businesses, that helps users track expenses, receipts, and memos. It provides features like customizable categories, yearly summaries, and export options in JSON and CSV formats

## Installation

### Download links

Specific download lins for each app are below, this downloads a .zip, which you will have to extract to get access to the .app; the .app can be moved to the Applications folder on your system:


- Clarity Wiki: [zip](https://drive.proton.me/urls/HDM470K63R#5bCR9KGyWyNX) OR [source code](https://github.com/mnani87/clarity/blob/main/clarityone_wiki.py) || [icon file](https://github.com/mnani87/clarity/blob/main/icon_wiki.icns) || [requirements](https://github.com/mnani87/clarity/blob/main/requirements-wiki.txt)
- Clarity Explorer [zip](https://drive.proton.me/urls/WMP0T9HBF8#YvPvp4NDq4Hh) OR [source code](https://github.com/mnani87/clarity/blob/main/clarityone_explorer.py) || [icon file](https://github.com/mnani87/clarity/blob/main/icon_explorer.icns) || [requirements](https://github.com/mnani87/clarity/blob/main/requirements-explorer.txt)
- Clarity Editor [zip](https://drive.proton.me/urls/DBMV0M2E9C#IfPoDYHeYx7R) OR [source code](https://github.com/mnani87/clarity/blob/main/clarityone_editor.py) || [icon file](https://github.com/mnani87/clarity/blob/main/icon_editor.icns) || [requirements](https://github.com/mnani87/clarity/blob/main/requirements-editor.txt)
- Clarity Clips [zip](https://drive.proton.me/urls/RQ6JNTREMC#uU8CzQhReFyY) OR [source code](https://github.com/mnani87/clarity/blob/main/clarityone_clips.py) || [icon file](https://github.com/mnani87/clarity/blob/main/icon_clips.icns) || [requirements](https://github.com/mnani87/clarity/blob/main/requirements-clips.txt)
- Clarity Calendar [zip](https://drive.proton.me/urls/J81HNVDXPC#wDaZlKLkUCor) OR [source code](https://github.com/mnani87/clarity/blob/main/clarityone_calendar.py) || [icon file](https://github.com/mnani87/clarity/blob/main/icon_calendar.icns) || [requirements](https://github.com/mnani87/clarity/blob/main/requirements-calendar.txt)
- Clarity Timekeeper [zip](https://drive.proton.me/urls/TDPPWKAXM8#kCGA3EXwCmyO) OR [source code](https://github.com/mnani87/clarity/blob/main/clarityone_timekeeper.py) || [icon file](https://github.com/mnani87/clarity/blob/main/icon_timekeeper.icns) || [requirements](https://github.com/mnani87/clarity/blob/main/requirements-timekeeper.txt)
- Clarity Finances [zip](https://drive.proton.me/urls/6XDVH81ZFW#YJtgiFh57rSJ) OR [source code](https://github.com/mnani87/clarity/blob/main/clarityone_finances.py) || [icon file](https://github.com/mnani87/clarity/blob/main/icon_finances.icns) || [requirements](https://github.com/mnani87/clarity/blob/main/requirements-finances.txt)

### Download Bundled App version

You can download bundled .app versions for some of the apps directly from the [ClarityOne website](https://mnani87.github.io/mnanihome/clarityone.html) or from the zip links above.

### Bypassing macOS Gatekeeper warnings

If you have downloaded the zip and unzipped it to reveal the app, when you try to open the app for the first time, macOS may prevent it from opening because it is from an unidentified developer. 

To open the app, use control-click or right-click, choose open. A warning dialog will pop up stating that the app is from an unidentified developer (me!) but you can open it anyway. 

If this does not work, open System Preferences (by clicking the Apple icon in the top left of your screen and choosing System Preferences). Click on "Security & Privacy", and choose to Allow Apps from Unidentified Developers. If this doesn't work, build from source as described below.




### Building from Source

Detailed instructions are given here, but for further guidance you can reach out to me or simply ask ChatGPT or Perplexity. You will need to use the Terminal (Cmd+Space on your Mac will open the Spotlight Search, and if you simply type `Terminal` in the search box, you will be able to open the Terminal app. You can then navigate to the folder where you want to download these apps by using the `cd` command in your Terminal. Alternatively, you can create a folder (say, you can create a 'Clarity' folder on your file system; then right-click and select 'New Terminal at Folder' from the menu (if not directly visible, it might be under 'services' after in the menu which opens on right clicking).

Once you are in the folder, you can make separate folders for all the apps (or the ones you specifically want to download): for example `mkdir wiki explorer editor clips calendar timekeeper finances` will create all these folders.

####  Download the source code

To build the apps from source, you can clone the repository using the following command: in your terminal

```

	git clone https://github.com/mnani87/clarity.git

```

If you are comfortable with git and github, you will know what to do; but for those who want to build from source without using git or Github, follow the instructions here.

You can download the source code and icon files as well as the requirements files for each app from the links given above, and then copy the downloaded files from the Downloads folder to the relevant folder where you are building the app. 

Then move to the relevant folder in your terminal with the command `cd [directory name]`; for instance `cd wiki` or `cd clips`.

The remaining instructions assume, for illustration, that you are building Clarity Clips; but in principle, all  these Clarity apps can be built using the same suggestions by changing the name from clips to whatever app you are building.


#### Set up Virtual Environment

Once you are in the folder of where you are building the app (eg., after runninng `cd clips` in Terminal) It is recommended to use a Python virtual environment to avoid package conflicts:

```

	python3 -m venv venv

```

Once this command runs, activate the virtual environment with:

```

	source venv/bin/activate

```

#### Install Dependencies

Check the source code or the relevant requirements file for what all is required to be imported. Install those with:

```

	pip install -r [requirements-appname].txt

```

Replace [requirements-appname] with the actual name of the requirements file; so, for Clips, run:

```

	pip install -r requirements-clips.txt

```


#### Running the apps

To run any app, execute the following command (replace [appname] with the actual source code file name):

```

	python clarityone_[appname].py

```

So, for running Clarity Clips, you will have to run:

```

	python clarityone_clips.py

```

#### Creating the .app version with PyInstaller

If you want to create a standalone .app version of an app, first install Pyinstaller:

```

	pip install pyinstaller

```


Then you can create an app version, by running:

```
	pyinstaller --onefile --windowed --icon=icon_[appname].icns clarityone_[appname].py

```

Replace `[appname]` with the actual python file name for the particular app; so, for Clips, you can run:

```

	pyinstaller --onefile --windowed --icon=icon_clips.icns clarityone_clips.py
```

This will then create `build` and `dist` sub-folders; and in the `dist` folder, you will have two files; one of which will be the .app version which you can move to your Applications folder as well.



## Usage

You can run the app by simply double clicking the .app file (or the applicaiton from your Applications folder, or by using spotlight search to search for the app and open it. Usage notes for how you can use each app are given below.

### Clarity Wiki

A [User Guide is available here](https://mnani87.github.io/mnanihome/guide-wiki.html), which includes a brief overview of the features, keyboard shortcuts, usage and troubleshooting tips etc.

### Clarity Explorer

A [User Guide is available here](https://mnani87.github.io/mnanihome/guide-explorer.html), which includes a brief overview of the features, keyboard shortcuts, usage and troubleshooting tips etc.

### Clarity Editor

A [User Guide is available here](https://mnani87.github.io/mnanihome/guide-editor.html), which includes a brief overview of the features, keyboard shortcuts, usage and troubleshooting tips etc.

### Clarity Clips

A [User Guide is available here](https://mnani87.github.io/mnanihome/guide-clips.html), which includes a brief overview of the features, keyboard shortcuts, usage and troubleshooting tips etc.

### Clarity Calendar

A [User Guide is available here](https://mnani87.github.io/mnanihome/guide-calendar.html), which includes a brief overview of the features, keyboard shortcuts, usage and troubleshooting tips etc.

### Clarity TimeKeeper

Simple log activities by clicking on a box for the relevant date and time. The 'Manage Activities' button will let you edit the list of activities as per your needs. 

### Clarity Finances

The buttons are fairly clear; for editing or deleting an entry you have logged, right click on the entry (known bug - if you right click even if there is no entry, it opens the edit dialog box, but the app will crash - so make sure that there is an entry that you are right-clicking for editing or deleting!). Reports can be exported in json or in csv, and csv can be read by spreadsheet programs such as Excel.

## Roadmap for future development

### Planned features

- Adding a dark mode across all apps.
- Integrating the apps for seamless usage (perhaps through an overarching dashboard or launchpad) while preserving their standalone nature as well.
- Support for drag and drop functionality, especially in Calendar
- Support for more fonts and better rendering and export to pdf, md and html in Editor
- Support for better export in Finances, to ensure easy compatability with accounting software
- Better file previewing in Explorer

### Contributions for future developments

We welcome contributions! Here's how you can get involved:

- *Bug Reports:* Open an issue on GitHub with steps to reproduce the problem.
- *Feature Requests:* Submit your ideas, ensuring they align with the minimalist philosophy.
- *Code Contribution:* Fork the repository, make changes in a new branch, and submit a pull request.
- *Testing:* Help test beta releases and provide feedback.

## License

ClarityOne is licensed under the GNU General Public License v3.0. You are free to use, modify, and redistribute the software under this license.
You can read the full license here: [GNU GPL v3.0](https://www.gnu.org/licenses/gpl-3.0.html)



