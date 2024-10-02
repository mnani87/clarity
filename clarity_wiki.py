# Clarity Wiki - A Personal Knowledge Base and note-taking app, with live preview of markdown. 
# ClarityOne: Clear, simple, trying to do one thing well. 
# Copyright (c) 2024 MCN
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 3, as published by
# the Free Software Foundation. The full license is available at:
# https://www.gnu.org/licenses/gpl-3.0.html
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY REPRESENTATION OR WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. Indeed, the program may be worse than useless.

# clarity_wiki.py

import sys
import os
import re
import markdown
import yaml
import urllib.parse
import shutil
import tempfile
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QFileDialog, QAction, QVBoxLayout,
    QWidget, QSplitter, QListWidget, QListWidgetItem, QLineEdit, QCompleter,
    QLabel, QTabWidget, QMessageBox, QToolBar, QStatusBar, QInputDialog, QStyle, QHBoxLayout, QMenu,
    QListView, QCheckBox, QPushButton, QDialog, QDialogButtonBox, QGridLayout, QScrollArea
)
from PyQt5.QtGui import (
    QKeySequence, QTextCursor, QSyntaxHighlighter, QTextCharFormat, QColor,
    QFont, QPalette, QIcon, QPixmap
)
from PyQt5.QtCore import Qt, QSize, QUrl, QRect, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtSvg import QSvgWidget
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Constants for macOS application data directory
NOTES_DIR = os.path.expanduser('~/Library/Application Support/ClarityWiki/notes/')
MISC_WIKI = 'miscellaneous'  # Default wiki for ungrouped notes


class TagFilterDialog(QDialog):
    """
    Dialog to select tags for filtering notes.
    """
    def __init__(self, available_tags, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Filter by Tags")
        self.resize(300, 400)
        self.selected_tags = []

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Scroll Area for tags
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)

        self.tag_checkboxes = []
        for tag in available_tags:
            checkbox = QCheckBox(tag)
            self.tag_checkboxes.append(checkbox)
            scroll_layout.addWidget(checkbox)

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_selected_tags(self):
        self.selected_tags = [cb.text() for cb in self.tag_checkboxes if cb.isChecked()]
        return self.selected_tags


class MarkdownHighlighter(QSyntaxHighlighter):
    """
    Minimalistic monochrome syntax highlighter for Markdown text.
    Provides basic formatting through font styles without varying colors.
    """
    def __init__(self, parent: QTextEdit):
        super().__init__(parent.document())
        self.editor = parent
        self.highlighting_rules = []

        # Determine if the palette is dark or light
        palette = self.editor.palette()
        is_dark = palette.color(QPalette.Window).value() < 128

        # Define a single color based on the theme
        syntax_color = QColor("#FFFFFF") if is_dark else QColor("#000000")

        # Define a single QTextCharFormat for all syntax
        # (Will be cloned and modified for each pattern)
        
        # List of regex patterns to highlight along with their formatting styles
        patterns = [
            (r'\*\*(.*?)\*\*', 'bold'),          # Bold
            (r'\*(.*?)\*', 'italic'),           # Italic
            (r'~~(.*?)~~', 'strikeout'),        # Strikethrough
            (r'^(#{1,6})\s+(.*)', 'bold'),      # Headers
        ]

        # Add patterns to the highlighter with corresponding QTextCharFormat
        for pattern, style in patterns:
            regex = re.compile(pattern)
            fmt = QTextCharFormat()
            fmt.setForeground(syntax_color)

            if style == 'bold':
                fmt.setFontWeight(QFont.Bold)
            elif style == 'italic':
                fmt.setFontItalic(True)
            elif style == 'strikeout':
                fmt.setFontStrikeOut(True)

            self.highlighting_rules.append((regex, fmt))

    def highlightBlock(self, text):
        """
        Applies syntax highlighting to the given block of text.
        """
        for pattern, fmt in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)

class NoteEditor(QWidget):
    """
    Widget containing the tags input and the QTextEdit for editing notes.
    """
    def __init__(self, notes_dir, parent=None):
        super().__init__(parent)
        self.notes_dir = notes_dir

        # Layouts
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Tags Layout
        tags_layout = QHBoxLayout()
        tags_label = QLabel("Tags (comma separated):")
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("e.g., work, urgent")
        tags_layout.addWidget(tags_label)
        tags_layout.addWidget(self.tags_input)

        # Editor
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Charter", 12))
        self.highlighter = MarkdownHighlighter(self.editor)  # Pass the editor directly

        # Add to layout
        self.layout.addLayout(tags_layout)
        self.layout.addWidget(self.editor)

        # Auto-completer
        self.completer = QCompleter(self.get_note_titles(), self.editor)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.PopupCompletion)
        self.completer.activated.connect(self.insert_completion)
        self.completer.setMaxVisibleItems(10)

        # Connect signals
        self.editor.textChanged.connect(self.update_completer)

    def get_note_titles(self):
        """
        Retrieves the list of note titles from the notes directory.
        """
        titles = []
        for root, dirs, files in os.walk(self.notes_dir):
            for f in files:
                if f.endswith(('.md', '.txt')):
                    titles.append(os.path.splitext(f)[0])
        return sorted(set(titles))

    def update_completer(self):
        """
        Updates the completer's model with the latest note titles.
        """
        self.completer.model().setStringList(self.get_note_titles())

    def insert_completion(self, completion):
        """
        Inserts the selected completion into the text, replacing the [[
        """
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 2)  # Move back by 2 to account for [[
        cursor.select(QTextCursor.WordUnderCursor)
        if cursor.selectedText() == '[[':
            cursor.removeSelectedText()
            cursor.insertText(f"[[{completion}]]")
            self.editor.setTextCursor(cursor)

    def keyPressEvent(self, event):
        """
        Handles key press events for auto-completion and formatting shortcuts.
        """
        # Handle formatting shortcuts
        if event.matches(QKeySequence.Bold):
            self.format_bold()
            return
        elif event.matches(QKeySequence.Italic):
            self.format_italic()
            return

        # Detect if the user has typed '[[' to trigger completer
        super(NoteEditor, self).keyPressEvent(event)  # Let QTextEdit handle the key press first

        cursor = self.editor.textCursor()
        cursor_position = cursor.position()
        if cursor_position < 2:
            return
        cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 2)
        block = self.editor.document().findBlock(cursor.position())
        last_two_chars = block.text()[-2:]
        if last_two_chars == '[[':
            # Show completer at cursor position
            cursor_rect = self.editor.cursorRect(cursor)
            cursor_rect.setWidth(self.completer.popup().sizeHintForColumn(0))
            self.completer.complete(cursor_rect)

    def format_bold(self):
        """
        Formats the selected text as bold.
        """
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            cursor.insertText(f"**{selected_text}**")
        else:
            cursor.insertText("****")
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 2)

    def format_italic(self):
        """
        Formats the selected text as italic.
        """
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            cursor.insertText(f"*{selected_text}*")
        else:
            cursor.insertText("*")
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)

class CustomWebEnginePage(QWebEnginePage):
    """
    Custom QWebEnginePage to handle link navigation for internal note links.
    """
    def __init__(self, clarity_wiki, parent=None, notes_dir=None):
        super().__init__(parent)
        self.clarity_wiki = clarity_wiki
        self.notes_dir = notes_dir  # The root directory for all wikis

    def acceptNavigationRequest(self, url, _type, is_main_frame):
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            if url.scheme() == "internal":
                # Decode the note title from the URL
                note_title = urllib.parse.unquote(url.toString().replace("internal://", ""))
                # Ensure we are checking in the current wiki directory
                current_wiki_path = os.path.join(self.notes_dir, self.clarity_wiki.current_wiki)
                file_path_md = os.path.join(current_wiki_path, f"{note_title}.md")
                file_path_txt = os.path.join(current_wiki_path, f"{note_title}.txt")

                # Check if the note exists and open it in a tab
                if os.path.exists(file_path_md):
                    self.clarity_wiki.open_note_in_tab(file_path_md)
                    return False  # Prevent default navigation
                elif os.path.exists(file_path_txt):
                    self.clarity_wiki.open_note_in_tab(file_path_txt)
                    return False  # Prevent default navigation
                else:
                    QMessageBox.warning(self.clarity_wiki, "Note Not Found",
                                        f"The note '{note_title}' does not exist in the current wiki.")
                    return False  # Prevent default navigation
        return super().acceptNavigationRequest(url, _type, is_main_frame)

class MarkdownPreview(QWebEngineView):
    """
    WebEngineView to display the HTML preview of the markdown content.
    """
    def __init__(self, clarity_wiki, parent=None):
        super().__init__(parent)
        self.clarity_wiki = clarity_wiki

    def load_html(self, html_content):
        """
        Loads the given HTML content into the web view.
        """
        self.setHtml(html_content)


class ClarityWiki(QMainWindow):
    """
    Main application window for Clarity Wiki.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Clarity Wiki")
        # Use standard file icon from the current style
        self.setWindowIcon(QApplication.style().standardIcon(QStyle.SP_FileIcon))
        self.resize(1200, 800)

        # Multi-wiki directory initialization
        os.makedirs(os.path.join(NOTES_DIR, MISC_WIKI), exist_ok=True)
        self.current_wiki = None  # Store the current selected wiki
        self.notes_dir = NOTES_DIR

        # Initialize UI components
        self.init_ui()
        self.load_wikis()

    def init_ui(self):
        """
        Initializes the UI components.
        """
        # Central Widget with Splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        splitter = QSplitter(Qt.Horizontal)

        # Wikis List
        self.wikis_list = QListWidget()
        self.wikis_list.setIconSize(QSize(16, 16))
        self.wikis_list.itemClicked.connect(self.wiki_selected)
        splitter.addWidget(self.wikis_list)

        # Notes List
        self.notes_list = QListWidget()
        self.notes_list.setIconSize(QSize(16, 16))
        self.notes_list.itemDoubleClicked.connect(self.note_double_clicked)
        self.notes_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.notes_list.customContextMenuRequested.connect(self.show_note_context_menu)
        splitter.addWidget(self.notes_list)

        # Tab Widget for Editors and Previews
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        splitter.addWidget(self.tab_widget)

        splitter.setSizes([150, 250, 800])

        main_layout.addWidget(splitter)

        # Toolbar
        self.init_toolbar()

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    def init_toolbar(self):
        """
        Initializes the toolbar with actions.
        """
        toolbar = QToolBar("Main Toolbar")
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)

        # New Wiki Action
        new_wiki_action = QAction("New Wiki", self)
        new_wiki_action.setIcon(QIcon.fromTheme("folder-new"))
        new_wiki_action.triggered.connect(self.new_wiki)
        toolbar.addAction(new_wiki_action)

        # Delete Wiki Action
        delete_wiki_action = QAction("Delete Wiki", self)
        delete_wiki_action.setIcon(QIcon.fromTheme("folder-delete"))
        delete_wiki_action.triggered.connect(self.delete_wiki)
        toolbar.addAction(delete_wiki_action)

        toolbar.addSeparator()

        # New Note Action
        new_note_action = QAction("New Note", self)
        new_note_action.setIcon(QIcon.fromTheme("document-new"))
        new_note_action.setShortcut(QKeySequence.New)
        new_note_action.triggered.connect(self.new_note)
        toolbar.addAction(new_note_action)

        # Open Note Action
        open_note_action = QAction("Open Note", self)
        open_note_action.setIcon(QIcon.fromTheme("document-open"))
        open_note_action.setShortcut(QKeySequence.Open)
        open_note_action.triggered.connect(self.open_note)
        toolbar.addAction(open_note_action)

        # Save Note Action
        save_note_action = QAction("Save Note", self)
        save_note_action.setIcon(QIcon.fromTheme("document-save"))
        save_note_action.setShortcut(QKeySequence.Save)
        save_note_action.triggered.connect(self.save_note)
        toolbar.addAction(save_note_action)

        # Export Note Action
        export_note_action = QAction("Export Note", self)
        export_note_action.setIcon(QIcon.fromTheme("document-export"))
        export_note_action.triggered.connect(self.export_note)
        toolbar.addAction(export_note_action)

        # Delete Note Action
        delete_note_action = QAction("Delete Note", self)
        delete_note_action.setIcon(QIcon.fromTheme("edit-delete"))
        delete_note_action.setShortcut(QKeySequence("Ctrl+D"))  # Use Cmd+D on macOS or Ctrl+D on other platforms
        delete_note_action.triggered.connect(self.delete_note)
        toolbar.addAction(delete_note_action)

        toolbar.addSeparator()

        # Tag Filter Action
        filter_tags_action = QAction("Filter Tags", self)
        filter_tags_action.setIcon(QIcon.fromTheme("view-filter"))
        filter_tags_action.triggered.connect(self.filter_tags)
        toolbar.addAction(filter_tags_action)

        toolbar.addSeparator()

        # Search Within Current Wiki
        self.search_bar_current_wiki = QLineEdit()
        self.search_bar_current_wiki.setPlaceholderText("Search within current wiki...")
        self.search_bar_current_wiki.textChanged.connect(self.search_current_wiki)
        toolbar.addWidget(self.search_bar_current_wiki)

        # Search Across All Wikis
        self.search_bar_all_wikis = QLineEdit()
        self.search_bar_all_wikis.setPlaceholderText("Search across all wikis...")
        self.search_bar_all_wikis.textChanged.connect(self.search_all_wikis)
        toolbar.addWidget(self.search_bar_all_wikis)

        toolbar.addSeparator()

        # Bold Action
        bold_action = QAction("Bold", self)
        bold_action.setIcon(QIcon.fromTheme("format-text-bold"))
        bold_action.setShortcut(QKeySequence.Bold)
        bold_action.triggered.connect(self.bold_text)
        toolbar.addAction(bold_action)

        # Italic Action
        italic_action = QAction("Italic", self)
        italic_action.setIcon(QIcon.fromTheme("format-text-italic"))
        italic_action.setShortcut(QKeySequence.Italic)
        italic_action.triggered.connect(self.italic_text)
        toolbar.addAction(italic_action)

    def load_wikis(self):
        """
        Loads the list of wikis (directories) in the notes directory.
        """
        self.wikis_list.clear()

        for wiki_name in sorted(os.listdir(self.notes_dir)):
            wiki_path = os.path.join(self.notes_dir, wiki_name)
            if os.path.isdir(wiki_path):
                item = QListWidgetItem(wiki_name)
                item.setData(Qt.UserRole, wiki_path)
                self.wikis_list.addItem(item)

    def wiki_selected(self, item):
        """
        Loads the notes of the selected wiki when clicked.
        """
        self.current_wiki = item.text()  # Store the selected wiki name
        wiki_path = item.data(Qt.UserRole)
        self.load_notes(wiki_path)

    def load_notes(self, wiki_path):
        """
        Loads the list of notes from the selected wiki directory.
        """
        self.notes_list.clear()

        for file_name in sorted(os.listdir(wiki_path)):
            if file_name.endswith(('.md', '.txt')):
                item = QListWidgetItem(file_name)
                item.setData(Qt.UserRole, os.path.join(wiki_path, file_name))
                self.notes_list.addItem(item)

    def show_note_context_menu(self, pos):
        """
        Shows context menu on right-click for the notes list.
        Allows deleting the selected note.
        """
        item = self.notes_list.itemAt(pos)
        if item:
            menu = QMenu(self)
            delete_action = menu.addAction("Delete Note")
            action = menu.exec_(self.notes_list.mapToGlobal(pos))
            if action == delete_action:
                file_path = item.data(Qt.UserRole)
                confirm = QMessageBox.question(
                    self, "Delete Note",
                    f"Are you sure you want to delete '{os.path.basename(file_path)}'?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if confirm == QMessageBox.Yes:
                    os.remove(file_path)
                    self.load_notes(os.path.dirname(file_path))
                    self.status_bar.showMessage(f"Deleted note: {os.path.basename(file_path)}", 5000)

    def new_wiki(self):
        """
        Creates a new wiki (directory) and adds it to the wikis list.
        """
        wiki_name, ok = QInputDialog.getText(self, "New Wiki", "Enter wiki name:")
        if ok and wiki_name:
            sanitized_name = re.sub(r'[\\/*?:"<>|]', "", wiki_name)
            wiki_path = os.path.join(self.notes_dir, sanitized_name)
            if not os.path.exists(wiki_path):
                os.makedirs(wiki_path)
                self.load_wikis()
                self.status_bar.showMessage(f"Created new wiki: {sanitized_name}", 5000)
            else:
                QMessageBox.warning(self, "Error", f"A wiki with the name '{sanitized_name}' already exists.")

    def delete_wiki(self):
        """
        Deletes the selected wiki after confirming with the user.
        """
        selected_item = self.wikis_list.currentItem()
        
        if not selected_item:
            QMessageBox.warning(self, "No Wiki Selected", "Please select a wiki to delete.")
            return
        
        wiki_name = selected_item.text()
        wiki_path = os.path.join(self.notes_dir, wiki_name)
        
        if not os.path.exists(wiki_path):
            QMessageBox.warning(self, "Wiki Not Found", f"The wiki '{wiki_name}' does not exist.")
            return

        # Warning message box for confirmation
        confirm = QMessageBox.question(
            self,
            "Delete Wiki",
            f"Are you sure you want to delete the wiki '{wiki_name}'?\nThis will also delete all notes inside it and cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                shutil.rmtree(wiki_path)
                self.load_wikis()  # Reload the wikis list after deletion
                self.status_bar.showMessage(f"Deleted wiki: {wiki_name}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete wiki: {e}")

    def new_note(self):
        """
        Creates a new note in the selected wiki or the 'miscellaneous' wiki.
        """
        if not self.current_wiki:
            QMessageBox.warning(self, "No Wiki Selected", "Please select a wiki to add a note.")
            return

        note_title, ok = QInputDialog.getText(self, "New Note", "Enter note title:")
        if ok and note_title:
            sanitized_title = re.sub(r'[\\/*?:"<>|]', "", note_title)
            wiki_path = os.path.join(self.notes_dir, self.current_wiki)
            file_path_md = os.path.join(wiki_path, f"{sanitized_title}.md")

            if os.path.exists(file_path_md):
                QMessageBox.warning(self, "Error", f"A note with the name '{sanitized_title}' already exists.")
                return

            with open(file_path_md, 'w', encoding='utf-8') as f:
                f.write(f"---\ntags: []\n---\n\n# {sanitized_title}\n")
            self.load_notes(wiki_path)
            self.status_bar.showMessage(f"Created new note: {sanitized_title}", 5000)

    def open_note(self):
        """
        Opens an existing note using a file dialog.
        """
        if not self.current_wiki:
            QMessageBox.warning(self, "No Wiki Selected", "Please select a wiki first.")
            return

        wiki_path = os.path.join(self.notes_dir, self.current_wiki)
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Note", wiki_path, "Markdown Files (*.md);;Text Files (*.txt)")

        if file_path:
            self.open_note_in_tab(file_path)

    def open_note_in_tab(self, file_path):
        """
        Opens a note in a new tab, always creating a new tab even if the note is already open.
        """
        editor_widget = NoteEditor(self.notes_dir)
        preview = MarkdownPreview(self)
        page = CustomWebEnginePage(self, preview, self.notes_dir)
        preview.setPage(page)

        # Apply consistent stylesheet to QWebEngineView
        self.apply_preview_stylesheet(preview)

        # Layout for editor and preview
        tab_splitter = QSplitter(Qt.Vertical)
        tab_splitter.addWidget(editor_widget)
        tab_splitter.addWidget(preview)
        tab_splitter.setSizes([600, 400])

        # Create a container widget for the tab
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(tab_splitter)
        container.setLayout(layout)

        # Add the tab to the tab widget
        tab_title = os.path.basename(file_path)
        self.tab_widget.addTab(container, tab_title)
        self.tab_widget.setCurrentWidget(container)

        # Load the note content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Parse YAML front matter for tags
            front_matter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
            if front_matter_match:
                front_matter = front_matter_match.group(1)
                metadata = yaml.safe_load(front_matter)
                tags = metadata.get('tags', [])
                editor_widget.tags_input.setText(', '.join(tags))
                # Remove front matter from content for the editor
                content_body = content[front_matter_match.end():]
                editor_widget.editor.setPlainText(content_body)
            else:
                editor_widget.editor.setPlainText(content)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open note: {e}")
            return

        # Set up connections
        editor_widget.editor.textChanged.connect(lambda: self.update_preview(editor_widget, preview))
        editor_widget.tags_input.textChanged.connect(lambda: self.update_tags(editor_widget))
        self.update_preview(editor_widget, preview)  # Initial preview

        # Store the current note path in the editor
        editor_widget.current_note_path = file_path

        # Update backlinks
        self.update_backlinks(editor_widget)

    def apply_preview_stylesheet(self, preview):
        """
        Applies a stylesheet to the QWebEngineView to match the application's palette.
        """
        palette = self.palette()
        if palette.color(QPalette.Window).value() < 128:
            # Dark mode
            bg_color = "#2B2B2B"
            text_color = "#FFFFFF"
        else:
            # Light mode
            bg_color = "#FFFFFF"
            text_color = "#000000"

        stylesheet = f"""
            body {{
                background-color: {bg_color};
                color: {text_color};
                font-family: sans-serif;
                padding: 10px;
            }}
            a {{
                color: #1E90FF;
            }}
        """
        preview.setStyleSheet(stylesheet)

    def close_tab(self, index):
        """
        Closes a tab at the specified index, prompting the user to save changes if the document is modified.
        """
        widget = self.tab_widget.widget(index)
        editor_widget = widget.findChild(NoteEditor)
        if editor_widget and editor_widget.editor.document().isModified():
            response = QMessageBox.question(
                self, "Unsaved Changes",
                "The note has unsaved changes. Do you want to save before closing?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if response == QMessageBox.Yes:
                self.save_note()
            elif response == QMessageBox.Cancel:
                return
        self.tab_widget.removeTab(index)

    def save_note(self):
        """
        Saves the current note, including tags, and resets the document's modification state.
        """
        current_widget = self.tab_widget.currentWidget()
        if not current_widget:
            return
        editor_widget = current_widget.findChild(NoteEditor)
        if not editor_widget:
            return
        file_path = getattr(editor_widget, 'current_note_path', None)
        if not file_path:
            return

        try:
            content = editor_widget.editor.toPlainText()
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()

            front_matter_match = re.match(r'^---\n(.*?)\n---\n', original_content, re.DOTALL)
            if front_matter_match:
                front_matter = front_matter_match.group(1)
                metadata = yaml.safe_load(front_matter)
            else:
                metadata = {}

            tags_text = editor_widget.tags_input.text()
            tags = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
            metadata['tags'] = tags

            new_front_matter = yaml.dump(metadata, sort_keys=False)
            new_front_matter = f"---\n{new_front_matter}---\n\n"

            new_content = new_front_matter + content

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            # Reset the modification state of the document
            editor_widget.editor.document().setModified(False)

            self.status_bar.showMessage(f"Saved note: {os.path.basename(file_path)}", 5000)
            wiki_path = os.path.dirname(file_path)
            self.load_notes(wiki_path)

            # Update backlinks
            self.update_backlinks(editor_widget)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save note: {e}")

    def delete_note(self):
        """
        Deletes the current note after prompting the user for confirmation.
        """
        current_widget = self.tab_widget.currentWidget()
        if not current_widget:
            QMessageBox.warning(self, "No Note Opened", "Please open a note to delete.")
            return

        editor_widget = current_widget.findChild(NoteEditor)
        if not editor_widget:
            QMessageBox.warning(self, "No Note Found", "Please open a note to delete.")
            return

        file_path = getattr(editor_widget, 'current_note_path', None)
        if not file_path:
            QMessageBox.warning(self, "No Note Found", "Please open a note to delete.")
            return

        # Ask for confirmation
        confirm = QMessageBox.question(
            self, "Delete Note",
            f"Are you sure you want to delete '{os.path.basename(file_path)}'?",
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            try:
                os.remove(file_path)
                self.tab_widget.removeTab(self.tab_widget.indexOf(current_widget))
                self.status_bar.showMessage(f"Deleted note: {os.path.basename(file_path)}", 5000)
                wiki_path = os.path.dirname(file_path)
                self.load_notes(wiki_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete note: {e}")

    def export_note(self):
        """
        Exports the current note as HTML or PDF.
        """
        current_widget = self.tab_widget.currentWidget()
        if not current_widget:
            QMessageBox.warning(self, "No Note Opened", "Please open a note to export.")
            return

        editor_widget = current_widget.findChild(NoteEditor)
        if not editor_widget:
            QMessageBox.warning(self, "No Note Found", "Please open a note to export.")
            return

        file_path = getattr(editor_widget, 'current_note_path', None)
        if not file_path:
            QMessageBox.warning(self, "No Note Found", "Please open a note to export.")
            return

        # Ask for export format
        export_format, ok = QInputDialog.getItem(
            self,
            "Export Note",
            "Select export format:",
            ["HTML", "PDF"],
            0,
            False
        )
        if not ok or not export_format:
            return  # User cancelled

        # Choose export location
        default_extension = "html" if export_format == "HTML" else "pdf"
        export_filter = f"{export_format} Files (*.{default_extension})"
        export_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Export Note as {export_format}",
            os.path.splitext(file_path)[0] + f".{default_extension}",
            export_filter
        )

        if not export_path:
            return  # User cancelled

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Convert Markdown to HTML with extensions
            html = markdown.markdown(content, extensions=['extra', 'toc', 'codehilite'])

            # Define CSS styles with desired font
            css = """
            <style>
                body {
                    font-family: 'Charter', 'Palatino', serif;
                    padding: 20px;
                    background-color: white;
                    color: black;
                }
                h1, h2, h3, h4, h5, h6 {
                    color: #1E90FF;
                }
                pre {
                    background-color: #f0f0f0;
                    padding: 10px;
                    border-radius: 5px;
                }
                code {
                    background-color: #f0f0f0;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: 'Courier New', Courier, monospace;
                }
                a {
                    color: #FF4500;
                    text-decoration: none;
                }
                a:hover {
                    text-decoration: underline;
                }
            </style>
            """

            # Combine CSS with HTML
            full_html = f"<html><head>{css}</head><body>{html}</body></html>"

            if export_format == "HTML":
                with open(export_path, 'w', encoding='utf-8') as f:
                    f.write(full_html)
                self.status_bar.showMessage(f"Exported note as HTML: {export_path}", 5000)

            elif export_format == "PDF":
                # Create a temporary QWebEngineView
                web_view = QWebEngineView()
                web_view.setHtml(full_html, QUrl(""))

                # Store a reference to prevent garbage collection
                self._export_web_view = web_view

                # Define a callback to handle the PDF data
                def handle_pdf_export(pdf_data):
                    try:
                        with open(export_path, 'wb') as f:
                            f.write(pdf_data)
                        self.status_bar.showMessage(f"Exported note as PDF: {export_path}", 5000)
                    except Exception as e:
                        QMessageBox.critical(self, "Export Error", f"Failed to save PDF: {e}")
                    finally:
                        # Clean up the web_view reference
                        del self._export_web_view

                # Connect the signal to ensure the page is loaded before exporting
                def on_load_finished(ok):
                    if ok:
                        # Initiate PDF export
                        web_view.page().printToPdf(handle_pdf_export)
                    else:
                        QMessageBox.critical(self, "Export Error", "Failed to load HTML for PDF export.")
                        # Clean up the web_view reference
                        del self._export_web_view

                web_view.loadFinished.connect(on_load_finished)
                web_view.show()  # Necessary to initiate the load

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export note: {e}")


    def filter_tags(self):
        """
        Opens the tag filter dialog and filters notes based on selected tags.
        """
        available_tags = self.get_all_tags()
        if not available_tags:
            QMessageBox.information(self, "No Tags", "No tags available to filter.")
            return

        dialog = TagFilterDialog(available_tags, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_tags = dialog.get_selected_tags()
            if selected_tags:
                self.apply_tag_filter(selected_tags)
            else:
                # If no tags selected, reload all notes
                self.load_notes(os.path.join(self.notes_dir, self.current_wiki))

    def get_all_tags(self):
        """
        Retrieves all unique tags from the current wiki.
        """
        if not self.current_wiki:
            return []

        all_tags = set()
        wiki_path = os.path.join(self.notes_dir, self.current_wiki)

        for file_name in os.listdir(wiki_path):
            if file_name.endswith(('.md', '.txt')):
                file_path = os.path.join(wiki_path, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    front_matter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
                    if front_matter_match:
                        front_matter = front_matter_match.group(1)
                        metadata = yaml.safe_load(front_matter)
                        tags = metadata.get('tags', [])
                        all_tags.update(tags)

        return sorted(all_tags)

    def apply_tag_filter(self, selected_tags):
        """
        Filters the notes list based on the selected tags.
        """
        self.notes_list.clear()
        wiki_path = os.path.join(self.notes_dir, self.current_wiki)

        for file_name in sorted(os.listdir(wiki_path)):
            if file_name.endswith(('.md', '.txt')):
                file_path = os.path.join(wiki_path, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    front_matter_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
                    if front_matter_match:
                        front_matter = front_matter_match.group(1)
                        metadata = yaml.safe_load(front_matter)
                        tags = metadata.get('tags', [])
                        if any(tag in tags for tag in selected_tags):
                            item = QListWidgetItem(file_name)
                            item.setData(Qt.UserRole, file_path)
                            self.notes_list.addItem(item)

    def bold_text(self):
        """
        Formats the selected text as bold.
        """
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            editor_widget = current_widget.findChild(NoteEditor)
            if editor_widget:
                editor_widget.format_bold()

    def italic_text(self):
        """
        Formats the selected text as italic.
        """
        current_widget = self.tab_widget.currentWidget()
        if current_widget:
            editor_widget = current_widget.findChild(NoteEditor)
            if editor_widget:
                editor_widget.format_italic()

    def search_current_wiki(self, query):
        """
        Searches for notes within the current wiki based on content.
        """
        if not self.current_wiki:
            return

        wiki_path = os.path.join(self.notes_dir, self.current_wiki)
        self.notes_list.clear()  # Clear current note list

        query_lower = query.lower()

        for file_name in sorted(os.listdir(wiki_path)):
            if file_name.endswith(('.md', '.txt')):
                file_path = os.path.join(wiki_path, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if query_lower in content:
                        item = QListWidgetItem(file_name)
                        item.setData(Qt.UserRole, file_path)
                        self.notes_list.addItem(item)

    def search_all_wikis(self, query):
        """
        Searches for notes across all wikis based on content.
        """
        if not query:
            return  # Avoid loading all notes when search is cleared

        self.notes_list.clear()  # Clear current note list
        query_lower = query.lower()

        for wiki_name in sorted(os.listdir(self.notes_dir)):
            wiki_path = os.path.join(self.notes_dir, wiki_name)
            if os.path.isdir(wiki_path):
                for file_name in sorted(os.listdir(wiki_path)):
                    if file_name.endswith(('.md', '.txt')):
                        file_path = os.path.join(wiki_path, file_name)
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read().lower()
                            if query_lower in content:
                                item = QListWidgetItem(f"{wiki_name}/{file_name}")
                                item.setData(Qt.UserRole, file_path)
                                self.notes_list.addItem(item)

    def note_double_clicked(self, item):
        """
        Opens a note when it's double-clicked in the notes list.
        """
        file_path = item.data(Qt.UserRole)
        self.open_note_in_tab(file_path)

    def update_preview(self, editor_widget, preview):
        """
        Updates the HTML preview based on the markdown content.
        """
        markdown_text = editor_widget.editor.toPlainText()
        html = markdown.markdown(markdown_text, extensions=['extra', 'toc', 'codehilite'])

        def replace_link(match):
            note = match.group(1).strip()
            encoded_note = urllib.parse.quote(note)
            return f'<a href="internal://{encoded_note}">[[{note}]]</a>'

        html = re.sub(r'\[\[([^\]]+)\]\]', replace_link, html)
        preview.load_html(html)

    def update_tags(self, editor_widget):
        """
        Automatically saves tags when the tags input is changed.
        """
        self.save_note()

    def get_backlinks(self, current_note_title):
        """
        Retrieves a list of notes that link to the current note.
        """
        backlinks = []
        wiki_path = os.path.join(self.notes_dir, self.current_wiki)

        for file_name in os.listdir(wiki_path):
            if file_name.endswith(('.md', '.txt')):
                note_title = os.path.splitext(file_name)[0]
                file_path = os.path.join(wiki_path, file_name)
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    links = re.findall(r'\[\[([^\]]+)\]\]', content)
                    if current_note_title in links:
                        backlinks.append(note_title)

        return backlinks

    def update_backlinks(self, editor_widget):
        """
        Displays backlinks for the current note.
        """
        file_path = getattr(editor_widget, 'current_note_path', None)
        if not file_path:
            return

        note_title = os.path.splitext(os.path.basename(file_path))[0]
        backlinks = self.get_backlinks(note_title)

        if backlinks:
            backlinks_text = "<h3>Backlinks</h3><ul>"
            for backlink in backlinks:
                backlinks_text += f'<li><a href="internal://{urllib.parse.quote(backlink)}">[[{backlink}]]</a></li>'
            backlinks_text += "</ul>"
        else:
            backlinks_text = "<h3>No Backlinks</h3>"

        # Find the preview widget in the tab and append backlinks
        preview = editor_widget.parent().findChild(MarkdownPreview)
        if preview:
            markdown_text = editor_widget.editor.toPlainText()
            html = markdown.markdown(markdown_text, extensions=['extra', 'toc', 'codehilite'])

            def replace_link(match):
                note = match.group(1).strip()
                encoded_note = urllib.parse.quote(note)
                return f'<a href="internal://{encoded_note}">[[{note}]]</a>'

            html = re.sub(r'\[\[([^\]]+)\]\]', replace_link, html)
            html += backlinks_text
            preview.setHtml(html)

    def export_backlinks(self, file_path):
        """
        Exports backlinks as part of the note.
        """
        # This function can be implemented similarly to export_note if needed
        pass


def main():
    """
    Entry point for the application.
    """
    app = QApplication(sys.argv)
    app.setApplicationName("Clarity Wiki")
    app.setOrganizationName("ClarityWiki")
    app.setOrganizationDomain("claritywiki.local")

    # Apply a Fusion style for a modern look
    app.setStyle("Fusion")

    window = ClarityWiki()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
