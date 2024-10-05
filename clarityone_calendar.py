# claritycalendar.py

import sys
import json
import uuid
from datetime import datetime
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QCalendarWidget, QListWidget, QListWidgetItem,
    QLineEdit, QTextEdit, QLabel, QComboBox, QMessageBox, QDialog,
    QFormLayout, QCheckBox, QDateEdit, QAction, QMenu, QTabWidget, QShortcut
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QColor, QBrush, QKeySequence, QFont


# ---------------------------
# Data Management Functions
# ---------------------------

def get_data_file_path():
    """
    Constructs the path to the data.json file within
    ~/Library/Application Support/ClarityCalendar/ on macOS
    or appropriate directory on other OS.
    """
    home = Path.home()
    if sys.platform.startswith('darwin'):
        app_support = home / 'Library' / 'Application Support' / 'ClarityCalendar'
    elif sys.platform.startswith('win'):
        app_support = home / 'AppData' / 'Roaming' / 'ClarityCalendar'
    else:
        app_support = home / '.config' / 'ClarityCalendar'
    app_support.mkdir(parents=True, exist_ok=True)
    data_file = app_support / 'data.json'
    return data_file

DATA_FILE = get_data_file_path()

def load_data():
    """
    Loads data from the JSON file.
    If the file does not exist or is corrupted, initializes empty data.
    Also migrates old event data from 'time' to 'start_time'.
    """
    if not DATA_FILE.exists():
        # Initialize with empty data
        return {"events": [], "tasks": []}
    with open(DATA_FILE, 'r') as f:
        try:
            data = json.load(f)
            # Ensure the keys exist
            if 'events' not in data:
                data['events'] = []
            if 'tasks' not in data:
                data['tasks'] = []
            # Migrate events from 'time' to 'start_time' if necessary
            for event in data['events']:
                if 'time' in event and 'start_time' not in event:
                    event['start_time'] = event.pop('time')
                if 'end_time' not in event:
                    event['end_time'] = None
            return data
        except json.JSONDecodeError:
            return {"events": [], "tasks": []}

def save_data(data):
    """
    Saves data to the JSON file with indentation for readability.
    """
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)


# ---------------------------
# Event Management Functions
# ---------------------------

def add_event(data, title, date, start_time, end_time, description, priority):
    """
    Adds a new event to the data.
    """
    event = {
        "id": str(uuid.uuid4()),
        "title": title,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,  # Can be None
        "description": description,
        "priority": priority
    }
    data['events'].append(event)
    save_data(data)
    return event

def edit_event(data, event_id, title, date, start_time, end_time, description, priority):
    """
    Edits an existing event identified by event_id.
    """
    for event in data['events']:
        if event['id'] == event_id:
            event['title'] = title
            event['date'] = date
            event['start_time'] = start_time
            event['end_time'] = end_time
            event['description'] = description
            event['priority'] = priority
            break
    save_data(data)

def delete_event(data, event_id):
    """
    Deletes an event identified by event_id.
    """
    data['events'] = [event for event in data['events'] if event['id'] != event_id]
    save_data(data)


# ---------------------------
# Task Management Functions
# ---------------------------

def add_task(data, title, deadline, priority):
    """
    Adds a new task to the data.
    """
    task = {
        "id": str(uuid.uuid4()),
        "title": title,
        "deadline": deadline,  # Can be None
        "priority": priority
    }
    data['tasks'].append(task)
    save_data(data)
    return task

def edit_task(data, task_id, title, deadline, priority):
    """
    Edits an existing task identified by task_id.
    """
    for task in data['tasks']:
        if task['id'] == task_id:
            task['title'] = title
            task['deadline'] = deadline  # Can be None
            task['priority'] = priority
            break
    save_data(data)

def delete_task(data, task_id):
    """
    Deletes a task identified by task_id.
    """
    data['tasks'] = [task for task in data['tasks'] if task['id'] != task_id]
    save_data(data)


# ---------------------------
# Dialogs for Adding/Editing
# ---------------------------

class AddEditEventDialog(QDialog):
    """
    Dialog for adding or editing an event.
    """
    def __init__(self, parent=None, event=None, preselected_date=None):
        super().__init__(parent)
        self.setWindowTitle("Add Event" if event is None else "Edit Event")
        self.event = event
        self.preselected_date = preselected_date
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout()

        self.title_edit = QLineEdit()
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_time_edit = QLineEdit()
        self.start_time_edit.setPlaceholderText("HHMM (e.g., 1000 for 10:00)")
        self.end_time_edit = QLineEdit()
        self.end_time_edit.setPlaceholderText("HHMM (optional, e.g., 1130 for 11:30)")
        self.description_edit = QTextEdit()
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["High", "Medium", "Low"])

        if self.event:
            self.title_edit.setText(self.event['title'])
            self.date_edit.setDate(QDate.fromString(self.event['date'], "yyyy-MM-dd"))
            self.start_time_edit.setText(self.event['start_time'].replace(":", ""))  # Remove colon for input
            if self.event.get('end_time'):
                self.end_time_edit.setText(self.event['end_time'].replace(":", ""))
            self.description_edit.setPlainText(self.event['description'])
            index = self.priority_combo.findText(self.event['priority'])
            if index >= 0:
                self.priority_combo.setCurrentIndex(index)
        else:
            if self.preselected_date:
                self.date_edit.setDate(self.preselected_date)
            else:
                self.date_edit.setDate(QDate.currentDate())

        layout.addRow("Title:", self.title_edit)
        layout.addRow("Date:", self.date_edit)
        layout.addRow("Start Time:", self.start_time_edit)
        layout.addRow("End Time (Optional):", self.end_time_edit)
        layout.addRow("Description:", self.description_edit)
        layout.addRow("Priority:", self.priority_combo)

        # Buttons
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_button)
        btn_layout.addWidget(self.cancel_button)

        layout.addRow(btn_layout)
        self.setLayout(layout)
    
    def get_data(self):
        """
        Retrieves the data entered by the user.
        """
        # Parse start time input
        start_time_input = self.start_time_edit.text().strip()
        if len(start_time_input) == 4 and start_time_input.isdigit():
            start_time_formatted = f"{start_time_input[:2]}:{start_time_input[2:]}"
        else:
            start_time_formatted = self.start_time_edit.text().strip()
        
        # Parse end time input
        end_time_input = self.end_time_edit.text().strip()
        if len(end_time_input) == 4 and end_time_input.isdigit():
            end_time_formatted = f"{end_time_input[:2]}:{end_time_input[2:]}"
        elif end_time_input == "":
            end_time_formatted = None
        else:
            end_time_formatted = end_time_input.strip()

        return {
            "title": self.title_edit.text(),
            "date": self.date_edit.date().toString("yyyy-MM-dd"),
            "start_time": start_time_formatted,
            "end_time": end_time_formatted,
            "description": self.description_edit.toPlainText(),
            "priority": self.priority_combo.currentText()
        }


class AddEditTaskDialog(QDialog):
    """
    Dialog for adding or editing a task.
    """
    def __init__(self, parent=None, task=None):
        super().__init__(parent)
        self.setWindowTitle("Add Task" if task is None else "Edit Task")
        self.task = task
        self.init_ui()
    
    def init_ui(self):
        layout = QFormLayout()

        self.title_edit = QLineEdit()
        self.deadline_edit = QDateEdit()
        self.deadline_edit.setCalendarPopup(True)
        self.deadline_edit.setDisplayFormat("yyyy-MM-dd")
        self.deadline_checkbox = QCheckBox("Set Deadline")
        self.deadline_edit.setEnabled(False)
        self.deadline_checkbox.stateChanged.connect(self.toggle_deadline)

        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["High", "Medium", "Low"])

        if self.task:
            self.title_edit.setText(self.task['title'])
            if self.task.get('deadline'):
                self.deadline_checkbox.setChecked(True)
                deadline_date = QDate.fromString(self.task['deadline'], "yyyy-MM-dd")
                self.deadline_edit.setDate(deadline_date if deadline_date.isValid() else QDate.currentDate())
                self.deadline_edit.setEnabled(True)
            index = self.priority_combo.findText(self.task['priority'])
            if index >= 0:
                self.priority_combo.setCurrentIndex(index)

        layout.addRow("Title:", self.title_edit)
        layout.addRow(self.deadline_checkbox, self.deadline_edit)
        layout.addRow("Priority:", self.priority_combo)

        # Buttons
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.save_button)
        btn_layout.addWidget(self.cancel_button)

        layout.addRow(btn_layout)
        self.setLayout(layout)
    
    def toggle_deadline(self, state):
        """
        Enables or disables the deadline edit based on the checkbox state.
        """
        self.deadline_edit.setEnabled(state == Qt.Checked)
    
    def get_data(self):
        """
        Retrieves the data entered by the user.
        """
        deadline = None
        if self.deadline_checkbox.isChecked():
            deadline_date = self.deadline_edit.date().toString("yyyy-MM-dd")
            deadline = deadline_date  # Only date, no time
        
        return {
            "title": self.title_edit.text(),
            "deadline": deadline,  # Can be None if not set
            "priority": self.priority_combo.currentText()
        }


# ---------------------------
# Main Application Window
# ---------------------------

class ClarityCalendar(QMainWindow):
    """
    Main application window for Clarity Calendar.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clarity Calendar")
        self.setGeometry(100, 100, 1300, 800)  # Increased width for better layout
        self.data = load_data()
        self.init_ui()
        self.setup_shortcuts()
        self.apply_palatino_font()
    
    def apply_palatino_font(self):
        """
        Applies Palatino font to the entire application.
        """
        font = QFont("Charter", 14)
        QApplication.instance().setFont(font)
    
    def init_ui(self):
        """
        Initializes the user interface components.
        """
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Left Panel: Calendar
        left_panel = QVBoxLayout()
        
        # Toolbar for Adding Events and Tasks
        toolbar = QHBoxLayout()
        
        # Add Event Button
        self.add_event_btn = QPushButton("Add Event")
        self.add_event_btn.clicked.connect(self.add_event)
        self.add_event_btn.setToolTip("Click to add a new event")
        toolbar.addWidget(self.add_event_btn)
        
        # Add Task Button
        self.add_task_btn = QPushButton("Add Task")
        self.add_task_btn.clicked.connect(self.add_task)
        self.add_task_btn.setToolTip("Click to add a new task")
        toolbar.addWidget(self.add_task_btn)
        
        toolbar.addStretch()
        
        left_panel.addLayout(toolbar)
        
        # Navigation Bar with Month and Year Dropdowns
        nav_layout = QHBoxLayout()
        
        # Accessing the default navigation bar components
        self.calendar = QCalendarWidget()
        self.calendar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.calendar.customContextMenuRequested.connect(self.calendar_context_menu)
        # Ensure the default navigation bar is visible
        self.calendar.setNavigationBarVisible(True)
        
        # Styling the Month and Year Dropdowns
        self.style_calendar_nav()

        nav_layout.addWidget(self.calendar)
        
        left_panel.addLayout(nav_layout)
        
        main_layout.addLayout(left_panel, 7)  # Ratio: 3 parts
        
        # Right Panel: Tabs for Events and To-Do List
        right_panel = QTabWidget()
        right_panel.setTabPosition(QTabWidget.North)
        
        # Events Tab
        self.events_tab = QWidget()
        events_layout = QVBoxLayout()
        
        # Search Bar for Events
        search_layout_events = QHBoxLayout()
        search_label_events = QLabel("Search Events:")
        self.search_events = QLineEdit()
        self.search_events.setPlaceholderText("Enter event title or description...")
        self.search_events.textChanged.connect(self.populate_all_events)
        search_layout_events.addWidget(search_label_events)
        search_layout_events.addWidget(self.search_events)
        events_layout.addLayout(search_layout_events)
        
        events_label = QLabel("All Events:")
        events_layout.addWidget(events_label)
        self.events_list = QListWidget()
        self.events_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.events_list.customContextMenuRequested.connect(self.event_context_menu)
        events_layout.addWidget(self.events_list)
        self.events_tab.setLayout(events_layout)
        right_panel.addTab(self.events_tab, "Events")
        
        # To-Do List Tab
        self.todo_tab = QWidget()
        todo_layout = QVBoxLayout()
        
        # Search Bar for Tasks
        search_layout_tasks = QHBoxLayout()
        search_label_tasks = QLabel("Search Tasks:")
        self.search_tasks = QLineEdit()
        self.search_tasks.setPlaceholderText("Enter task title...")
        self.search_tasks.textChanged.connect(self.populate_all_tasks)
        search_layout_tasks.addWidget(search_label_tasks)
        search_layout_tasks.addWidget(self.search_tasks)
        todo_layout.addLayout(search_layout_tasks)
        
        todo_label = QLabel("To-Do List:")
        todo_layout.addWidget(todo_label)
        self.todo_list = QListWidget()
        self.todo_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.todo_list.customContextMenuRequested.connect(self.todo_context_menu)
        todo_layout.addWidget(self.todo_list)
        self.todo_tab.setLayout(todo_layout)
        right_panel.addTab(self.todo_tab, "To-Do List")
        
        # Adding the right panel to the main layout
        main_layout.addWidget(right_panel, 5)  # Ratio: 2 parts
        
        # Menu Bar for Additional Features
        self.create_menu()
        
        self.refresh_views()
    
    def style_calendar_nav(self):
        """
        Styles the month and year dropdowns in the QCalendarWidget.
        """
        # Define the stylesheet for QComboBox
        combo_style = """
            QComboBox {
                border: 1px solid gray;
                border-radius: 4px;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
                background-color: #f0f0f0;
            }
            QComboBox:editable {
                background: white;
            }
            QComboBox:!editable, QComboBox::drop-down:editable {
                background: #f0f0f0;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: darkgray;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox::down-arrow {
                /* image: url(down_arrow.png); */ /* Removed to prevent issues */
                width: 10px;
                height: 10px;
            }
            QComboBox::down-arrow:on { /* shift the arrow when popup is open */
                top: 1px;
                left: 1px;
            }
        """
        # Apply the stylesheet to the QCalendarWidget's month and year comboboxes
        month_combo = self.calendar.findChild(QComboBox, "monthCombo")
        year_combo = self.calendar.findChild(QComboBox, "yearCombo")
        
        if month_combo:
            month_combo.setStyleSheet(combo_style)
        if year_combo:
            year_combo.setStyleSheet(combo_style)
    
    def create_menu(self):
        """
        Creates the menu bar with additional options.
        """
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("File")
        
        # Export Data
        export_action = QAction("Export Data", self)
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        # Import Data
        import_action = QAction("Import Data", self)
        import_action.triggered.connect(self.import_data)
        file_menu.addAction(import_action)
    
    def setup_shortcuts(self):
        """
        Sets up keyboard shortcuts for various actions.
        """
        # Add Event Shortcut: Command+E (macOS) / Ctrl+E (Windows/Linux)
        if sys.platform.startswith('darwin'):
            add_event_shortcut = QShortcut(QKeySequence("Meta+E"), self)
        else:
            add_event_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        add_event_shortcut.activated.connect(self.add_event)
        
        # Add Task Shortcut: Command+T (macOS) / Ctrl+T (Windows/Linux)
        if sys.platform.startswith('darwin'):
            add_task_shortcut = QShortcut(QKeySequence("Meta+T"), self)
        else:
            add_task_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        add_task_shortcut.activated.connect(self.add_task)
        
        # Reset Calendar View Shortcut: Command+G (macOS) / Ctrl+G (Windows/Linux)
        if sys.platform.startswith('darwin'):
            reset_calendar_shortcut = QShortcut(QKeySequence("Meta+G"), self)
        else:
            reset_calendar_shortcut = QShortcut(QKeySequence("Ctrl+G"), self)
        reset_calendar_shortcut.activated.connect(self.reset_calendar_view)
    
    def refresh_views(self):
        """
        Refreshes the calendar highlights, events list, and to-do list.
        """
        self.populate_all_events()
        self.populate_all_tasks()
        self.highlight_calendar()
        self.style_calendar_nav()  # Re-apply styles in case of view changes
    
    def populate_all_events(self):
        """
        Populates the events list with all events, sorted chronologically.
        Applies search filter if any.
        """
        self.events_list.clear()
        search_query = self.search_events.text().lower()
        # Sort events by date and start time
        sorted_events = sorted(
            self.data['events'],
            key=lambda e: (e['date'], e.get('start_time') or "00:00")
        )
        for event in sorted_events:
            if (search_query in event['title'].lower()) or (search_query in event['description'].lower()):
                end_time_display = f" - {event['end_time']}" if event.get('end_time') else ""
                item_text = f"{event['date']} {event.get('start_time', '00:00')}{end_time_display} - {event['title']} (Priority: {event['priority']})"
                item = QListWidgetItem(item_text)
                # Store event ID in the item for easy access
                item.setData(Qt.UserRole, event['id'])
                self.events_list.addItem(item)
    
    def populate_all_tasks(self):
        """
        Populates the to-do list with all tasks, sorted chronologically.
        Applies search filter if any.
        """
        self.todo_list.clear()
        search_query = self.search_tasks.text().lower()
        # Sort tasks by deadline; tasks without deadlines come last
        sorted_tasks = sorted(
            self.data['tasks'],
            key=lambda t: (t['deadline'] is None, t['deadline'])
        )
        for task in sorted_tasks:
            if search_query in task['title'].lower():
                if task['deadline']:
                    item_text = f"{task['deadline']} - {task['title']} (Priority: {task['priority']})"
                else:
                    item_text = f"No Deadline - {task['title']} (Priority: {task['priority']})"
                item = QListWidgetItem(item_text)
                # Store task ID in the item for easy access
                item.setData(Qt.UserRole, task['id'])
                self.todo_list.addItem(item)
    
    def highlight_calendar(self):
        """
        Highlights dates that have events with light blue color.
        """
        # Reset all date formats
        default_format = self.calendar.dateTextFormat(QDate())
        default_format.setBackground(Qt.white)
        self.calendar.setDateTextFormat(QDate(), default_format)
        
        # Collect all dates with events
        dates_with_events = {event['date'] for event in self.data['events']}
        
        # Highlight these dates
        for date_str in dates_with_events:
            date_obj = QDate.fromString(date_str, "yyyy-MM-dd")
            if date_obj.isValid():
                fmt = self.calendar.dateTextFormat(date_obj)
                fmt.setBackground(QBrush(QColor("#44a6c6")))  # Light Blue color
                self.calendar.setDateTextFormat(date_obj, fmt)
    
    def add_event(self, preselected_date=None):
        """
        Opens the Add Event dialog and adds the event if confirmed.
        If preselected_date is provided, it sets the date in the dialog.
        """
        if preselected_date:
            date = preselected_date
        else:
            date = self.calendar.selectedDate()
        dialog = AddEditEventDialog(self, preselected_date=date)
        if dialog.exec_() == QDialog.Accepted:
            event_data = dialog.get_data()
            # Basic validation
            try:
                datetime.strptime(event_data['date'], "%Y-%m-%d")
                datetime.strptime(event_data['start_time'], "%H:%M")
                if event_data['end_time']:
                    datetime.strptime(event_data['end_time'], "%H:%M")
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Please enter valid date and time formats.")
                return
            # Add event
            add_event(
                self.data,
                event_data['title'],
                event_data['date'],
                event_data['start_time'],
                event_data['end_time'],
                event_data['description'],
                event_data['priority']
            )
            self.refresh_views()
            QMessageBox.information(self, "Success", "Event added successfully.")
    
    def add_task(self):
        """
        Opens the Add Task dialog and adds the task if confirmed.
        """
        dialog = AddEditTaskDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            task_data = dialog.get_data()
            # Basic validation
            if task_data['deadline']:
                try:
                    datetime.strptime(task_data['deadline'], "%Y-%m-%d")
                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", "Please enter a valid deadline format (YYYY-MM-DD).")
                    return
            # Add task
            add_task(
                self.data,
                task_data['title'],
                task_data['deadline'],
                task_data['priority']
            )
            self.refresh_views()
            QMessageBox.information(self, "Success", "Task added successfully.")
    
    def edit_event(self, item):
        """
        Edits an event based on the selected item.
        """
        event_id = item.data(Qt.UserRole)
        event = next((e for e in self.data['events'] if e['id'] == event_id), None)
        if not event:
            QMessageBox.warning(self, "Event Not Found", "Selected event could not be found.")
            return
        dialog = AddEditEventDialog(self, event)
        if dialog.exec_() == QDialog.Accepted:
            event_data = dialog.get_data()
            # Basic validation
            try:
                datetime.strptime(event_data['date'], "%Y-%m-%d")
                datetime.strptime(event_data['start_time'], "%H:%M")
                if event_data['end_time']:
                    datetime.strptime(event_data['end_time'], "%H:%M")
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Please enter valid date and time formats.")
                return
            # Edit event
            edit_event(
                self.data,
                event_id,
                event_data['title'],
                event_data['date'],
                event_data['start_time'],
                event_data['end_time'],
                event_data['description'],
                event_data['priority']
            )
            self.refresh_views()
            QMessageBox.information(self, "Success", "Event edited successfully.")
    
    def delete_event(self, item):
        """
        Deletes an event based on the selected item.
        """
        event_id = item.data(Qt.UserRole)
        event = next((e for e in self.data['events'] if e['id'] == event_id), None)
        if not event:
            QMessageBox.warning(self, "Event Not Found", "Selected event could not be found.")
            return
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            f"Are you sure you want to delete the event '{event['title']}'?", 
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            delete_event(self.data, event_id)
            self.refresh_views()
            QMessageBox.information(self, "Success", "Event deleted successfully.")
    
    def edit_task(self, item):
        """
        Edits a task based on the selected item.
        """
        task_id = item.data(Qt.UserRole)
        task = next((t for t in self.data['tasks'] if t['id'] == task_id), None)
        if not task:
            QMessageBox.warning(self, "Task Not Found", "Selected task could not be found.")
            return
        dialog = AddEditTaskDialog(self, task)
        if dialog.exec_() == QDialog.Accepted:
            task_data = dialog.get_data()
            # Basic validation
            if task_data['deadline']:
                try:
                    datetime.strptime(task_data['deadline'], "%Y-%m-%d")
                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", "Please enter a valid deadline format (YYYY-MM-DD).")
                    return
            # Edit task
            edit_task(
                self.data,
                task_id,
                task_data['title'],
                task_data['deadline'],
                task_data['priority']
            )
            self.refresh_views()
            QMessageBox.information(self, "Success", "Task edited successfully.")
    
    def delete_task(self, item):
        """
        Deletes a task based on the selected item.
        """
        task_id = item.data(Qt.UserRole)
        task = next((t for t in self.data['tasks'] if t['id'] == task_id), None)
        if not task:
            QMessageBox.warning(self, "Task Not Found", "Selected task could not be found.")
            return
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            f"Are you sure you want to delete the task '{task['title']}'?", 
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            delete_task(self.data, task_id)
            self.refresh_views()
            QMessageBox.information(self, "Success", "Task deleted successfully.")
    
    def event_context_menu(self, position):
        """
        Creates a context menu for events.
        """
        item = self.events_list.itemAt(position)
        if item:
            menu = QMenu()
            edit_action = QAction("Edit Event", self)
            delete_action = QAction("Delete Event", self)
            menu.addAction(edit_action)
            menu.addAction(delete_action)
            action = menu.exec_(self.events_list.mapToGlobal(position))
            if action == edit_action:
                self.edit_event(item)
            elif action == delete_action:
                self.delete_event(item)
    
    def todo_context_menu(self, position):
        """
        Creates a context menu for tasks.
        """
        item = self.todo_list.itemAt(position)
        if item:
            menu = QMenu()
            edit_action = QAction("Edit Task", self)
            delete_action = QAction("Delete Task", self)
            menu.addAction(edit_action)
            menu.addAction(delete_action)
            action = menu.exec_(self.todo_list.mapToGlobal(position))
            if action == edit_action:
                self.edit_task(item)
            elif action == delete_action:
                self.delete_task(item)
    
    def calendar_context_menu(self, position):
        """
        Creates a context menu for the calendar to add events directly to a date.
        """
        date = self.calendar.selectedDate()
        menu = QMenu()
        add_event_action = QAction("Add Event to Selected Date", self)
        add_event_action.triggered.connect(lambda: self.add_event(preselected_date=date))
        menu.addAction(add_event_action)
        menu.exec_(self.calendar.mapToGlobal(position))
    
    def reset_calendar_view(self):
        """
        Resets the calendar to today's date.
        """
        today = QDate.currentDate()
        self.calendar.setSelectedDate(today)
        self.calendar.showSelectedDate()
    
    def export_data(self):
        """
        Exports the current data to a user-specified JSON file.
        """
        from PyQt5.QtWidgets import QFileDialog
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Data", "", "JSON Files (*.json)", options=options)
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    json.dump(self.data, f, indent=4)
                QMessageBox.information(self, "Export Successful", f"Data exported to {file_path}")
            except Exception as e:
                QMessageBox.warning(self, "Export Failed", f"An error occurred: {str(e)}")
    
    def import_data(self):
        """
        Imports data from a user-specified JSON file.
        """
        from PyQt5.QtWidgets import QFileDialog
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Data", "", "JSON Files (*.json)", options=options)
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    imported_data = json.load(f)
                # Migrate imported data if necessary
                if 'events' in imported_data and 'tasks' in imported_data:
                    for event in imported_data['events']:
                        if 'time' in event and 'start_time' not in event:
                            event['start_time'] = event.pop('time')
                        if 'end_time' not in event:
                            event['end_time'] = None
                    self.data = imported_data
                    save_data(self.data)
                    self.refresh_views()
                    QMessageBox.information(self, "Import Successful", f"Data imported from {file_path}")
                else:
                    QMessageBox.warning(self, "Import Failed", "Invalid data format.")
            except Exception as e:
                QMessageBox.warning(self, "Import Failed", f"An error occurred: {str(e)}")


# ---------------------------
# Main Execution
# ---------------------------

def main():
    """
    Main function to run the Clarity Calendar application.
    """
    app = QApplication(sys.argv)
    
    # Set application-wide font to Palatino
    font = QFont("Charter", 14)
    app.setFont(font)
    
    window = ClarityCalendar()
    window.show()
    print("Main window displayed.")
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
