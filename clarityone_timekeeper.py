# Clarity TimeKeeper - Keep track of your time. 
# ClarityOne: Clear, simple, trying to do one thing well.
# Copyright (c) 2024 MCN
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 3, as published by
# the Free Software Foundation. The full license is available at:
# https://www.gnu.org/licenses/gpl-3.0.html
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY REPRESENTATION OR WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. Indeed, the program may be worse than useless. 

# clarity_timekeeper.py

import sys
import os
import json
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QGridLayout,
    QInputDialog, QMessageBox, QVBoxLayout, QHBoxLayout, QScrollArea,
    QDialog, QListWidget, QLineEdit, QComboBox, QDateEdit, QRadioButton,
    QButtonGroup, QTextEdit
)
from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.QtGui import QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Constants
APP_NAME = "Clarity TimeKeeper"
DATA_DIR = os.path.expanduser(f"~/Library/Application Support/{APP_NAME}")
DATA_FILE = os.path.join(DATA_DIR, "data.json")
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
TIME_BLOCKS = [f"{hour:02d}:00-{(hour + 2)%24:02d}:00" for hour in range(0, 24, 2)]
PREDEFINED_ACTIVITIES = [
]

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

def get_monday(date):
    """Given a date, return the Monday of that week."""
    return date - timedelta(days=date.weekday())

def load_data():
    """Load activity data from the JSON file."""
    today = datetime.today()
    current_monday = get_monday(today).strftime("%Y-%m-%d")
    
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            QMessageBox.critical(None, "Error", "Data file is corrupted. Initializing new data.")
            data = {}
    else:
        data = {}
    
    # Initialize activities if not present
    if "activities" not in data:
        data["activities"] = PREDEFINED_ACTIVITIES.copy()
    
    # Initialize weeks if not present
    if "weeks" not in data:
        data["weeks"] = {}
    
    # Initialize current week if not present
    if current_monday not in data["weeks"]:
        data["weeks"][current_monday] = {day: {block: "" for block in TIME_BLOCKS} for day in DAYS_OF_WEEK}
    
    return data, current_monday

def save_data(data):
    """Save activity data to the JSON file."""
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to save data: {e}")

class ActivityManagerDialog(QDialog):
    """Dialog to manage activities: add, edit, delete."""
    def __init__(self, activities, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Activities")
        self.activities = activities
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # List Widget to display activities
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.activities)
        layout.addWidget(self.list_widget)
        
        # Buttons for Add, Edit, Delete
        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_activity)
        btn_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.edit_activity)
        btn_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_activity)
        btn_layout.addWidget(delete_btn)
        
        # Close Button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def add_activity(self):
        text, ok = QInputDialog.getText(self, "Add Activity", "Activity Name:")
        if ok and text.strip():
            activity = text.strip()
            if activity not in self.activities:
                self.activities.append(activity)
                self.list_widget.addItem(activity)
                QMessageBox.information(self, "Success", f"Added activity: {activity}")
            else:
                QMessageBox.warning(self, "Duplicate Activity", "This activity already exists.")
    
    def edit_activity(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an activity to edit.")
            return
        current_item = selected_items[0]
        current_text = current_item.text()
        new_text, ok = QInputDialog.getText(self, "Edit Activity", "Modify Activity Name:", text=current_text)
        if ok and new_text.strip():
            new_activity = new_text.strip()
            if new_activity in self.activities and new_activity != current_text:
                QMessageBox.warning(self, "Duplicate Activity", "This activity already exists.")
                return
            index = self.activities.index(current_text)
            self.activities[index] = new_activity
            current_item.setText(new_activity)
            QMessageBox.information(self, "Success", f"Activity updated to: {new_activity}")
    
    def delete_activity(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an activity to delete.")
            return
        current_item = selected_items[0]
        activity = current_item.text()
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to delete the activity '{activity}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.activities.remove(activity)
            self.list_widget.takeItem(self.list_widget.row(current_item))
            QMessageBox.information(self, "Deleted", f"Deleted activity: {activity}")

class ReportDialog(QDialog):
    """Dialog to generate and view reports."""
    def __init__(self, data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reports")
        self.data = data
        self.initUI()
    
    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Report Type Selection
        report_type_layout = QHBoxLayout()
        layout.addLayout(report_type_layout)
        
        self.daily_radio = QRadioButton("Daily")
        self.weekly_radio = QRadioButton("Weekly")
        self.monthly_radio = QRadioButton("Monthly")
        self.daily_radio.setChecked(True)
        
        self.report_group = QButtonGroup()
        self.report_group.addButton(self.daily_radio)
        self.report_group.addButton(self.weekly_radio)
        self.report_group.addButton(self.monthly_radio)
        
        report_type_layout.addWidget(self.daily_radio)
        report_type_layout.addWidget(self.weekly_radio)
        report_type_layout.addWidget(self.monthly_radio)
        
        # Date Selection
        date_layout = QHBoxLayout()
        layout.addLayout(date_layout)
        
        self.start_date_label = QLabel("Select Date:")
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        
        date_layout.addWidget(self.start_date_label)
        date_layout.addWidget(self.start_date_edit)
        
        # Generate Button
        generate_btn = QPushButton("Generate Report")
        generate_btn.clicked.connect(self.generate_report)
        layout.addWidget(generate_btn)
        
        # Report Display Area
        self.report_text = QTextEdit()
        self.report_text.setReadOnly(True)
        layout.addWidget(self.report_text)
        
        # Matplotlib Canvas for Charts
        self.figure = plt.figure(figsize=(5,4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
    
    def generate_report(self):
        report_type = "Daily" if self.daily_radio.isChecked() else "Weekly" if self.weekly_radio.isChecked() else "Monthly"
        selected_date = self.start_date_edit.date().toPyDate()
        
        if report_type == "Daily":
            self.generate_daily_report(selected_date)
        elif report_type == "Weekly":
            self.generate_weekly_report(selected_date)
        elif report_type == "Monthly":
            self.generate_monthly_report(selected_date)
    
    def generate_daily_report(self, date):
        """Generate a daily report for the selected date."""
        date_str = date.strftime("%Y-%m-%d")
        monday = get_monday(date)
        monday_str = monday.strftime("%Y-%m-%d")
        
        if monday_str not in self.data["weeks"]:
            QMessageBox.warning(self, "No Data", "No data available for the selected date.")
            return
        
        day_name = date.strftime("%A")
        if day_name not in DAYS_OF_WEEK:
            QMessageBox.warning(self, "Error", "Invalid day selected.")
            return
        
        day_data = self.data["weeks"][monday_str].get(day_name, {})
        
        activity_counts = {}
        for block, activity in day_data.items():
            if activity:
                activity_counts[activity] = activity_counts.get(activity, 0) + 2  # Each block is 2 hours
        
        # Display Report Text
        report = f"--- Daily Report for {day_name}, {date_str} ---\n\n"
        total_hours = 0
        for activity, hours in activity_counts.items():
            report += f"{activity}: {hours} hours\n"
            total_hours += hours
        report += f"\nTotal Logged Hours: {total_hours} hours"
        self.report_text.setText(report)
        
        # Generate Pie Chart
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if activity_counts:
            activities = list(activity_counts.keys())
            hours = list(activity_counts.values())
            ax.pie(hours, labels=activities, autopct='%1.1f%%', startangle=140)
            ax.set_title(f"Daily Activity Distribution\n{day_name}, {date_str}")
        else:
            ax.text(0.5, 0.5, "No activities logged.", horizontalalignment='center', verticalalignment='center')
            ax.axis('off')
        self.canvas.draw()
    
    def generate_weekly_report(self, date):
        """Generate a weekly report for the week containing the selected date."""
        monday = get_monday(date)
        monday_str = monday.strftime("%Y-%m-%d")
        
        if monday_str not in self.data["weeks"]:
            QMessageBox.warning(self, "No Data", "No data available for the selected week.")
            return
        
        week_data = self.data["weeks"][monday_str]
        
        activity_counts = {}
        for day, blocks in week_data.items():
            for block, activity in blocks.items():
                if activity:
                    activity_counts[activity] = activity_counts.get(activity, 0) + 2  # Each block is 2 hours
        
        # Display Report Text
        report = f"--- Weekly Report (Starting {monday_str}) ---\n\n"
        total_hours = 0
        for activity, hours in activity_counts.items():
            report += f"{activity}: {hours} hours\n"
            total_hours += hours
        report += f"\nTotal Logged Hours: {total_hours} hours"
        self.report_text.setText(report)
        
        # Generate Bar Chart
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if activity_counts:
            activities = list(activity_counts.keys())
            hours = list(activity_counts.values())
            ax.barh(activities, hours, color='skyblue')
            ax.set_xlabel('Hours')
            ax.set_title(f"Weekly Activity Distribution (Starting {monday_str})")
        else:
            ax.text(0.5, 0.5, "No activities logged.", horizontalalignment='center', verticalalignment='center')
            ax.axis('off')
        self.canvas.draw()
    
    def generate_monthly_report(self, date):
        """Generate a monthly report for the month containing the selected date."""
        year = date.year
        month = date.month
        first_day = datetime(year, month, 1)
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        last_day = next_month - timedelta(days=1)
        
        # Collect all weeks in the month
        weeks_in_month = []
        current_monday = get_monday(first_day)
        while current_monday <= last_day:
            monday_str = current_monday.strftime("%Y-%m-%d")
            if monday_str in self.data["weeks"]:
                weeks_in_month.append(self.data["weeks"][monday_str])
            current_monday += timedelta(weeks=1)
        
        if not weeks_in_month:
            QMessageBox.warning(self, "No Data", "No data available for the selected month.")
            return
        
        activity_counts = {}
        for week in weeks_in_month:
            for day, blocks in week.items():
                for block, activity in blocks.items():
                    if activity:
                        activity_counts[activity] = activity_counts.get(activity, 0) + 2  # Each block is 2 hours
        
        # Display Report Text
        report = f"--- Monthly Report for {first_day.strftime('%B %Y')} ---\n\n"
        total_hours = 0
        for activity, hours in activity_counts.items():
            report += f"{activity}: {hours} hours\n"
            total_hours += hours
        report += f"\nTotal Logged Hours: {total_hours} hours"
        self.report_text.setText(report)
        
        # Generate Pie Chart
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        if activity_counts:
            activities = list(activity_counts.keys())
            hours = list(activity_counts.values())
            ax.pie(hours, labels=activities, autopct='%1.1f%%', startangle=140)
            ax.set_title(f"Monthly Activity Distribution ({first_day.strftime('%B %Y')})")
        else:
            ax.text(0.5, 0.5, "No activities logged.", horizontalalignment='center', verticalalignment='center')
            ax.axis('off')
        self.canvas.draw()

class TimeKeeperApp(QWidget):
    """Main Application Window."""
    # Define default styles as class variables for maintainability
    DEFAULT_LABEL_STYLE = "background-color: black; color: white; border: 1px solid #ccc;"
    DEFAULT_BUTTON_STYLE = """
        QPushButton {
            border: 1px solid #ccc;
            text-align: left;
            padding: 5px;
            background-color: black;
            color: white;
        }
        QPushButton:hover {
            background-color: #333333;
        }
    """
  # Highlight styles for the current day

    HIGHLIGHT_LABEL_STYLE = "background-color: yellow; color: black; border: 1px solid #ccc;"
    HIGHLIGHT_BUTTON_STYLE = """
        QPushButton {
            background-color: yellow;
            border: 1px solid #ccc;
            text-align: left;
            padding: 5px;
            color: black;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #FFC107; /* Darker Yellow on Hover */
        }
    """

    # Non-highlight styles for other days
    NON_HIGHLIGHT_LABEL_STYLE = "background-color: black; color: white; border: 1px solid #ccc;"
    NON_HIGHLIGHT_BUTTON_STYLE = """
        QPushButton {
            border: 1px solid #ccc;
            text-align: left;
            padding: 5px;
            background-color: black;
            color: white;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #333333; /* Dark Gray on Hover */
        }
    """



    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.data, self.current_monday = load_data()
        self.initUI()
        self.check_week_transition()
    
    def initUI(self):
        # Set global Palatino font with size 14
        font = QFont("Palatino", 14)
        QApplication.instance().setFont(font)

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Top Buttons: Manage Activities, View Reports, Previous Week, Next Week
        top_btn_layout = QHBoxLayout()
        main_layout.addLayout(top_btn_layout)
        
        manage_activities_btn = QPushButton("Manage Activities")
        manage_activities_btn.clicked.connect(self.manage_activities)
        top_btn_layout.addWidget(manage_activities_btn)
        
        view_reports_btn = QPushButton("View Reports")
        view_reports_btn.clicked.connect(self.view_reports)
        top_btn_layout.addWidget(view_reports_btn)
        
        prev_week_btn = QPushButton("Previous Week")
        prev_week_btn.clicked.connect(self.previous_week)
        top_btn_layout.addWidget(prev_week_btn)
        
        next_week_btn = QPushButton("Next Week")
        next_week_btn.clicked.connect(self.next_week)
        top_btn_layout.addWidget(next_week_btn)
        
        # Scroll area for the gridCa
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)
        
        # Container widget for the grid
        container = QWidget()
        scroll.setWidget(container)
        
        # Grid layout
        self.grid = QGridLayout()
        container.setLayout(self.grid)
        
        # Initialize list to store day label references
        self.day_labels = []
        
        # Create header for days with dates
        current_monday_date = datetime.strptime(self.current_monday, "%Y-%m-%d")
        for col, day in enumerate(DAYS_OF_WEEK):
            # Calculate the date for the current day
            day_date = current_monday_date + timedelta(days=col)
            
            # Format the date as desired, e.g., "Monday, Oct 05"
            day_label_text = day_date.strftime("%A, %b %d")
            
            # Create and style the label
            label = QLabel(day_label_text)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(self.DEFAULT_LABEL_STYLE)
            
            # Add the label to the grid
            self.grid.addWidget(label, 0, col + 1)
            
            # Store reference to the label
            self.day_labels.append(label)
        
        # Create header for time blocks
        for row, time_block in enumerate(TIME_BLOCKS):
            label = QLabel(time_block)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet(self.DEFAULT_LABEL_STYLE)
            self.grid.addWidget(label, row + 1, 0)
        
        # Create grid of buttons
        self.buttons = {}
        for row, time_block in enumerate(TIME_BLOCKS):
            for col, day in enumerate(DAYS_OF_WEEK):
                activity = self.data["weeks"][self.current_monday][day][time_block]
                btn = QPushButton(activity if activity else "")
                btn.setStyleSheet(self.DEFAULT_BUTTON_STYLE)

                btn.setMinimumHeight(60)  # Set a minimum height to accommodate multiple lines
                btn.clicked.connect(lambda checked, d=day, t=time_block: self.log_activity(d, t))
                self.grid.addWidget(btn, row + 1, col + 1)
                self.buttons[(day, time_block)] = btn
        
        # Set stretch to make the grid responsive
        for col in range(len(DAYS_OF_WEEK) + 1):
            self.grid.setColumnStretch(col, 1)
        for row in range(len(TIME_BLOCKS) + 1):
            self.grid.setRowStretch(row, 1)
        
        # Initial UI refresh to ensure headers are updated
        self.refresh_ui()
    
    def update_day_headers(self):
        """Update the day headers with the correct dates based on the current week."""
        current_monday_date = datetime.strptime(self.current_monday, "%Y-%m-%d")
        for col, day_label in enumerate(self.day_labels):
            # Calculate the date for the current day
            day_date = current_monday_date + timedelta(days=col)
            
            # Format the date as desired, e.g., "Monday, Oct 05"
            day_label_text = day_date.strftime("%A, %b %d")
            
            # Update the label text
            day_label.setText(day_label_text)
    
    def refresh_ui(self):
        """Refresh the UI to display the selected week's data."""
        # Update day headers first
        self.update_day_headers()
        
        # Update button texts based on the selected week
        for (day, time_block), btn in self.buttons.items():
            activity = self.data["weeks"][self.current_monday][day][time_block]
            btn.setText(activity if activity else "")
            btn.setStyleSheet(self.DEFAULT_BUTTON_STYLE)
        
        # Highlight current day if the selected week is the current week
        selected_week_monday = datetime.strptime(self.current_monday, "%Y-%m-%d")
        current_week_monday = get_monday(datetime.today())
        if selected_week_monday == current_week_monday:
            today_weekday = datetime.today().strftime("%A")
            for col, day in enumerate(DAYS_OF_WEEK):
                if day == today_weekday:
                    for row in range(len(TIME_BLOCKS) + 1):
                        widget = self.grid.itemAtPosition(row, col + 1).widget()
                        if isinstance(widget, QLabel):
                            widget.setStyleSheet(self.HIGHLIGHT_LABEL_STYLE)
                        elif isinstance(widget, QPushButton):
                            widget.setStyleSheet(self.HIGHLIGHT_BUTTON_STYLE)
                else:
                    for row in range(len(TIME_BLOCKS) + 1):
                        widget = self.grid.itemAtPosition(row, col + 1).widget()
                        if isinstance(widget, QLabel):
                            widget.setStyleSheet(self.NON_HIGHLIGHT_LABEL_STYLE)
                        elif isinstance(widget, QPushButton):
                            widget.setStyleSheet(self.NON_HIGHLIGHT_BUTTON_STYLE)
        else:
            # For weeks that are not the current week, ensure all styles are non-highlighted
            for col, day in enumerate(DAYS_OF_WEEK):
                for row in range(len(TIME_BLOCKS) + 1):
                    widget = self.grid.itemAtPosition(row, col + 1).widget()
                    if isinstance(widget, QLabel):
                        widget.setStyleSheet(self.NON_HIGHLIGHT_LABEL_STYLE)
                    elif isinstance(widget, QPushButton):
                        widget.setStyleSheet(self.NON_HIGHLIGHT_BUTTON_STYLE)
    
    def manage_activities(self):
        """Open the Activity Manager Dialog."""
        dialog = ActivityManagerDialog(self.data["activities"], self)
        if dialog.exec_():
            # Update activities after managing
            self.data["activities"] = dialog.activities
            save_data(self.data)
    
    def view_reports(self):
        """Open the Report Dialog."""
        dialog = ReportDialog(self.data, self)
        dialog.exec_()
    
    def previous_week(self):
        """Navigate to the previous week."""
        new_monday = datetime.strptime(self.current_monday, "%Y-%m-%d") - timedelta(weeks=1)
        new_monday_str = new_monday.strftime("%Y-%m-%d")
        self.current_monday = new_monday_str
        if new_monday_str not in self.data["weeks"]:
            self.data["weeks"][new_monday_str] = {day: {block: "" for block in TIME_BLOCKS} for day in DAYS_OF_WEEK}
            save_data(self.data)
        self.refresh_ui()
    
    def next_week(self):
        """Navigate to the next week."""
        new_monday = datetime.strptime(self.current_monday, "%Y-%m-%d") + timedelta(weeks=1)
        new_monday_str = new_monday.strftime("%Y-%m-%d")
        self.current_monday = new_monday_str
        if new_monday_str not in self.data["weeks"]:
            self.data["weeks"][new_monday_str] = {day: {block: "" for block in TIME_BLOCKS} for day in DAYS_OF_WEEK}
            save_data(self.data)
        self.refresh_ui()
    
    def log_activity(self, day, time_block):
        """Prompt user to select an activity for the selected time block."""
        activities = self.data["activities"].copy()
        activities.append("Clear")  # Option to clear the activity
        
        activity, ok = QInputDialog.getItem(
            self, "Select Activity", f"Select activity for {day} {time_block}:", activities, 0, False
        )
        if ok:
            if activity == "Clear":
                self.data["weeks"][self.current_monday][day][time_block] = ""
            else:
                self.data["weeks"][self.current_monday][day][time_block] = activity
            self.buttons[(day, time_block)].setText(activity if activity != "Clear" else "")
            save_data(self.data)
            self.refresh_ui()  # Refresh UI to update any necessary styles
    
    def check_week_transition(self):
        """Check periodically if the week has changed and update data accordingly."""
        # Check every hour
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_week_if_needed)
        self.timer.start(60 * 60 * 1000)  # 1 hour in milliseconds
    
    def update_week_if_needed(self):
        """Update data and UI if a new week has started."""
        today = datetime.today()
        new_monday = get_monday(today).strftime("%Y-%m-%d")
        if new_monday != self.current_monday:
            self.current_monday = new_monday
            if new_monday not in self.data["weeks"]:
                # Initialize new week's data
                self.data["weeks"][new_monday] = {day: {block: "" for block in TIME_BLOCKS} for day in DAYS_OF_WEEK}
                save_data(self.data)
            # Refresh UI
            self.refresh_ui()

def main():
    app = QApplication(sys.argv)
    window = TimeKeeperApp()
    window.showMaximized()  # Start maximized for better visibility
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
