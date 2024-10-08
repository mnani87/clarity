# Clarity Editor - A lightweight editor Macs, with basic formatting features. 
# ClarityOne: Clear, simple, trying to do one thing well.  
# Copyright (c) 2024 MCN 
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU General Public License, version 3, as published by 
# the Free Software Foundation. The full license is available at: 
# https://www.gnu.org/licenses/gpl-3.0.html 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY REPRESENTATION OR WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. Indeed, the program may be worse than useless.  

# clarityone_editor_v2proto.py

import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QDialog,
    QComboBox, QFileDialog, QSpinBox, QInputDialog, QMessageBox, QLabel,
    QAction, QToolBar, QLineEdit, QCheckBox, QPushButton, QHBoxLayout, QVBoxLayout,
    QSplitter, QWidget
)
from PyQt5.QtGui import (
    QFont, QTextCursor, QTextTableFormat, QKeySequence, QTextBlockFormat,
    QTextListFormat, QTextDocumentWriter, QPalette, QColor, QTextDocument, QTextCharFormat
)
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrinter

import qdarkstyle

from odf import text, teletype
from odf.opendocument import load

import markdown
from markdown.extensions import Extension  
import pygments  

from spellchecker import SpellChecker


class FindReplaceDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Find and Replace')
        self.setModal(False)  # Allow interaction with the main window

        self.parent = parent  # Reference to the main editor

        # Create widgets
        self.find_label = QLabel('Find:')
        self.find_input = QLineEdit()
        self.replace_label = QLabel('Replace:')
        self.replace_input = QLineEdit()

        # Options (uncomment if needed)
        # self.case_checkbox = QCheckBox('Case Sensitive')
        # self.whole_word_checkbox = QCheckBox('Whole Words')

        self.find_next_button = QPushButton('Find Next')
        self.replace_button = QPushButton('Replace')
        self.replace_all_button = QPushButton('Replace All')
        self.close_button = QPushButton('Close')

        # Connect signals
        self.find_next_button.clicked.connect(self.find_next)
        self.replace_button.clicked.connect(self.replace)
        self.replace_all_button.clicked.connect(self.replace_all)
        self.close_button.clicked.connect(self.close)
        self.find_input.textChanged.connect(self.highlight_all_occurrences)  # Highlight as you type

        # Layout
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.find_label)
        top_layout.addWidget(self.find_input)

        middle_layout = QHBoxLayout()
        middle_layout.addWidget(self.replace_label)
        middle_layout.addWidget(self.replace_input)

        options_layout = QHBoxLayout()
        # Uncomment if options are implemented
        # options_layout.addWidget(self.case_checkbox)
        # options_layout.addWidget(self.whole_word_checkbox)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.find_next_button)
        buttons_layout.addWidget(self.replace_button)
        buttons_layout.addWidget(self.replace_all_button)
        buttons_layout.addWidget(self.close_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addLayout(middle_layout)
        main_layout.addLayout(options_layout)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

        # Initialize search cursor
        self.cursor = None

    def find_next(self):
        """Find the next occurrence of the search text."""
        search_text = self.find_input.text()
        if not search_text:
            QMessageBox.warning(self, 'Find', 'Please enter text to find.')
            return

        options = QTextDocument.FindFlags()
        # Uncomment if options are implemented
        # if self.case_checkbox.isChecked():
        #     options |= QTextDocument.FindCaseSensitively
        # if self.whole_word_checkbox.isChecked():
        #     options |= QTextDocument.FindWholeWords

        # If no previous search, start from current cursor position
        if self.cursor is None:
            self.cursor = self.parent.editor.textCursor()
        else:
            # Move cursor forward to avoid finding the same text again
            position = self.cursor.position() + self.cursor.selectionEnd() - self.cursor.selectionStart()
            self.cursor.setPosition(position)

        # Search for the text
        self.cursor = self.parent.editor.document().find(search_text, self.cursor, options)
        if self.cursor.isNull():
            # Start from the beginning
            self.cursor = self.parent.editor.document().find(search_text, QTextCursor(), options)
            if self.cursor.isNull():
                QMessageBox.information(self, 'Find', 'Text not found.')
                self.cursor = None
                return

        # Highlight the found text
        self.parent.editor.setTextCursor(self.cursor)
        self.parent.editor.setFocus()

    def replace(self):
        """Replace the currently selected text if it matches the search text."""
        if self.cursor is None or self.cursor.selectedText() == '':
            self.find_next()
            return

        # Check if current selection matches search text
        search_text = self.find_input.text()
        selected_text = self.cursor.selectedText()
        options = QTextDocument.FindFlags()
        # Uncomment if options are implemented
        # if self.case_checkbox.isChecked():
        #     options |= QTextDocument.FindCaseSensitively
        # if self.whole_word_checkbox.isChecked():
        #     options |= QTextDocument.FindWholeWords

        # Replace the text
        replace_text = self.replace_input.text()
        self.cursor.insertText(replace_text)
        self.parent.editor.setTextCursor(self.cursor)
        self.parent.editor.setFocus()
        self.cursor = None  # Reset cursor after replacement

        # Refresh highlights
        self.highlight_all_occurrences()

    def replace_all(self):
        """Replace all occurrences of the search text."""
        search_text = self.find_input.text()
        if not search_text:
            QMessageBox.warning(self, 'Replace All', 'Please enter text to find.')
            return

        replace_text = self.replace_input.text()
        options = QTextDocument.FindFlags()
        # Uncomment if options are implemented
        # if self.case_checkbox.isChecked():
        #     options |= QTextDocument.FindCaseSensitively
        # if self.whole_word_checkbox.isChecked():
        #     options |= QTextDocument.FindWholeWords

        document = self.parent.editor.document()
        cursor = QTextCursor(document)
        count = 0

        cursor.beginEditBlock()
        while True:
            # Find the text
            found_cursor = document.find(search_text, cursor, options)
            if found_cursor.isNull():
                break

            # Replace the text
            found_cursor.insertText(replace_text)
            count += 1

            # Move the main cursor to after the replacement to continue searching
            cursor.setPosition(found_cursor.position())

        cursor.endEditBlock()

        QMessageBox.information(self, 'Replace All', f'Replaced {count} occurrence(s).')
        self.parent.editor.setFocus()
        self.cursor = None  # Reset cursor after replacement

        # Refresh highlights
        self.highlight_all_occurrences()

    def highlight_all_occurrences(self):
        """Highlight all occurrences of the search text in the document."""
        # Clear previous highlights
        self.remove_highlight()

        search_text = self.find_input.text()
        if not search_text:
            return  # Do nothing if search text is empty

        options = QTextDocument.FindFlags()
        # Uncomment if options are implemented
        # if self.case_checkbox.isChecked():
        #     options |= QTextDocument.FindCaseSensitively
        # if self.whole_word_checkbox.isChecked():
        #     options |= QTextDocument.FindWholeWords

        # Define the format for highlighting
        highlight_format = QTextCharFormat()
        highlight_format.setBackground(QColor("yellow"))

        # Start from the beginning of the document
        cursor = QTextCursor(self.parent.editor.document())
        while True:
            # Find the search text
            cursor = self.parent.editor.document().find(search_text, cursor, options)
            if cursor.isNull():
                break
            # Apply the highlight format
            cursor.mergeCharFormat(highlight_format)

    def remove_highlight(self):
        """Remove all highlights from the document."""
        # Define the format to clear the background color
        clear_format = QTextCharFormat()
        clear_format.setBackground(QColor("transparent"))

        # Select the entire document
        cursor = QTextCursor(self.parent.editor.document())
        cursor.beginEditBlock()
        cursor.select(QTextCursor.Document)
        cursor.mergeCharFormat(clear_format)
        cursor.endEditBlock()

    def closeEvent(self, event):
        """Handle the dialog close event."""
        self.remove_highlight()
        event.accept()

class ClarityEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize state
        self.is_modified = False  # Track if the document is modified
        self.current_file_path = None  # Track the path of the currently opened file
        self.dark_mode = False  # Start with light mode
        self.current_markdown = None  # To track if we're editing a Markdown file

        # Create the main text editor with default font Charter
        self.editor = QTextEdit()
        self.editor.setFont(QFont('Charter', 14))
        self.editor.cursorPositionChanged.connect(self.update_format_selection)  # Update toolbar based on cursor
        self.editor.textChanged.connect(self.mark_as_modified)  # Track modifications
    
        # Create the Markdown preview widget
        self.preview_widget = QTextEdit()
        self.preview_widget.setReadOnly(True)

        # Create a splitter to hold the editor and preview
        self.splitter = QSplitter(Qt.Horizontal)
        self.editor_widget = QWidget()

        # Set up the editor layout
        editor_layout = QVBoxLayout()
        editor_layout.addWidget(self.editor)
        self.editor_widget.setLayout(editor_layout)

        # Add widgets to the splitter
        self.splitter.addWidget(self.editor_widget)
        self.splitter.addWidget(self.preview_widget)
        self.splitter.setSizes([1200, 0])  # Start with preview pane hidden

        # Set the splitter as the central widget
        self.setCentralWidget(self.splitter)

        # Connect text change signal to update preview
        self.editor.textChanged.connect(self.update_markdown_preview)

        # Set default line and paragraph spacing
        self.set_default_spacing()

        # Create actions and toolbars
        self.create_actions()
        self.create_toolbars()

        # Set up the main window
        self.setWindowTitle('Clarity Editor')
        self.setGeometry(100, 100, 1200, 900)

        # Set default alignment
        self.set_default_alignment()

    def create_actions(self):
        """Create actions for the toolbar and menu."""
        # Formatting Actions
        self.bold_action = QAction('Bold', self)
        self.bold_action.triggered.connect(self.make_bold)
        self.bold_action.setShortcut(QKeySequence("Ctrl+B"))
        self.bold_action.setCheckable(True)

        self.italic_action = QAction('Italic', self)
        self.italic_action.triggered.connect(self.make_italic)
        self.italic_action.setShortcut(QKeySequence("Ctrl+I"))
        self.italic_action.setCheckable(True)

        self.underline_action = QAction('Underline', self)
        self.underline_action.triggered.connect(self.make_underline)
        self.underline_action.setShortcut(QKeySequence("Ctrl+U"))
        self.underline_action.setCheckable(True)

        # Alignment Actions
        self.left_align_action = QAction('Left', self)
        self.left_align_action.triggered.connect(self.align_left)
        self.left_align_action.setCheckable(True)

        self.center_align_action = QAction('Center', self)
        self.center_align_action.triggered.connect(self.align_center)
        self.center_align_action.setCheckable(True)

        self.right_align_action = QAction('Right', self)
        self.right_align_action.triggered.connect(self.align_right)
        self.right_align_action.setCheckable(True)

        self.justify_action = QAction('Justify', self)
        self.justify_action.triggered.connect(self.justify_text)
        self.justify_action.setCheckable(True)

        # List Actions
        self.bullet_list_action = QAction('Bullets', self)
        self.bullet_list_action.triggered.connect(self.insert_bullet_list)

        self.number_list_action = QAction('Numbering', self)
        self.number_list_action.triggered.connect(self.insert_numbered_list)

        # Font Selector
        self.font_selector = QComboBox(self)
        self.font_selector.addItems([
            'Avenir', 'Arial', 'Book Antiqua', 'Charter', 'Franklin Gothic',
            'Garamond', 'Gill Sans', 'Helvetica', 'Optima', 'Palatino',
            'Times New Roman'
        ])
        self.font_selector.currentTextChanged.connect(self.change_font)

        # Font Size Selector
        self.font_size_selector = QSpinBox(self)
        self.font_size_selector.setRange(4, 48)
        self.font_size_selector.setValue(14)
        self.font_size_selector.valueChanged.connect(self.change_font_size)

        # Line Spacing Selector
        self.line_spacing_selector = QComboBox(self)
        self.line_spacing_selector.addItems(['0.8', '0.9', '1', '1.15', '1.25', '1.3', '1.5', '2'])
        self.line_spacing_selector.setCurrentText('1.15')  # Set default line spacing
        self.line_spacing_selector.currentTextChanged.connect(self.set_line_spacing)

        # Paragraph Spacing Selectors
        self.paragraph_before_selector = QSpinBox(self)
        self.paragraph_before_selector.setRange(0, 50)
        self.paragraph_before_selector.setValue(6)
        self.paragraph_before_selector.setPrefix("Before: ")
        self.paragraph_before_selector.valueChanged.connect(self.set_paragraph_spacing)

        self.paragraph_after_selector = QSpinBox(self)
        self.paragraph_after_selector.setRange(0, 50)
        self.paragraph_after_selector.setValue(6)
        self.paragraph_after_selector.setPrefix("After: ")
        self.paragraph_after_selector.valueChanged.connect(self.set_paragraph_spacing)

        # Table Actions
        self.insert_table_action = QAction('Insert Table', self)
        self.insert_table_action.triggered.connect(self.insert_table)

        self.modify_table_action = QAction('Modify Table', self)
        self.modify_table_action.triggered.connect(self.modify_table)

        # File Actions
        self.new_action = QAction('New', self)
        self.new_action.triggered.connect(self.new_document)
        self.new_action.setShortcut(QKeySequence("Ctrl+N"))

        self.open_action = QAction('Open', self)
        self.open_action.triggered.connect(self.open_file)
        self.open_action.setShortcut(QKeySequence("Ctrl+O"))

        self.save_action = QAction('Save', self)
        self.save_action.triggered.connect(self.save_file)
        self.save_action.setShortcut(QKeySequence("Ctrl+S"))

        self.save_as_action = QAction('Save As', self)
        self.save_as_action.triggered.connect(self.save_file_as)
        self.save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))

        # Toggling dark mode View Actions
        self.toggle_dark_mode_action = QAction('Toggle Dark Mode', self)
        self.toggle_dark_mode_action.triggered.connect(self.toggle_dark_mode)

        # Find and Replace Actions
        self.find_action = QAction('Find', self)
        self.find_action.triggered.connect(self.show_find_replace_dialog)
        self.find_action.setShortcut(QKeySequence("Ctrl+F"))

        self.replace_action = QAction('Replace', self)
        self.replace_action.triggered.connect(self.show_find_replace_dialog)
        self.replace_action.setShortcut(QKeySequence("Ctrl+R"))

        # Markdown Actions
        self.md_bold_action = QAction('Bold', self)
        self.md_bold_action.triggered.connect(lambda: self.insert_markdown_syntax('**', '**'))

        self.md_italic_action = QAction('Italic', self)
        self.md_italic_action.triggered.connect(lambda: self.insert_markdown_syntax('*', '*'))

        self.md_code_action = QAction('Code', self)
        self.md_code_action.triggered.connect(lambda: self.insert_markdown_syntax('`', '`'))

        self.md_link_action = QAction('Link', self)
        self.md_link_action.triggered.connect(self.insert_markdown_link)

        self.md_image_action = QAction('Image', self)
        self.md_image_action.triggered.connect(self.insert_markdown_image)

    def create_toolbars(self):
        """Create toolbars and add actions."""
        # Format Toolbar
        self.format_toolbar = QToolBar('Format')
        self.addToolBar(Qt.TopToolBarArea, self.format_toolbar)
        self.format_toolbar.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        self.format_toolbar.setMovable(False)

        self.format_toolbar.addAction(self.bold_action)
        self.format_toolbar.addAction(self.italic_action)
        self.format_toolbar.addAction(self.underline_action)
        self.format_toolbar.addSeparator()
        self.format_toolbar.addAction(self.left_align_action)
        self.format_toolbar.addAction(self.center_align_action)
        self.format_toolbar.addAction(self.right_align_action)
        self.format_toolbar.addAction(self.justify_action)
        self.format_toolbar.addSeparator()
        self.format_toolbar.addAction(self.bullet_list_action)
        self.format_toolbar.addAction(self.number_list_action)
        self.format_toolbar.addSeparator()
        self.format_toolbar.addWidget(QLabel("Font:"))
        self.format_toolbar.addWidget(self.font_selector)
        self.format_toolbar.addWidget(QLabel("Size:"))
        self.format_toolbar.addWidget(self.font_size_selector)

        # Insert a toolbar break to start a new row
        self.addToolBarBreak(Qt.TopToolBarArea)

        # Additional Toolbar
        self.additional_toolbar = QToolBar('Additional')
        self.addToolBar(Qt.TopToolBarArea, self.additional_toolbar)
        self.additional_toolbar.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        self.additional_toolbar.setMovable(False)

        self.additional_toolbar.addWidget(QLabel("Line Spacing:"))
        self.additional_toolbar.addWidget(self.line_spacing_selector)
        self.additional_toolbar.addWidget(self.paragraph_before_selector)
        self.additional_toolbar.addWidget(self.paragraph_after_selector)
        self.additional_toolbar.addSeparator()
        self.additional_toolbar.addAction(self.insert_table_action)
        self.additional_toolbar.addAction(self.modify_table_action)
        self.additional_toolbar.addSeparator()
        self.additional_toolbar.addAction(self.new_action)
        self.additional_toolbar.addAction(self.open_action)
        self.additional_toolbar.addAction(self.save_action)
        self.additional_toolbar.addAction(self.save_as_action)
        self.additional_toolbar.addSeparator()
        self.additional_toolbar.addAction(self.find_action)
        self.additional_toolbar.addAction(self.replace_action)
        self.additional_toolbar.addSeparator()
        self.additional_toolbar.addAction(self.toggle_dark_mode_action)

        # Markdown Toolbar
        self.markdown_toolbar = QToolBar('Markdown')
        self.addToolBar(Qt.TopToolBarArea, self.markdown_toolbar)
        self.markdown_toolbar.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        self.markdown_toolbar.setMovable(False)

        self.markdown_toolbar.addAction(self.md_bold_action)
        self.markdown_toolbar.addAction(self.md_italic_action)
        self.markdown_toolbar.addAction(self.md_code_action)
        self.markdown_toolbar.addAction(self.md_link_action)
        self.markdown_toolbar.addAction(self.md_image_action)

        # Start with the Markdown toolbar hidden
        self.markdown_toolbar.setVisible(False)

    def set_default_spacing(self):
        """Apply default line and paragraph spacing to the entire document."""
        cursor = self.editor.textCursor()
        cursor.select(QTextCursor.Document)
        block_format = QTextBlockFormat()
        block_format.setLineHeight(115, QTextBlockFormat.ProportionalHeight)  # 1.15 line spacing
        block_format.setTopMargin(6)  # 6 points before paragraph
        block_format.setBottomMargin(6)  # 6 points after paragraph
        cursor.mergeBlockFormat(block_format)
        self.editor.setTextCursor(cursor)

    def set_default_alignment(self):
        """Set the default text alignment to justified."""
        cursor = self.editor.textCursor()
        cursor.select(QTextCursor.Document)
        block_format = QTextBlockFormat()
        block_format.setAlignment(Qt.AlignJustify)
        cursor.mergeBlockFormat(block_format)
        self.editor.setTextCursor(cursor)

    def mark_as_modified(self):
        """Mark the document as modified."""
        self.is_modified = True
        if self.current_file_path:
            self.setWindowTitle(f"Clarity Editor - {os.path.basename(self.current_file_path)}*")
        else:
            self.setWindowTitle("Clarity Editor - Untitled*")

    def make_bold(self):
        """Toggle bold formatting."""
        fmt = self.editor.currentCharFormat()
        fmt.setFontWeight(QFont.Bold if not fmt.fontWeight() == QFont.Bold else QFont.Normal)
        self.editor.setCurrentCharFormat(fmt)
        self.bold_action.setChecked(fmt.fontWeight() == QFont.Bold)
        self.editor.setFocus()

    def make_italic(self):
        """Toggle italic formatting."""
        fmt = self.editor.currentCharFormat()
        fmt.setFontItalic(not fmt.fontItalic())
        self.editor.setCurrentCharFormat(fmt)
        self.italic_action.setChecked(fmt.fontItalic())
        self.editor.setFocus()

    def make_underline(self):
        """Toggle underline formatting."""
        fmt = self.editor.currentCharFormat()
        fmt.setFontUnderline(not fmt.fontUnderline())
        self.editor.setCurrentCharFormat(fmt)
        self.underline_action.setChecked(fmt.fontUnderline())
        self.editor.setFocus()

    def align_left(self):
        """Align text to the left."""
        self.set_alignment(Qt.AlignLeft)
        self.update_alignment_buttons()
        self.editor.setFocus()

    def align_center(self):
        """Center align text."""
        self.set_alignment(Qt.AlignCenter)
        self.update_alignment_buttons()
        self.editor.setFocus()

    def align_right(self):
        """Align text to the right."""
        self.set_alignment(Qt.AlignRight)
        self.update_alignment_buttons()
        self.editor.setFocus()

    def justify_text(self):
        """Justify text."""
        self.set_alignment(Qt.AlignJustify)
        self.update_alignment_buttons()
        self.editor.setFocus()

    def set_alignment(self, alignment):
        """Set the alignment for the current paragraph."""
        cursor = self.editor.textCursor()
        block_format = cursor.blockFormat()
        block_format.setAlignment(alignment)
        cursor.setBlockFormat(block_format)
        self.editor.setTextCursor(cursor)

    def update_alignment_buttons(self):
        """Update the checked state of alignment actions."""
        alignment = self.editor.textCursor().blockFormat().alignment()
        self.left_align_action.setChecked(alignment == Qt.AlignLeft)
        self.center_align_action.setChecked(alignment == Qt.AlignCenter)
        self.right_align_action.setChecked(alignment == Qt.AlignRight)
        self.justify_action.setChecked(alignment == Qt.AlignJustify)

    def insert_bullet_list(self):
        """Insert a bulleted list."""
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        list_format = QTextListFormat()
        list_format.setStyle(QTextListFormat.ListDisc)  # Bullet list
        cursor.createList(list_format)
        cursor.endEditBlock()
        self.editor.setFocus()

    def insert_numbered_list(self):
        """Insert a numbered list."""
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        list_format = QTextListFormat()
        list_format.setStyle(QTextListFormat.ListDecimal)  # Numbered list
        cursor.createList(list_format)
        cursor.endEditBlock()
        self.editor.setFocus()

    def change_font(self, font_name):
        """Change the font family."""
        fmt = self.editor.currentCharFormat()
        fmt.setFontFamily(font_name)
        self.editor.setCurrentCharFormat(fmt)
        self.editor.setFocus()

    def change_font_size(self, size):
        """Change the font size."""
        fmt = self.editor.currentCharFormat()
        fmt.setFontPointSize(size)
        self.editor.setCurrentCharFormat(fmt)
        self.editor.setFocus()

    def set_line_spacing(self, spacing_value):
        """Set the line spacing."""
        try:
            spacing = float(spacing_value) * 100
            cursor = self.editor.textCursor()
            block_format = cursor.blockFormat()
            block_format.setLineHeight(spacing, QTextBlockFormat.ProportionalHeight)
            cursor.setBlockFormat(block_format)
            self.editor.setTextCursor(cursor)
            self.editor.setFocus()
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid line spacing value.")

    def set_paragraph_spacing(self):
        """Set the paragraph spacing before and after."""
        cursor = self.editor.textCursor()
        block_format = cursor.blockFormat()
        block_format.setTopMargin(self.paragraph_before_selector.value())
        block_format.setBottomMargin(self.paragraph_after_selector.value())
        cursor.setBlockFormat(block_format)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()

    def insert_table(self):
        """Insert a table with user-specified rows and columns."""
        # Ask the user for rows and columns
        rows, ok1 = QInputDialog.getInt(self, 'Insert Table', 'Number of rows:', 2, 1, 100)
        if not ok1:
            return
        columns, ok2 = QInputDialog.getInt(self, 'Insert Table', 'Number of columns:', 2, 1, 100)
        if not ok2:
            return
        cursor = self.editor.textCursor()
        fmt = QTextTableFormat()
        fmt.setBorder(1)
        fmt.setCellPadding(5)  # Set padding for better visibility
        fmt.setCellSpacing(2)  # Set spacing between cells
        cursor.insertTable(rows, columns, fmt)
        self.editor.setFocus()

    def modify_table(self):
        """Modify the current table by adding or removing rows and columns."""
        cursor = self.editor.textCursor()
        table = cursor.currentTable()
        if table is None:
            QMessageBox.warning(self, 'No Table Found', 'No table found at the current cursor position.')
            return

        # Ask for the number of rows to add or remove
        rows_to_modify, ok1 = QInputDialog.getInt(
            self, 'Modify Table', 'Number of rows to add (+) or remove (-):', 0, -table.rows(), 100
        )
        if ok1 and rows_to_modify != 0:
            if rows_to_modify > 0:
                table.appendRows(rows_to_modify)
            elif rows_to_modify < 0:
                rows_to_remove = min(abs(rows_to_modify), table.rows())
                table.removeRows(table.rows() - rows_to_remove, rows_to_remove)

        # Ask for the number of columns to add or remove
        columns_to_modify, ok2 = QInputDialog.getInt(
            self, 'Modify Table', 'Number of columns to add (+) or remove (-):', 0, -table.columns(), 100
        )
        if ok2 and columns_to_modify != 0:
            if columns_to_modify > 0:
                table.appendColumns(columns_to_modify)
            elif columns_to_modify < 0:
                cols_to_remove = min(abs(columns_to_modify), table.columns())
                table.removeColumns(table.columns() - cols_to_remove, cols_to_remove)
        self.editor.setFocus()

    def show_find_replace_dialog(self):
        """Show the find and replace dialog."""
        if not hasattr(self, 'find_replace_dialog'):
            self.find_replace_dialog = FindReplaceDialog(self)
        self.find_replace_dialog.show()
        self.find_replace_dialog.raise_()
        self.find_replace_dialog.activateWindow()

    def save_file(self):
        """Save the current document. If it's a new document, prompt 'Save As'."""
        if self.current_file_path:
            try:
                self.save_content(self.current_file_path)
                self.is_modified = False  # Mark as not modified after saving
                self.statusBar().showMessage(f"Saved: {os.path.basename(self.current_file_path)}")
                self.setWindowTitle(f"Clarity Editor - {os.path.basename(self.current_file_path)}")
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
                return False
        else:
            # Otherwise, save as a new file
            return self.save_file_as()

    def save_file_as(self):
        """Save the document as a new file with selected format."""
        # Ask user to select file type
        save_options = ['html', 'md', 'txt', 'pdf', 'odt']

        file_type, ok = QInputDialog.getItem(
            self, 'Save As', 'Select file type:', save_options, 0, False
        )
        if not ok:
            return False  # User cancelled

        # Define file filter based on selected file type
        filters = {
            'html': "HTML Files (*.html)",
            'md': "Markdown Files (*.md)",
            'txt': "Text Files (*.txt)",
            'pdf': "PDF Files (*.pdf)",
            'odt': "ODF Text Files (*.odt)"
        }
        filter_selected = filters.get(file_type, "All Files (*)")

        # Open a file dialog to select save location
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save File As", f"document.{file_type}", filter_selected, options=QFileDialog.Options()
        )

        if file_name:
            # Automatically append the correct extension if not provided
            if not file_name.lower().endswith(f'.{file_type}'):
                file_name += f'.{file_type}'

            try:
                self.save_content(file_name)
                self.current_file_path = file_name  # Store the current file path
                self.is_modified = False  # Mark as not modified after saving
                self.statusBar().showMessage(f"Saved: {os.path.basename(file_name)}")
                self.setWindowTitle(f"Clarity Editor - {os.path.basename(self.current_file_path)}")
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
                return False
        else:
            return False  # User cancelled

    def save_content(self, file_name):
        """Save the content to the specified file."""
        if file_name.lower().endswith('.pdf'):
            self.save_as_pdf(file_name)
        elif file_name.lower().endswith('.html'):
            content = self.editor.document().toHtml()
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(content)
        elif file_name.lower().endswith('.md'):
            markdown_text = self.editor.toPlainText()
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(markdown_text)
        elif file_name.lower().endswith('.odt'):
            self.save_as_odt(file_name)
        else:  # Save as plain text
            content = self.editor.toPlainText()
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(content)

    def save_as_pdf(self, file_name):
        """Save the document as a PDF (.pdf) file."""
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(file_name)
        if self.current_markdown is not None:
            # Render the markdown to HTML and print it
            markdown_text = self.editor.toPlainText()
            html_content = markdown.markdown(
                markdown_text,
                extensions=[
                    'extra',
                    'codehilite',
                    'toc',
                    'nl2br',
                ]
            )
            doc = QTextDocument()
            css = '''
            <style>
            /* Code block styling */
            .codehilite {
                background-color: #f8f8f8;
                border: 1px solid #ccc;
                padding: 5px;
                overflow-x: auto;
            }
            /* Table styling */
            table {
                border-collapse: collapse;
                width: 100%;
            }
            th, td {
                border: 1px solid #ccc;
                padding: 5px;
            }
            </style>
            '''
            doc.setHtml(css + html_content)
            doc.print_(printer)
        else:
            self.editor.document().print_(printer)

    def save_as_odt(self, file_name):
        """Save the document as an ODT file using QTextDocumentWriter."""
        try:
            writer = QTextDocumentWriter(file_name, b'ODF')
            success = writer.write(self.editor.document())
            if not success:
                raise IOError("Failed to write ODT file.")
        except Exception as e:
            raise e

    def open_file(self):
        """Open an existing file."""
        # Define supported formats
        supported_formats = "Markdown Files (*.md);;HTML Files (*.html);;Text Files (*.txt);;ODF Text Files (*.odt);;All Files (*)"

        # Open a file dialog to select a file to open
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", supported_formats, options=QFileDialog.Options()
        )
        if not file_name:
            return  # Return if no file is selected

        # Check for unsaved changes
        if self.is_modified:
            reply = QMessageBox.question(
                self, 'Unsaved Work',
                'Do you want to save the current document before opening a new one?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                if not self.save_file():
                    return  # If saving was cancelled or failed, do not proceed
            elif reply == QMessageBox.Cancel:
                return  # Do not proceed if cancel is selected

        # Determine the file type and read the content
        try:
            if file_name.lower().endswith('.md'):
                with open(file_name, 'r', encoding='utf-8') as file:
                    markdown_text = file.read()
                    self.editor.setPlainText(markdown_text)
                    self.current_markdown = markdown_text
                    self.update_markdown_preview()
                    # Show the Markdown toolbar
                    self.markdown_toolbar.setVisible(True)
                    # Adjust splitter sizes
                    self.splitter.setSizes([600, 600])
                self.setWindowTitle(f"Clarity Editor - {os.path.basename(file_name)}")
            elif file_name.lower().endswith('.odt'):
                # Inform the user
                QMessageBox.information(self, "ODT Support", "Opening ODT files will only extract plain text without formatting.")
                # Proceed to extract text
                odt_doc = load(file_name)
                all_paras = odt_doc.getElementsByType(text.P)
                content = ''
                for para in all_paras:
                    content += teletype.extractText(para) + '\n'
                self.editor.setPlainText(content)
                self.current_markdown = None  # Reset current markdown
                self.preview_widget.clear()
                # Hide the Markdown toolbar
                self.markdown_toolbar.setVisible(False)
                # Adjust splitter sizes
                self.splitter.setSizes([1200, 0])
                self.setWindowTitle(f"Clarity Editor - {os.path.basename(file_name)}")
            elif file_name.lower().endswith('.html'):
                with open(file_name, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.editor.setHtml(content)
                self.current_markdown = None  # Reset current markdown
                self.preview_widget.clear()
                # Hide the Markdown toolbar
                self.markdown_toolbar.setVisible(False)
                # Adjust splitter sizes
                self.splitter.setSizes([1200, 0])
                self.setWindowTitle(f"Clarity Editor - {os.path.basename(file_name)}")
            else:
                with open(file_name, 'r', encoding='utf-8') as file:
                    content = file.read()
                    self.editor.setPlainText(content)
                self.current_markdown = None  # Reset current markdown
                self.preview_widget.clear()
                # Hide the Markdown toolbar
                self.markdown_toolbar.setVisible(False)
                # Adjust splitter sizes
                self.splitter.setSizes([1200, 0])
                self.setWindowTitle(f"Clarity Editor - {os.path.basename(file_name)}")

            self.current_file_path = file_name  # Store the path of the currently opened file
            self.is_modified = False  # Mark as not modified initially
            self.statusBar().showMessage(f"Opened: {os.path.basename(file_name)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while opening the file: {str(e)}")

    def new_document(self):
        """Create a new document, prompting to save if there are unsaved changes."""
        # Check if there is unsaved work
        if self.is_modified:
            reply = QMessageBox.question(
                self, 'Unsaved Work',
                'Do you want to save the current document before creating a new one?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                if not self.save_file():
                    return  # If saving was cancelled or failed, do not proceed
            elif reply == QMessageBox.Cancel:
                return  # Do not proceed if cancel is selected

        # Clear the editor for a new document
        self.editor.clear()
        self.current_file_path = None  # Reset the current file path
        self.is_modified = False  # Reset modified status
        self.statusBar().showMessage("New document created.")

        # Reset formatting to defaults
        self.set_default_alignment()
        self.set_default_spacing()

        # Reset current markdown and clear preview
        self.current_markdown = None
        self.preview_widget.clear()
        # Hide the Markdown toolbar
        self.markdown_toolbar.setVisible(False)
        # Adjust splitter sizes
        self.splitter.setSizes([1200, 0])
        self.setWindowTitle("Clarity Editor - Untitled")

    def update_format_selection(self):
        """Update the format toolbar based on the current cursor position."""
        try:
            cursor = self.editor.textCursor()
            char_format = cursor.charFormat()
            block_format = cursor.blockFormat()

            # Update font family
            current_font_family = char_format.fontFamily()
            if current_font_family:
                index = self.font_selector.findText(current_font_family)
                if index >= 0:
                    self.font_selector.blockSignals(True)
                    self.font_selector.setCurrentIndex(index)
                    self.font_selector.blockSignals(False)

            # Update font size
            current_font_size = char_format.fontPointSize()
            if current_font_size > 0:
                self.font_size_selector.blockSignals(True)
                self.font_size_selector.setValue(int(current_font_size))
                self.font_size_selector.blockSignals(False)

            # Update alignment buttons
            alignment = block_format.alignment()
            self.left_align_action.setChecked(alignment == Qt.AlignLeft)
            self.center_align_action.setChecked(alignment == Qt.AlignCenter)
            self.right_align_action.setChecked(alignment == Qt.AlignRight)
            self.justify_action.setChecked(alignment == Qt.AlignJustify)

            # Update bold, italic, underline buttons
            self.bold_action.setChecked(char_format.fontWeight() == QFont.Bold)
            self.italic_action.setChecked(char_format.fontItalic())
            self.underline_action.setChecked(char_format.fontUnderline())

        except Exception as e:
            QMessageBox.critical(self, "Format Selection Error", f"Failed to update format selection: {e}")

    def closeEvent(self, event):
        """Prompt the user to save before exiting."""
        if self.is_modified:
            reply = QMessageBox.question(
                self, 'Unsaved Work',
                'Do you want to save the current document before exiting?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                if not self.save_file():
                    event.ignore()
                    return
            elif reply == QMessageBox.Cancel:
                event.ignore()
                return
        event.accept()

    def toggle_dark_mode(self):
        """Toggle dark mode for the application."""
        if getattr(self, 'dark_mode', False):
            self.set_light_mode()
            self.dark_mode = False
        else:
            self.set_dark_mode()
            self.dark_mode = True

    # Dark mode styling

    def set_dark_mode(self):
        """Switch to dark mode."""
        QApplication.setStyle("Fusion")
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        # Set the editor's text color to white and background to dark
        palette = self.editor.palette()
        palette.setColor(QPalette.Text, QColor("white"))
        palette.setColor(QPalette.Base, QColor("#2b2b2b"))
        self.editor.setPalette(palette)

        # Apply to preview widget
        palette = self.preview_widget.palette()
        palette.setColor(QPalette.Text, QColor("white"))
        palette.setColor(QPalette.Base, QColor("#2b2b2b"))
        self.preview_widget.setPalette(palette)

    def set_light_mode(self):
        """Switch to light mode."""
        QApplication.setPalette(QApplication.style().standardPalette())
        self.setStyleSheet("")

        # Reset the editor's text color to black and background to white
        palette = self.editor.palette()
        palette.setColor(QPalette.Text, QColor("black"))
        palette.setColor(QPalette.Base, QColor("white"))
        self.editor.setPalette(palette)

        # Apply to preview widget
        palette = self.preview_widget.palette()
        palette.setColor(QPalette.Text, QColor("black"))
        palette.setColor(QPalette.Base, QColor("white"))
        self.preview_widget.setPalette(palette)

    def update_markdown_preview(self):
        """Update the Markdown preview pane."""
        if self.current_markdown is not None:
            markdown_text = self.editor.toPlainText()
            html_content = markdown.markdown(
                markdown_text,
                extensions=[
                    'extra',
                    'codehilite',
                    'toc',
                    'nl2br',
                ]
            )
            # Add CSS styles
            css = '''
            <style>
            /* Code block styling */
            .codehilite {
                background-color: #f8f8f8;
                border: 1px solid #ccc;
                padding: 5px;
                overflow-x: auto;
            }
            /* Table styling */
            table {
                border-collapse: collapse;
                width: 100%;
            }
            th, td {
                border: 1px solid #ccc;
                padding: 5px;
            }
            </style>
            '''
            self.preview_widget.setHtml(css + html_content)
        else:
            self.preview_widget.clear()

    def insert_markdown_syntax(self, start_syntax, end_syntax):
        """Insert Markdown syntax around the selected text."""
        cursor = self.editor.textCursor()
        selected_text = cursor.selectedText()
        new_text = f"{start_syntax}{selected_text}{end_syntax}"
        cursor.insertText(new_text)
        self.editor.setFocus()

    def insert_markdown_link(self):
        """Insert a Markdown link."""
        text, ok = QInputDialog.getText(self, 'Insert Link', 'Display Text:')
        if not ok:
            return
        url, ok = QInputDialog.getText(self, 'Insert Link', 'URL:')
        if not ok:
            return
        markdown_link = f"[{text}]({url})"
        cursor = self.editor.textCursor()
        cursor.insertText(markdown_link)
        self.editor.setFocus()

    def insert_markdown_image(self):
        """Insert a Markdown image."""
        alt_text, ok = QInputDialog.getText(self, 'Insert Image', 'Alt Text:')
        if not ok:
            return
        image_url, ok = QInputDialog.getText(self, 'Insert Image', 'Image URL:')
        if not ok:
            return
        markdown_image = f"![{alt_text}]({image_url})"
        cursor = self.editor.textCursor()
        cursor.insertText(markdown_image)
        self.editor.setFocus()

def main():
    """Initialize and run the Clarity Editor application."""
    app = QApplication(sys.argv)

    # Set Palatino 14 as the global font for the entire interface
    app.setFont(QFont('Palatino', 14))

    window = ClarityEditor()
    window.resize(1200, 900)
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
