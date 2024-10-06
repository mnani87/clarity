# Clarity Explorer - A File Explorer system for Macs, but with a twist: organise files by project views, wherever the files actually are...
# ClarityOne: Clear, simple, trying to do one thing well. 
# Copyright (c) 2024 MCN
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 3, as published by
# the Free Software Foundation. The full license is available at:
# https://www.gnu.org/licenses/gpl-3.0.html
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY REPRESENTATION OR WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. Indeed, the program may be worse than useless.

# clarityone_explorer.py

import sys
import json
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QListWidget, QPushButton, QFileDialog, 
    QLabel, QTextBrowser, QHBoxLayout, QSplitter, QMessageBox, QInputDialog, QWidget, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont, QKeySequence
from PyQt5.QtWidgets import QShortcut
import PyPDF2
from docx import Document
from odf.opendocument import load as load_odf
from odf.text import P

# Define the path to save the projects file in ~/Library/Application Support/ClarityExplorer/
def get_project_file_path():
    app_support_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'ClarityExplorer')
    if not os.path.exists(app_support_dir):
        os.makedirs(app_support_dir)  # Create the directory if it doesn't exist
    return os.path.join(app_support_dir, 'projects.json')

# Load projects from JSON
def load_projects():
    project_file = get_project_file_path()
    if os.path.exists(project_file):
        with open(project_file, 'r') as f:
            return json.load(f)
    return {}

# Save projects to JSON
def save_projects(projects):
    project_file = get_project_file_path()
    with open(project_file, 'w') as f:
        json.dump(projects, f, indent=4)

class ClarityExplorer(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Clarity Explorer")
        self.setGeometry(100, 100, 800, 600)
        
        self.projects = load_projects()
        self.current_project = None
        self.file_path_map = {}  # Dictionary to map displayed file names to full paths
        
        # Set global font to Charter
        font = QFont("Charter", 12)
        self.setFont(font)
        
        # Main layout
        main_layout = QHBoxLayout()
        
        # Sidebar for Projects
        self.project_list = QListWidget()
        self.project_list.setFont(QFont("Charter", 12))
        self.project_list.addItems(self.projects.keys())
        self.project_list.itemClicked.connect(self.load_project_files)
        
        # Search Bar for Current Project
        self.project_search_bar = QLineEdit()
        self.project_search_bar.setPlaceholderText("Search files in this project...")
        self.project_search_bar.textChanged.connect(self.search_files_in_project)
        
        # Search Bar for Entire Explorer
        self.explorer_search_bar = QLineEdit()
        self.explorer_search_bar.setPlaceholderText("Search files across all projects...")
        self.explorer_search_bar.textChanged.connect(self.search_files_in_explorer)
        
        # File List and Preview
        self.file_list = QListWidget()
        self.file_list.setFont(QFont("Charter", 12))
        self.file_list.itemClicked.connect(self.preview_file)
        self.file_list.itemDoubleClicked.connect(self.open_file_with_default_app)  # Handle double-click event
        
        # Preview Area
        self.preview = QTextBrowser()
        self.preview.setReadOnly(True)
        self.preview.setFont(QFont("Charter", 12))
        
        # Add Project Button
        add_project_btn = QPushButton("Add Project")
        add_project_btn.setFont(QFont("Charter", 12))
        add_project_btn.clicked.connect(self.add_project)
        
        # Add File to Project Button (no compulsory tags)
        add_file_btn = QPushButton("Add File to Project")
        add_file_btn.setFont(QFont("Charter", 12))
        add_file_btn.clicked.connect(self.add_file)

        # Add Tags Button
        add_tag_btn = QPushButton("Manage Tags for File")
        add_tag_btn.setFont(QFont("Charter", 12))
        add_tag_btn.clicked.connect(self.add_tags_to_file)
        
        # Delete Project Button
        delete_project_btn = QPushButton("Delete Project")
        delete_project_btn.setFont(QFont("Charter", 12))
        delete_project_btn.clicked.connect(self.delete_project)

        # Delete File Button
        delete_file_btn = QPushButton("Delete File")
        delete_file_btn.setFont(QFont("Charter", 12))
        delete_file_btn.clicked.connect(self.delete_file_from_project)
        
        # Left Sidebar
        sidebar = QVBoxLayout()
        sidebar.addWidget(self.project_list)
        sidebar.addWidget(add_project_btn)
        sidebar.addWidget(add_file_btn)
        sidebar.addWidget(add_tag_btn)
        sidebar.addWidget(delete_project_btn)  # Add Delete Project button
        sidebar.addWidget(delete_file_btn)     # Add Delete File button
        
        left_widget = QWidget()
        left_widget.setLayout(sidebar)
        
        # Main content layout
        content_layout = QVBoxLayout()
        content_layout.addWidget(self.project_search_bar)  # Search Bar for Project
        content_layout.addWidget(self.explorer_search_bar)  # Search Bar for Explorer
        content_layout.addWidget(QLabel("Files:"))
        content_layout.addWidget(self.file_list)
        
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        
        # Splitter to adjust sizes of panels
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(content_widget)
        splitter.addWidget(self.preview)
        
        main_widget = QWidget()
        main_layout.addWidget(splitter)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Add keyboard shortcuts
        self.add_shortcuts()
    
    def load_project_files(self, item):
        project_name = item.text()
        self.current_project = project_name
        self.file_list.clear()
        self.file_path_map.clear()  # Clear the mapping for the new project
        
        # Populate the file list with just the file names, and map them to full paths
        for file_data in self.projects[project_name]:
            file_name = os.path.basename(file_data["file_path"])
            tags = file_data.get("tags", [])
            self.file_path_map[file_name] = file_data["file_path"]
            display_name = f"{file_name} (Tags: {', '.join(tags)})" if tags else file_name
            self.file_list.addItem(display_name)
    
    def add_project(self):
        # Add a new project with a user input dialog
        project_name, ok = QInputDialog.getText(self, 'New Project', 'Enter project name:')
        if ok and project_name:
            self.projects[project_name] = []
            self.project_list.addItem(project_name)
            save_projects(self.projects)
    
    def add_file(self):
        if not self.current_project:
            return
        
        # Open file dialog to add files
        files, _ = QFileDialog.getOpenFileNames(self, "Add Files to Project")
        if files:
            for file_path in files:
                file_name = os.path.basename(file_path)
                self.projects[self.current_project].append({"file_path": file_path, "tags": []})
                display_name = file_name
                self.file_list.addItem(display_name)
                self.file_path_map[file_name] = file_path
            save_projects(self.projects)
    
    def add_tags_to_file(self):
        if not self.current_project or not self.file_list.currentItem():
            return

        file_name = self.file_list.currentItem().text().split(' (Tags:')[0]
        file_path = self.file_path_map.get(file_name)
        project_files = self.projects[self.current_project]

        # Find the file data in the project and manage tags
        for file_data in project_files:
            if file_data["file_path"] == file_path:
                current_tags = file_data.get("tags", [])
                current_tags_str = ", ".join(current_tags)

                # Open input dialog pre-populated with existing tags
                tags_input, ok = QInputDialog.getText(self, "Manage Tags", 
                    f"Current Tags: {current_tags_str}\nAdd or edit tags (comma-separated):", 
                    text=current_tags_str  # Pre-populate with existing tags
                )
                
                if ok:
                    new_tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]
                    file_data["tags"] = new_tags
                    display_name = f"{file_name} (Tags: {', '.join(new_tags)})" if new_tags else file_name
                    self.file_list.currentItem().setText(display_name)
                    save_projects(self.projects)

    def search_files_in_project(self):
        search_query = self.project_search_bar.text().lower()
        self.file_list.clear()
        
        if not self.current_project:
            return
        
        for file_data in self.projects[self.current_project]:
            file_name = os.path.basename(file_data["file_path"])
            tags = file_data.get("tags", [])
            combined_text = f"{file_name} {' '.join(tags)}".lower()
            
            if search_query in combined_text:
                display_name = f"{file_name} (Tags: {', '.join(tags)})" if tags else file_name
                self.file_list.addItem(display_name)
                self.file_path_map[file_name] = file_data["file_path"]
    
    def search_files_in_explorer(self):
        search_query = self.explorer_search_bar.text().lower()
        self.file_list.clear()
        self.file_path_map.clear()

        # Search across all projects
        for project_name, files in self.projects.items():
            for file_data in files:
                file_name = os.path.basename(file_data["file_path"])
                tags = file_data.get("tags", [])
                combined_text = f"{file_name} {' '.join(tags)}".lower()

                if search_query in combined_text:
                    display_name = f"{file_name} (Tags: {', '.join(tags)})" if tags else file_name
                    self.file_list.addItem(display_name)
                    self.file_path_map[file_name] = file_data["file_path"]

    def preview_file(self, item):
        file_name = item.text().split(' (Tags:')[0]  # Extract file name without tags
        file_path = self.file_path_map.get(file_name)  # Get full path from the map
        
        if not os.path.exists(file_path):
            # Show an error message if the file does not exist
            QMessageBox.warning(self, "File Not Found", f"File not found: {file_path}")
            self.handle_missing_file(file_name)
            return
        
        # Preview different file types
        if file_path.endswith('.txt') or file_path.endswith('.md'):
            self.preview_plain_text(file_path)
        elif file_path.endswith('.pdf'):
            self.preview_pdf(file_path)
        elif file_path.endswith('.html'):
            self.preview_html(file_path)
        elif file_path.endswith('.docx'):
            self.preview_docx(file_path)
        elif file_path.endswith('.odt') or file_path.endswith('.odf'):
            self.preview_odt(file_path)
        elif file_path.endswith(('.jpg', '.png', '.gif')):
            self.preview_image(file_path)
        else:
            self.preview.setPlainText("Cannot preview this file type.")

    def preview_plain_text(self, file_path):
        """Preview plain text files (.txt, .md)."""
        with open(file_path, 'r') as f:
            self.preview.setPlainText(f.read())

    def preview_pdf(self, file_path):
        """Preview PDF files using PyPDF2."""
        try:
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = "\n".join(page.extract_text() for page in reader.pages)
                self.preview.setPlainText(text)
        except Exception as e:
            self.preview.setPlainText(f"Error loading PDF: {str(e)}")
    
    def preview_html(self, file_path):
        """Preview HTML files using QTextBrowser."""
        with open(file_path, 'r') as f:
            html_content = f.read()
            self.preview.setHtml(html_content)
    
    def preview_docx(self, file_path):
        """Preview DOCX files using python-docx."""
        try:
            doc = Document(file_path)
            full_text = "\n".join([para.text for para in doc.paragraphs])
            self.preview.setPlainText(full_text)
        except Exception as e:
            self.preview.setPlainText(f"Error loading DOCX: {str(e)}")
    
    def preview_odt(self, file_path):
        """Preview ODT/ODF files using odfpy."""
        try:
            odt_doc = load_odf(file_path)
            paragraphs = odt_doc.getElementsByType(P)
            full_text = "\n".join([para.text for para in paragraphs])
            self.preview.setPlainText(full_text)
        except Exception as e:
            self.preview.setPlainText(f"Error loading ODT: {str(e)}")

    def preview_image(self, file_path):
        """Preview image files."""
        pixmap = QPixmap(file_path)
        self.preview.setPixmap(pixmap)
    
    def handle_missing_file(self, file_name):
        # Offer to remove or locate the missing file
        file_path = self.file_path_map.get(file_name)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("File Missing")
        msg.setText(f"The file {file_path} is missing. What would you like to do?")
        locate_btn = msg.addButton("Locate", QMessageBox.ActionRole)
        remove_btn = msg.addButton("Remove from Project", QMessageBox.ActionRole)
        cancel_btn = msg.addButton("Cancel", QMessageBox.RejectRole)
        msg.exec_()
        
        if msg.clickedButton() == locate_btn:
            new_file, _ = QFileDialog.getOpenFileName(self, "Locate File")
            if new_file:
                # Update the file path in the project and save changes
                project_files = self.projects[self.current_project]
                project_files[project_files.index(file_path)] = new_file
                self.file_path_map[file_name] = new_file  # Update the mapping
                self.file_list.clear()
                self.load_project_files(self.project_list.currentItem())  # Refresh the list
                save_projects(self.projects)
        elif msg.clickedButton() == remove_btn:
            # Remove the missing file from the project
            self.projects[self.current_project].remove(file_path)
            self.file_list.clear()
            self.load_project_files(self.project_list.currentItem())  # Refresh the list
            save_projects(self.projects)

    def delete_project(self):
        """Delete the currently selected project from the app."""
        if self.current_project:
            reply = QMessageBox.question(self, 'Delete Project', 
                                         f"Are you sure you want to delete the project '{self.current_project}'?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                del self.projects[self.current_project]
                self.project_list.takeItem(self.project_list.currentRow())  # Remove from list
                self.file_list.clear()  # Clear the files display
                self.current_project = None
                save_projects(self.projects)

    def delete_file_from_project(self):
        """Delete the selected file from the current project without deleting it from storage."""
        if self.current_project and self.file_list.currentItem():
            file_name = self.file_list.currentItem().text().split(' (Tags:')[0]
            file_path = self.file_path_map.get(file_name)
            reply = QMessageBox.question(self, 'Delete File', 
                                         f"Are you sure you want to remove the file '{file_name}' from the project?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.projects[self.current_project] = [f for f in self.projects[self.current_project] if f["file_path"] != file_path]
                self.file_list.takeItem(self.file_list.currentRow())  # Remove from list
                save_projects(self.projects)
    
    def open_file_with_default_app(self, item):
        """Open the file with the default application on double-click."""
        file_name = item.text().split(' (Tags:')[0]
        file_path = self.file_path_map.get(file_name)
        
        if os.path.exists(file_path):
            try:
                # macOS: Use the 'open' command to open the file with the default application
                subprocess.run(["open", file_path])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open the file: {e}")
        else:
            QMessageBox.warning(self, "File Not Found", f"File not found: {file_path}")
            self.handle_missing_file(file_name)

    def add_shortcuts(self):
        """Add keyboard shortcuts for common actions."""
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self.add_project)  # Shortcut for adding new project
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self.project_search_bar.setFocus)  # Shortcut for focusing the project search bar
        QShortcut(QKeySequence("Ctrl+Shift+F"), self).activated.connect(self.explorer_search_bar.setFocus)  # Shortcut for focusing the explorer-wide search bar

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ClarityExplorer()
    window.show()
    sys.exit(app.exec_())
