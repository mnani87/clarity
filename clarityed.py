import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton, QComboBox, QFileDialog,
    QSpinBox, QInputDialog, QMessageBox, QAction, QToolBar, QLabel, QDialog, QVBoxLayout, QLineEdit, QHBoxLayout
)
from PyQt5.QtGui import (
    QFont, QTextCursor, QTextTableFormat, QKeySequence, QTextBlockFormat,
    QTextListFormat, QTextCharFormat, QIcon, QTextDocument
)
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrinter
import markdown
import html2text

class ClarityNotes(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize state
        self.is_modified = False  # Track if the document is modified
        self.current_file_path = None  # Track the path of the currently opened file

        # Create the main text editor with default font Charter
        self.editor = QTextEdit()
        self.set_default_font()
        self.editor.cursorPositionChanged.connect(self.update_font_selection)  # Connect cursor movement to font update
        self.editor.textChanged.connect(self.mark_as_modified)  # Track modifications

        # Set default line and paragraph spacing
        self.set_default_spacing()

        # Create toolbar actions with global shortcuts
        self.create_actions()
        self.create_toolbars()
        self.create_menus()

        # Set up the status bar
        self.status_bar = self.statusBar()
        self.status_label = QLabel("")
        self.status_bar.addWidget(self.status_label)
        self.word_count_label = QLabel("Words: 0 | Characters: 0")
        self.status_bar.addPermanentWidget(self.word_count_label)
        self.editor.textChanged.connect(self.update_word_count)

        # Set up the main window
        self.setWindowTitle('Clarity Notes: v1.0')
        self.setGeometry(100, 100, 800, 600)

        # Set the QTextEdit as the central widget
        self.setCentralWidget(self.editor)

        # Handle close event to prompt saving
        self.setWindowIcon(QIcon())  # Set an icon if available

    def set_default_font(self):
        """Set Charter as the default font."""
        # Verify if Charter is available
        available_fonts = QFont().families()
        if 'Charter' in available_fonts:
            default_font = 'Charter'
        else:
            default_font = 'Times New Roman'  # Fallback to a common font

        self.editor.setFont(QFont(default_font, 12))

    def create_actions(self):
        """Create actions for formatting and file operations with shortcuts."""
        # Formatting Actions
        self.bold_action = QAction('Bold', self)
        self.bold_action.setShortcut(QKeySequence("Ctrl+B"))
        self.bold_action.triggered.connect(self.make_bold)

        self.italic_action = QAction('Italic', self)
        self.italic_action.setShortcut(QKeySequence("Ctrl+I"))
        self.italic_action.triggered.connect(self.make_italic)

        self.underline_action = QAction('Underline', self)
        self.underline_action.setShortcut(QKeySequence("Ctrl+U"))
        self.underline_action.triggered.connect(self.make_underline)

        self.align_left_action = QAction('Align Left', self)
        self.align_left_action.setShortcut(QKeySequence("Ctrl+L"))
        self.align_left_action.triggered.connect(self.align_left)

        self.align_center_action = QAction('Align Center', self)
        self.align_center_action.setShortcut(QKeySequence("Ctrl+E"))
        self.align_center_action.triggered.connect(self.align_center)

        self.align_right_action = QAction('Align Right', self)
        self.align_right_action.setShortcut(QKeySequence("Ctrl+R"))
        self.align_right_action.triggered.connect(self.align_right)

        self.align_justify_action = QAction('Justify', self)
        self.align_justify_action.setShortcut(QKeySequence("Ctrl+J"))
        self.align_justify_action.triggered.connect(self.align_justify)

        # Edit Actions
        self.undo_action = QAction('Undo', self)
        self.undo_action.setShortcut(QKeySequence("Ctrl+Z"))
        self.undo_action.triggered.connect(self.editor.undo)

        self.redo_action = QAction('Redo', self)
        self.redo_action.setShortcut(QKeySequence("Ctrl+Y"))
        self.redo_action.triggered.connect(self.editor.redo)

        self.find_replace_action = QAction('Find and Replace', self)
        self.find_replace_action.setShortcut(QKeySequence("Ctrl+F"))
        self.find_replace_action.triggered.connect(self.find_replace_dialog)

        # File Operations Actions
        self.save_action = QAction('Save', self)
        self.save_action.setShortcut(QKeySequence("Ctrl+S"))
        self.save_action.triggered.connect(self.save_file)

        self.open_action = QAction('Open', self)
        self.open_action.setShortcut(QKeySequence("Ctrl+O"))
        self.open_action.triggered.connect(self.open_file)

        self.new_action = QAction('New', self)
        self.new_action.setShortcut(QKeySequence("Ctrl+N"))
        self.new_action.triggered.connect(self.new_document)

        self.save_as_action = QAction('Save As', self)
        self.save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.save_as_action.triggered.connect(self.save_file_as_text)

        self.save_md_action = QAction('Save as Markdown', self)
        self.save_md_action.triggered.connect(self.save_file_as_markdown)

        self.save_html_action = QAction('Save as HTML', self)
        self.save_html_action.triggered.connect(self.save_file_as_html)

        self.save_pdf_action = QAction('Save as PDF', self)
        self.save_pdf_action.triggered.connect(self.save_file_as_pdf)

        self.about_action = QAction('About', self)
        self.about_action.triggered.connect(self.show_about_dialog)

        # Exit Action
        self.exit_action = QAction('Exit', self)
        self.exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        self.exit_action.triggered.connect(self.close)

    def create_toolbars(self):
        """Create and organize toolbars into multiple rows for better layout."""
        # Formatting Toolbar
        formatting_toolbar = QToolBar("Formatting Toolbar")
        self.addToolBar(formatting_toolbar)

        # Add formatting actions
        formatting_toolbar.addAction(self.bold_action)
        formatting_toolbar.addAction(self.italic_action)
        formatting_toolbar.addAction(self.underline_action)

        # Add alignment actions
        formatting_toolbar.addAction(self.align_left_action)
        formatting_toolbar.addAction(self.align_center_action)
        formatting_toolbar.addAction(self.align_right_action)
        formatting_toolbar.addAction(self.align_justify_action)

        # Add list buttons
        self.bullet_button = QPushButton('Bullets')
        self.bullet_button.clicked.connect(self.insert_bullet_list)
        formatting_toolbar.addWidget(self.bullet_button)

        self.numbering_button = QPushButton('Numbering')
        self.numbering_button.clicked.connect(self.insert_numbered_list)
        formatting_toolbar.addWidget(self.numbering_button)

        # Font Toolbar
        font_toolbar = QToolBar("Font Toolbar")
        self.addToolBar(font_toolbar)

        # Since we're only using Charter, we'll remove the font selector
        # and keep only the font size spinbox
        font_toolbar.addWidget(QLabel("Font Size: "))
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(8, 48)
        self.font_size_spinbox.setValue(12)
        self.font_size_spinbox.valueChanged.connect(self.change_font_size)
        font_toolbar.addWidget(self.font_size_spinbox)

        # Spacing Toolbar
        spacing_toolbar = QToolBar("Spacing Toolbar")
        self.addToolBar(spacing_toolbar)

        # Add line spacing combo box
        self.line_spacing_combo = QComboBox()
        self.line_spacing_combo.addItems(['0.8', '0.9', '1', '1.15', '1.25', '1.3', '1.5', '2'])
        self.line_spacing_combo.setCurrentText('1.15')  # Set default line spacing
        self.line_spacing_combo.currentTextChanged.connect(self.set_line_spacing)
        spacing_toolbar.addWidget(QLabel("Line Spacing: "))
        spacing_toolbar.addWidget(self.line_spacing_combo)

        # Add paragraph spacing spinboxes
        self.paragraph_before_spinbox = QSpinBox()
        self.paragraph_before_spinbox.setRange(0, 50)
        self.paragraph_before_spinbox.setValue(6)  # Default value for paragraph spacing before
        self.paragraph_before_spinbox.setPrefix("Before: ")
        self.paragraph_before_spinbox.valueChanged.connect(self.set_paragraph_spacing)
        spacing_toolbar.addWidget(self.paragraph_before_spinbox)

        self.paragraph_after_spinbox = QSpinBox()
        self.paragraph_after_spinbox.setRange(0, 50)
        self.paragraph_after_spinbox.setValue(6)  # Default value for paragraph spacing after
        self.paragraph_after_spinbox.setPrefix("After: ")
        self.paragraph_after_spinbox.valueChanged.connect(self.set_paragraph_spacing)
        spacing_toolbar.addWidget(self.paragraph_after_spinbox)

        # Tables Toolbar
        tables_toolbar = QToolBar("Tables Toolbar")
        self.addToolBar(tables_toolbar)

        # Add table buttons
        self.table_button = QPushButton('Insert Table')
        self.table_button.clicked.connect(self.insert_table)
        tables_toolbar.addWidget(self.table_button)

        self.modify_table_button = QPushButton('Modify Table')
        self.modify_table_button.clicked.connect(self.modify_table)
        tables_toolbar.addWidget(self.modify_table_button)

        # Edit Toolbar
        edit_toolbar = QToolBar("Edit Toolbar")
        self.addToolBar(edit_toolbar)

        edit_toolbar.addAction(self.undo_action)
        edit_toolbar.addAction(self.redo_action)
        edit_toolbar.addAction(self.find_replace_action)

        # File Operations Toolbar
        file_toolbar = QToolBar("File Toolbar")
        self.addToolBar(file_toolbar)

        # Add file operation buttons
        self.new_document_button = QPushButton('New Document')
        self.new_document_button.clicked.connect(self.new_document)
        file_toolbar.addWidget(self.new_document_button)

        self.open_button = QPushButton('Open')
        self.open_button.clicked.connect(self.open_file)
        file_toolbar.addWidget(self.open_button)

        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_file)
        file_toolbar.addWidget(self.save_button)

        self.save_as_button = QPushButton('Save As')
        self.save_as_button.clicked.connect(self.save_file_as_text)
        file_toolbar.addWidget(self.save_as_button)

        self.save_md_button = QPushButton('Save as Markdown')
        self.save_md_button.clicked.connect(self.save_file_as_markdown)
        file_toolbar.addWidget(self.save_md_button)

        self.save_html_button = QPushButton('Save as HTML')
        self.save_html_button.clicked.connect(self.save_file_as_html)
        file_toolbar.addWidget(self.save_html_button)

        self.save_pdf_button = QPushButton('Save as PDF')
        self.save_pdf_button.clicked.connect(self.save_file_as_pdf)
        file_toolbar.addWidget(self.save_pdf_button)

        # Add actions to enable global shortcuts
        self.add_actions_to_shortcuts()

    def create_menus(self):
        """Create menus for additional functionalities."""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu('File')
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # Edit Menu
        edit_menu = menubar.addMenu('Edit')
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addAction(self.find_replace_action)

        # Format Menu
        format_menu = menubar.addMenu('Format')
        format_menu.addAction(self.bold_action)
        format_menu.addAction(self.italic_action)
        format_menu.addAction(self.underline_action)
        format_menu.addSeparator()
        format_menu.addAction(self.align_left_action)
        format_menu.addAction(self.align_center_action)
        format_menu.addAction(self.align_right_action)
        format_menu.addAction(self.align_justify_action)

        # Help Menu
        help_menu = menubar.addMenu('Help')
        help_menu.addAction(self.about_action)

    def add_actions_to_shortcuts(self):
        """Add actions to the main window for global shortcuts."""
        self.addAction(self.bold_action)
        self.addAction(self.italic_action)
        self.addAction(self.underline_action)
        self.addAction(self.align_left_action)
        self.addAction(self.align_center_action)
        self.addAction(self.align_right_action)
        self.addAction(self.align_justify_action)
        self.addAction(self.undo_action)
        self.addAction(self.redo_action)
        self.addAction(self.find_replace_action)
        self.addAction(self.save_action)
        self.addAction(self.open_action)
        self.addAction(self.new_action)
        self.addAction(self.save_as_action)
        self.addAction(self.exit_action)

    def set_default_spacing(self):
        """Apply default line and paragraph spacing to the entire document."""
        cursor = self.editor.textCursor()
        cursor.select(QTextCursor.Document)
        block_format = QTextBlockFormat()
        block_format.setLineHeight(115, QTextBlockFormat.ProportionalHeight)  # 1.15 line spacing
        block_format.setTopMargin(6)  # 6 points before paragraph
        block_format.setBottomMargin(6)  # 6 points after paragraph
        block_format.setAlignment(Qt.AlignLeft)
        cursor.mergeBlockFormat(block_format)
        self.editor.setTextCursor(cursor)

    def mark_as_modified(self):
        """Mark the document as modified."""
        self.is_modified = True

    def make_bold(self):
        """Toggle bold formatting."""
        try:
            cursor = self.editor.textCursor()
            if cursor.hasSelection():
                fmt = QTextCharFormat()
                fmt.setFontWeight(QFont.Bold if not self.editor.fontWeight() == QFont.Bold else QFont.Normal)
                cursor.mergeCharFormat(fmt)
            else:
                fmt = self.editor.currentCharFormat()
                fmt.setFontWeight(QFont.Bold if not self.editor.fontWeight() == QFont.Bold else QFont.Normal)
                self.editor.setCurrentCharFormat(fmt)
        except Exception as e:
            QMessageBox.critical(self, "Bold Error", f"Failed to toggle bold: {e}")

    def make_italic(self):
        """Toggle italic formatting."""
        try:
            cursor = self.editor.textCursor()
            fmt = QTextCharFormat()
            fmt.setFontItalic(not self.editor.fontItalic())
            if cursor.hasSelection():
                cursor.mergeCharFormat(fmt)
            else:
                self.editor.setCurrentCharFormat(fmt)
        except Exception as e:
            QMessageBox.critical(self, "Italic Error", f"Failed to toggle italic: {e}")

    def make_underline(self):
        """Toggle underline formatting."""
        try:
            cursor = self.editor.textCursor()
            fmt = QTextCharFormat()
            fmt.setFontUnderline(not self.editor.fontUnderline())
            if cursor.hasSelection():
                cursor.mergeCharFormat(fmt)
            else:
                self.editor.setCurrentCharFormat(fmt)
        except Exception as e:
            QMessageBox.critical(self, "Underline Error", f"Failed to toggle underline: {e}")

    def align_left(self):
        """Align text to the left."""
        self.editor.setAlignment(Qt.AlignLeft)

    def align_center(self):
        """Center align text."""
        self.editor.setAlignment(Qt.AlignCenter)

    def align_right(self):
        """Align text to the right."""
        self.editor.setAlignment(Qt.AlignRight)

    def align_justify(self):
        """Justify text."""
        self.editor.setAlignment(Qt.AlignJustify)

    def insert_bullet_list(self):
        """Insert a bulleted list."""
        try:
            cursor = self.editor.textCursor()
            list_format = QTextListFormat()
            list_format.setStyle(QTextListFormat.ListDisc)  # Bullet list
            cursor.createList(list_format)
        except Exception as e:
            QMessageBox.critical(self, "List Error", f"Failed to insert bullet list: {e}")

    def insert_numbered_list(self):
        """Insert a numbered list."""
        try:
            cursor = self.editor.textCursor()
            list_format = QTextListFormat()
            list_format.setStyle(QTextListFormat.ListDecimal)  # Numbered list
            cursor.createList(list_format)
        except Exception as e:
            QMessageBox.critical(self, "List Error", f"Failed to insert numbered list: {e}")

    def change_font_size(self, size):
        """Change the font size of the selected text or future text."""
        try:
            cursor = self.editor.textCursor()
            if cursor.hasSelection():
                fmt = QTextCharFormat()
                fmt.setFontPointSize(size)
                cursor.mergeCharFormat(fmt)
            else:
                # Set for future text
                fmt = self.editor.currentCharFormat()
                fmt.setFontPointSize(size)
                self.editor.setCurrentCharFormat(fmt)
        except Exception as e:
            QMessageBox.critical(self, "Font Size Error", f"Failed to set font size: {e}")

    def set_line_spacing(self, spacing_value):
        """Set the line spacing for the selected text or current block."""
        try:
            cursor = self.editor.textCursor()
            block_format = QTextBlockFormat()
            block_format.setLineHeight(float(spacing_value) * 100, QTextBlockFormat.ProportionalHeight)
            cursor.mergeBlockFormat(block_format)
            self.editor.setTextCursor(cursor)
        except Exception as e:
            QMessageBox.critical(self, "Line Spacing Error", f"Failed to set line spacing: {e}")

    def set_paragraph_spacing(self):
        """Set the paragraph spacing before and after the selected text or current block."""
        try:
            cursor = self.editor.textCursor()
            block_format = QTextBlockFormat()
            block_format.setTopMargin(self.paragraph_before_spinbox.value())
            block_format.setBottomMargin(self.paragraph_after_spinbox.value())
            cursor.mergeBlockFormat(block_format)
            self.editor.setTextCursor(cursor)
        except Exception as e:
            QMessageBox.critical(self, "Paragraph Spacing Error", f"Failed to set paragraph spacing: {e}")

    def insert_table(self):
        """Insert a table with user-specified rows and columns."""
        try:
            # Ask the user for rows and columns with validation
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
            self.is_modified = True
        except Exception as e:
            QMessageBox.critical(self, "Table Error", f"Failed to insert table: {e}")

    def modify_table(self):
        """Modify the current table by adding or removing rows and columns."""
        try:
            # Get the current table
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
            self.is_modified = True
        except Exception as e:
            QMessageBox.critical(self, "Modify Table Error", f"Failed to modify table: {e}")

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
        self.set_default_font()
        self.set_default_spacing()
        self.status_label.setText("New document created.")

    def open_file(self):
        """Open an existing file (txt, md, html)."""
        # Open a file dialog to select a file to open
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open File", "",
            "Text Files (*.txt);;Markdown Files (*.md);;HTML Files (*.html *.htm);;All Files (*)"
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
                    return
            elif reply == QMessageBox.Cancel:
                return

        # Determine the file type and read the content
        try:
            if file_name.endswith('.md'):
                self.open_markdown_file(file_name)
            elif file_name.endswith(('.txt',)):
                # Open as Plain Text
                with open(file_name, 'r', encoding='utf-8') as file:
                    plain_text = file.read()
                    self.editor.setAcceptRichText(False)
                    self.editor.setPlainText(plain_text)
                    self.set_default_font()
                    self.set_default_spacing()
            elif file_name.endswith(('.html', '.htm')):
                # Open as HTML
                with open(file_name, 'r', encoding='utf-8') as file:
                    html_content = file.read()
                    self.editor.setAcceptRichText(True)
                    self.editor.setHtml(html_content)
                    self.set_default_font()
                    self.set_default_spacing()
            else:
                QMessageBox.warning(self, "Unsupported Format", "This file format is not currently supported for opening.")
                return
            self.current_file_path = file_name
            self.is_modified = False
            self.status_label.setText("File opened successfully.")
            # Apply default font to entire document
            self.apply_font_to_document()
            self.set_default_spacing()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while opening the file: {str(e)}")

    def save_file(self):
        """Save the current document. If it's a new document, prompt 'Save As'."""
        if self.current_file_path:
            try:
                if self.current_file_path.endswith('.md'):
                    self.save_as_markdown(self.current_file_path)
                elif self.current_file_path.endswith(('.html', '.htm')):
                    self.save_as_html(self.current_file_path)
                elif self.current_file_path.endswith('.pdf'):
                    self.save_as_pdf(self.current_file_path)
                else:
                    self.save_as_txt(self.current_file_path)
                self.is_modified = False  # Mark as not modified after saving
                self.status_label.setText("File saved successfully.")
                return True
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {e}")
                return False
        else:
            # Otherwise, save as a new file
            return self.save_file_as_text()

    def save_file_as_text(self):
        """Save the document as a plain text (.txt) file."""
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save as Text", "", "Text Files (*.txt);;All Files (*)"
            )
            if not file_name:
                return False

            # Automatically append the correct extension if not provided
            if not file_name.endswith('.txt'):
                file_name += '.txt'

            # Save as plain text
            self.save_as_txt(file_name)
            self.current_file_path = file_name
            self.is_modified = False
            self.status_label.setText("File saved as Text successfully.")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save as Text: {e}")
            return False

    def save_file_as_markdown(self):
        """Save the document as a Markdown (.md) file."""
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save as Markdown", "", "Markdown Files (*.md);;All Files (*)"
            )
            if not file_name:
                return

            # Automatically append the correct extension if not provided
            if not file_name.endswith('.md'):
                file_name += '.md'

            # Save as markdown
            self.save_as_markdown(file_name)
            self.status_label.setText("File saved as Markdown successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save as Markdown: {e}")

    def save_file_as_html(self):
        """Save the document as an HTML (.html) file."""
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save as HTML", "", "HTML Files (*.html *.htm);;All Files (*)"
            )
            if not file_name:
                return

            # Automatically append the correct extension if not provided
            if not file_name.endswith(('.html', '.htm')):
                file_name += '.html'

            # Save as HTML
            self.save_as_html(file_name)
            self.status_label.setText("File saved as HTML successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save as HTML: {e}")

    def save_file_as_pdf(self):
        """Save the document as a PDF (.pdf) file."""
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save as PDF", "", "PDF Files (*.pdf);;All Files (*)"
            )
            if not file_name:
                return

            # Automatically append the correct extension if not provided
            if not file_name.endswith('.pdf'):
                file_name += '.pdf'

            # Save as PDF
            self.save_as_pdf(file_name)
            self.status_label.setText("File saved as PDF successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save as PDF: {e}")

    def save_as_txt(self, file_name):
        """Save the document as a plain text (.txt) file."""
        try:
            content = self.editor.toPlainText()
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            raise e

    def save_as_markdown(self, file_name):
        """Save the document as a Markdown (.md) file."""
        try:
            # Convert HTML content to Markdown
            html_content = self.editor.toHtml()
            markdown_converter = html2text.HTML2Text()
            markdown_converter.ignore_links = False
            markdown_converter.ignore_images = False
            markdown_content = markdown_converter.handle(html_content)

            # Save Markdown content to file
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
        except Exception as e:
            raise e

    def save_as_html(self, file_name):
        """Save the document as an HTML (.html) file."""
        try:
            # Get HTML content from editor
            html_content = self.editor.toHtml()

            # Save HTML content to file
            with open(file_name, 'w', encoding='utf-8') as f:
                f.write(html_content)
        except Exception as e:
            raise e

    def save_as_pdf(self, file_name):
        """Save the document as a PDF (.pdf) file."""
        try:
            # Initialize QPrinter
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_name)

            # Print the document to PDF
            self.editor.document().print_(printer)
        except Exception as e:
            raise e

    def open_markdown_file(self, file_name):
        """Open and display a Markdown (.md) file."""
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                md_content = file.read()
                html_content = markdown.markdown(md_content)
                self.editor.setAcceptRichText(True)
                self.editor.setHtml(html_content)
            self.is_modified = False
            self.status_label.setText("Markdown file opened successfully.")
            # Apply default font to entire document
            self.apply_font_to_document()
            self.set_default_spacing()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open Markdown file: {e}")

    def apply_font_to_document(self):
        """Apply the default font family to the entire document without altering other formatting."""
        try:
            cursor = self.editor.textCursor()
            cursor.beginEditBlock()
            cursor.select(QTextCursor.Document)

            # Create a character format that only sets the font family
            fmt = QTextCharFormat()
            available_fonts = QFont().families()
            if 'Charter' in available_fonts:
                fmt.setFontFamily('Charter')
            else:
                fmt.setFontFamily('Times New Roman')  # Fallback to a common font

            # Merge the format without affecting other properties
            cursor.mergeCharFormat(fmt)
            cursor.endEditBlock()
        except Exception as e:
            QMessageBox.critical(self, "Font Application Error", f"Failed to apply font to document: {e}")


    def update_font_selection(self):
        """Update the font size spinbox based on the current cursor position."""
        # Since we're only using Charter, we don't need to update font selector
        # Just update the font size spinbox
        try:
            cursor = self.editor.textCursor()
            char_format = cursor.charFormat()

            # Get the current font size
            current_font_size = char_format.fontPointSize()

            if current_font_size > 0:
                self.font_size_spinbox.blockSignals(True)
                self.font_size_spinbox.setValue(int(current_font_size))
                self.font_size_spinbox.blockSignals(False)
        except Exception as e:
            QMessageBox.critical(self, "Font Selection Error", f"Failed to update font selection: {e}")

    def update_word_count(self):
        """Update word and character count in the status bar."""
        text = self.editor.toPlainText()
        words = len(text.strip().split())
        characters = len(text)
        self.word_count_label.setText(f"Words: {words} | Characters: {characters}")

    def find_replace_dialog(self):
        """Open a dialog for finding and replacing text."""
        dialog = FindReplaceDialog(self.editor, self)
        dialog.show()

    def show_about_dialog(self):
        """Display the About dialog."""
        QMessageBox.about(
            self, "About Clarity Notes",
            "Clarity Notes v1.0\n\nA distraction-free text editor developed with PyQt5."
        )

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

class FindReplaceDialog(QDialog):
    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor
        self.setWindowTitle("Find and Replace")

        # Create widgets
        self.find_input = QLineEdit()
        self.replace_input = QLineEdit()
        self.case_checkbox = QPushButton("Match Case")
        self.case_checkbox.setCheckable(True)
        self.find_button = QPushButton("Find")
        self.replace_button = QPushButton("Replace")
        self.replace_all_button = QPushButton("Replace All")

        # Layout
        layout = QVBoxLayout()
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("Find:"))
        find_layout.addWidget(self.find_input)
        layout.addLayout(find_layout)

        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("Replace with:"))
        replace_layout.addWidget(self.replace_input)
        layout.addLayout(replace_layout)

        options_layout = QHBoxLayout()
        options_layout.addWidget(self.case_checkbox)
        layout.addLayout(options_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.find_button)
        buttons_layout.addWidget(self.replace_button)
        buttons_layout.addWidget(self.replace_all_button)
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

        # Connect signals
        self.find_button.clicked.connect(self.find_text)
        self.replace_button.clicked.connect(self.replace_text)
        self.replace_all_button.clicked.connect(self.replace_all_text)

    def find_text(self):
        """Find the next occurrence of the search text."""
        find_text = self.find_input.text()
        if not find_text:
            return

        flags = QTextDocument.FindFlags()
        if self.case_checkbox.isChecked():
            flags |= QTextDocument.FindCaseSensitively

        if not self.editor.find(find_text, flags):
            QMessageBox.information(self, "Find", "No more occurrences found.")

    def replace_text(self):
        """Replace the current selection with the replace text."""
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_input.text())
            self.find_text()

    def replace_all_text(self):
        """Replace all occurrences of the find text with the replace text."""
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        if not find_text:
            return

        cursor = self.editor.textCursor()
        cursor.beginEditBlock()

        # Move cursor to the start
        cursor.movePosition(QTextCursor.Start)
        self.editor.setTextCursor(cursor)

        flags = QTextDocument.FindFlags()
        if self.case_checkbox.isChecked():
            flags |= QTextDocument.FindCaseSensitively

        replaced = 0
        while self.editor.find(find_text, flags):
            cursor = self.editor.textCursor()
            cursor.insertText(replace_text)
            replaced += 1

        cursor.endEditBlock()
        QMessageBox.information(self, "Replace All", f"Replaced {replaced} occurrences.")

def main():
    """Initialize and run the Clarity Notes application."""
    app = QApplication(sys.argv)
    window = ClarityNotes()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
