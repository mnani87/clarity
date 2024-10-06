# clarity_timekeeper.py

import sys
import os
import json
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QGridLayout,
    QInputDialog, QMessageBox, QVBoxLayout, QHBoxLayout, QScrollArea,
    QDialog, QTextEdit, QMenu, QFileDialog, QSplitter, QPlainTextEdit, QTextBrowser
)
from PyQt5.QtCore import Qt, QTimer, QDate, QEvent
from PyQt5.QtGui import QFont
import markdown2

# Constants
APP_NAME = "Clarity TimeKeeper"
DATA_DIR = os.path.expanduser(f"~/Library/Application Support/{APP_NAME}")
DATA_FILE = os.path.join(DATA_DIR, "data.json")
DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
TIME_BLOCKS = [f"{hour:02d}:00-{(hour + 1)%24:02d}:00" for hour in range(0, 24)]

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

class TimeKeeperApp(QWidget):
    """Main Application Window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.data, self.current_monday = load_data()
        self.initUI()
        self.check_week_transition()

    def initUI(self):
        # Set global font with size 14
        font = QFont("Charter", 14)
        QApplication.instance().setFont(font)

        # Main layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Top Buttons: Previous Week, Next Week, Export Data
        top_btn_layout = QHBoxLayout()
        main_layout.addLayout(top_btn_layout)
        
        prev_week_btn = QPushButton("Previous Week")
        prev_week_btn.clicked.connect(self.previous_week)
        top_btn_layout.addWidget(prev_week_btn)
        
        next_week_btn = QPushButton("Next Week")
        next_week_btn.clicked.connect(self.next_week)
        top_btn_layout.addWidget(next_week_btn)
        
        export_btn = QPushButton("Export Data")
        export_btn.clicked.connect(self.export_data)
        top_btn_layout.addWidget(export_btn)
        
        # Create main horizontal splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)

        # Left side: Calendar/grid area (70% width)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_splitter.addWidget(scroll)
        
        container = QWidget()
        scroll.setWidget(container)
        
        self.grid = QGridLayout()
        container.setLayout(self.grid)
        
        # Initialize list to store day label references
        self.day_labels = []
        current_monday_date = datetime.strptime(self.current_monday, "%Y-%m-%d")
        for col, day in enumerate(DAYS_OF_WEEK):
            day_date = current_monday_date + timedelta(days=col)
            day_label_text = day_date.strftime("%A, %b %d")
            label = QLabel(day_label_text)
            label.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(label, 0, col + 1)
            self.day_labels.append(label)

        for row, time_block in enumerate(TIME_BLOCKS):
            label = QLabel(time_block)
            label.setAlignment(Qt.AlignCenter)
            self.grid.addWidget(label, row + 1, 0)
        
        self.buttons = {}
        for row, time_block in enumerate(TIME_BLOCKS):
            for col, day in enumerate(DAYS_OF_WEEK):
                activity = self.data["weeks"][self.current_monday][day][time_block]
                btn = QPushButton(activity if activity else "")
                btn.setMinimumHeight(60)
                btn.installEventFilter(self)
                btn.setContextMenuPolicy(Qt.CustomContextMenu)
                btn.customContextMenuRequested.connect(self.show_context_menu)
                btn.clicked.connect(lambda checked, b=btn: self.display_note_for_button(b))
                self.grid.addWidget(btn, row + 1, col + 1)
                self.buttons[(day, time_block)] = btn

        # Right side: Split into top half (notes) and bottom half (deep work hours)
        right_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(right_splitter)

        # Top half: Notes display
        self.side_panel = QTextEdit()
        self.side_panel.setReadOnly(True)
        right_splitter.addWidget(self.side_panel)

        # Bottom half: Deep work stats
        self.sidebar = QLabel(self.generate_deep_work_stats())
        right_splitter.addWidget(self.sidebar)

        # Set the sizes for both splitters (left 70%, right 30%; right top half 50%, bottom half 50%)
        main_splitter.setSizes([1000, 400])  # 70% for left, 30% for right
        right_splitter.setSizes([300, 100])  # Split the right side evenly between notes and deep work stats

        self.refresh_ui()
   
    def update_day_headers(self):
        """Update the day headers with the correct dates based on the current week."""
        current_monday_date = datetime.strptime(self.current_monday, "%Y-%m-%d")
        for col, day_label in enumerate(self.day_labels):
            day_date = current_monday_date + timedelta(days=col)
            day_label_text = day_date.strftime("%A, %b %d")
            day_label.setText(day_label_text)
    
    def refresh_ui(self):
        """Refresh the UI to display the selected week's data."""
        self.update_day_headers()
        
        for (day, time_block), btn in self.buttons.items():
            activity = self.data["weeks"][self.current_monday][day][time_block]
            btn.setText(activity if activity else "")
            if activity == "Deep Work":
                btn.setStyleSheet("background-color: green;")
            else:
                btn.setStyleSheet("")
        
        self.sidebar.setText(self.generate_deep_work_stats())
    
    def generate_deep_work_stats(self):
        """Generate statistics for deep work hours in the current and past week/month."""
        current_week_hours = self.calculate_deep_work_hours(self.current_monday)
        past_week_hours = self.calculate_deep_work_hours((datetime.strptime(self.current_monday, "%Y-%m-%d") - timedelta(weeks=1)).strftime("%Y-%m-%d"))
        current_month_hours = self.calculate_deep_work_hours_month(datetime.today().strftime("%Y-%m-%d"))
        past_month_hours = self.calculate_deep_work_hours_month((datetime.today() - timedelta(weeks=4)).strftime("%Y-%m-%d"))
        
        stats = (f"Deep Work Hours:\n\n"
                 f"Current Week: {current_week_hours} hours\n"
                 f"Past Week: {past_week_hours} hours\n"
                 f"Current Month: {current_month_hours} hours\n"
                 f"Past Month: {past_month_hours} hours")
        return stats
    
    def calculate_deep_work_hours(self, monday):
        """Calculate deep work hours for a given week."""
        if monday not in self.data["weeks"]:
            return 0
        
        week_data = self.data["weeks"][monday]
        deep_work_hours = 0
        for day in DAYS_OF_WEEK:
            for block in TIME_BLOCKS:
                if week_data[day][block] == "Deep Work":
                    deep_work_hours += 1
        return deep_work_hours
    
    def calculate_deep_work_hours_month(self, date):
        """Calculate deep work hours for a given month."""
        year = datetime.strptime(date, "%Y-%m-%d").year
        month = datetime.strptime(date, "%Y-%m-%d").month
        deep_work_hours = 0
        
        for week in self.data["weeks"]:
            week_date = datetime.strptime(week, "%Y-%m-%d")
            if week_date.year == year and week_date.month == month:
                deep_work_hours += self.calculate_deep_work_hours(week)
        
        return deep_work_hours
    
    def eventFilter(self, obj, event):
        """Handle double-click events to mark a block as deep work."""
        if event.type() == QEvent.MouseButtonDblClick and isinstance(obj, QPushButton):
            self.mark_as_deep_work(obj)
        return super().eventFilter(obj, event)
    
    def mark_as_deep_work(self, button):
        """Mark a time block as deep work."""
        day, time_block = self.get_day_time_from_button(button)
        self.data["weeks"][self.current_monday][day][time_block] = "Deep Work"
        button.setStyleSheet("background-color: green;")
        save_data(self.data)
        self.refresh_ui()
    
    def show_context_menu(self, pos):
        """Show right-click context menu for adding, editing, or deleting notes, and undoing deep work."""
        menu = QMenu(self)
        add_note_action = menu.addAction("Add Note")
        edit_note_action = menu.addAction("Edit Note")
        delete_note_action = menu.addAction("Delete Note")
        undo_deep_work_action = menu.addAction("Undo Deep Work")
        
        clicked_button = self.sender()
        
        add_note_action.triggered.connect(lambda: self.add_note_for_button(clicked_button))
        edit_note_action.triggered.connect(lambda: self.edit_note_for_button(clicked_button))
        delete_note_action.triggered.connect(lambda: self.delete_note_for_button(clicked_button))
        undo_deep_work_action.triggered.connect(lambda: self.undo_deep_work(clicked_button))
        
        menu.exec_(self.mapToGlobal(pos))
    
    def add_note_for_button(self, button):
        """Add a note for a selected block with Markdown support."""
        day, time_block = self.get_day_time_from_button(button)

        # Create a custom dialog for multi-line text input
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Note")
        dialog.resize(400, 300)

        layout = QVBoxLayout(dialog)

        # Label for the input dialog
        label = QLabel("Enter your note (Markdown supported):")
        layout.addWidget(label)

        # Multi-line text box for input
        text_edit = QPlainTextEdit()
        layout.addWidget(text_edit)

        # Buttons for submitting or canceling
        submit_button = QPushButton("Submit")
        cancel_button = QPushButton("Cancel")
        submit_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        layout.addWidget(submit_button)
        layout.addWidget(cancel_button)

        if dialog.exec_() == QDialog.Accepted:
            note = text_edit.toPlainText()
            if note.strip():
                self.data["weeks"][self.current_monday][f"{day}_{time_block}_note"] = note
                save_data(self.data)
                self.refresh_ui()
    
    def edit_note_for_button(self, button):
        """Edit the note for a selected block with Markdown support."""
        day, time_block = self.get_day_time_from_button(button)
        existing_note = self.data["weeks"][self.current_monday].get(f"{day}_{time_block}_note", "")

        # Create a custom dialog for multi-line text input
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Note")
        dialog.resize(400, 300)

        layout = QVBoxLayout(dialog)

        # Label for the input dialog
        label = QLabel("Modify your note (Markdown supported):")
        layout.addWidget(label)

        # Multi-line text box for input, pre-filled with the existing note
        text_edit = QPlainTextEdit()
        text_edit.setPlainText(existing_note)
        layout.addWidget(text_edit)

        # Buttons for submitting or canceling
        submit_button = QPushButton("Submit")
        cancel_button = QPushButton("Cancel")
        submit_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)

        layout.addWidget(submit_button)
        layout.addWidget(cancel_button)

        if dialog.exec_() == QDialog.Accepted:
            new_note = text_edit.toPlainText()
            if new_note.strip():
                self.data["weeks"][self.current_monday][f"{day}_{time_block}_note"] = new_note
                save_data(self.data)
                self.refresh_ui()

    
    def delete_note_for_button(self, button):
        """Delete the note for a selected block."""
        day, time_block = self.get_day_time_from_button(button)
        
        if f"{day}_{time_block}_note" in self.data["weeks"][self.current_monday]:
            del self.data["weeks"][self.current_monday][f"{day}_{time_block}_note"]
            save_data(self.data)
            self.refresh_ui()
    
    def undo_deep_work(self, button):
        """Undo marking a block as deep work."""
        day, time_block = self.get_day_time_from_button(button)
        self.data["weeks"][self.current_monday][day][time_block] = ""
        button.setStyleSheet("")
        save_data(self.data)
        self.refresh_ui()
    
    def display_note_for_button(self, button):
        """Display the note for a selected block, rendering Markdown."""
        day, time_block = self.get_day_time_from_button(button)
        note = self.data["weeks"][self.current_monday].get(f"{day}_{time_block}_note", "")
        
        # Convert Markdown to HTML
        rendered_note = markdown2.markdown(note)
        
        # Display rendered Markdown in the QTextBrowser
        self.side_panel.setHtml(rendered_note)
    
    def get_day_time_from_button(self, button):
        """Helper method to retrieve the day and time block associated with a button."""
        for (day, time_block), btn in self.buttons.items():
            if btn == button:
                return day, time_block
        return None, None
    
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
    
    def export_data(self):
        """Export the data to a JSON file."""
        file_name, _ = QFileDialog.getSaveFileName(self, "Export Data", "", "JSON Files (*.json)")
        if file_name:
            with open(file_name, "w") as f:
                json.dump(self.data, f, indent=4)
            QMessageBox.information(self, "Success", "Data exported successfully.")
    
    def check_week_transition(self):
        """Check periodically if the week has changed and update data accordingly."""
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
                self.data["weeks"][new_monday] = {day: {block: "" for block in TIME_BLOCKS} for day in DAYS_OF_WEEK}
                save_data(self.data)
            self.refresh_ui()

def main():
    app = QApplication(sys.argv)
    window = TimeKeeperApp()
    window.showMaximized()  # Start maximized for better visibility
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
