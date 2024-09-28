# Clarity Notes - A Distraction-Free Text Editor
# Copyright (C) 2024 MCN
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# See <https://www.gnu.org/licenses/>.

import sys
import os
import shutil
import speech_recognition as sr
from pydub import AudioSegment
from odf.opendocument import load
from odf.text import P
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QHBoxLayout,
    QComboBox, QFileDialog, QSpinBox, QInputDialog, QMessageBox, QLabel, QCheckBox
)
from PyQt5.QtGui import QFont, QTextCursor, QTextTableFormat, QKeySequence, QTextBlockFormat, QTextListFormat
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtPrintSupport import QPrinter

class AudioTranscriptionThread(QThread):
    transcription_finished = pyqtSignal(str)
    transcription_failed = pyqtSignal(str)

    def __init__(self, audio_path, parent=None):
        super().__init__(parent)
        self.audio_path = audio_path

    def run(self):
        recognizer = sr.Recognizer()
        try:
            # Convert to WAV if necessary
            if not self.audio_path.lower().endswith('.wav'):
                audio = AudioSegment.from_file(self.audio_path)
                temp_audio_path = os.path.join(os.path.dirname(self.audio_path), "temp_audio.wav")
                audio.export(temp_audio_path, format='wav')
            else:
                temp_audio_path = self.audio_path

            with sr.AudioFile(temp_audio_path) as source:
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                self.transcription_finished.emit(text)
        except Exception as e:
            self.transcription_failed.emit(str(e))
        finally:
            # Clean up temporary file if it was created
            if not self.audio_path.lower().endswith('.wav') and os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)

class ClarityNotes(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize mode and state
        self.is_code_mode = False  # False = Normal Mode, True = Code Mode
        self.is_modified = False  # Track if the document is modified
        self.current_file_path = None  # Track the path of the currently opened file

        # Create the main text editor with default font Avenir
        self.editor = QTextEdit()
        self.editor.setFont(QFont('Avenir', 12))
        self.editor.cursorPositionChanged.connect(self.update_font_selection)  # Connect cursor movement to font update
        self.editor.textChanged.connect(self.mark_as_modified)  # Track modifications

        # Set default line and paragraph spacing
        self.set_default_spacing()

        # Create toolbar buttons
        self.create_toolbar_buttons()

        # Set up stylesheets for dark and normal modes
        self.dark_stylesheet = """
            QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
            }
            QTextEdit {
                background-color: #3C3F41;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #5C5C5C;
                color: #FFFFFF;
                border: none;
                padding: 5px;
            }
            QPushButton:pressed {
                background-color: #787878;
            }
            QComboBox {
                background-color: #5C5C5C;
                color: #FFFFFF;
            }
            QSpinBox {
                background-color: #5C5C5C;
                color: #FFFFFF;
            }
            QLabel {
                color: #FFFFFF;
            }
        """
        self.normal_stylesheet = ""

        # Set up the toolbar layout
        self.setup_toolbar_layout()

        # Set up the main layout
        self.setup_main_layout()

        # Set up the main window
        self.setWindowTitle('Clarity: v0.5')
        self.setGeometry(100, 100, 1000, 700)

        # Track dark mode status
        self.is_dark_mode = False

        # Initialize audio transcription thread
        self.transcription_thread = None

    def create_toolbar_buttons(self):
        """Create and initialize toolbar buttons and widgets."""
        # Formatting Buttons
        self.bold_button = QPushButton('Bold')
        self.bold_button.clicked.connect(self.make_bold)
        self.bold_button.setShortcut(QKeySequence("Ctrl+B"))

        self.italic_button = QPushButton('Italic')
        self.italic_button.clicked.connect(self.make_italic)
        self.italic_button.setShortcut(QKeySequence("Ctrl+I"))

        self.underline_button = QPushButton('Underline')
        self.underline_button.clicked.connect(self.make_underline)
        self.underline_button.setShortcut(QKeySequence("Ctrl+U"))

        # List Buttons
        self.bullet_button = QPushButton('Bullets')
        self.bullet_button.clicked.connect(self.insert_bullet_list)

        self.numbering_button = QPushButton('Numbering')
        self.numbering_button.clicked.connect(self.insert_numbered_list)

        # Font Selector
        self.font_selector = QComboBox()
        self.font_selector.addItems([
            'Avenir', 'Arial', 'Book Antiqua', 'Charter', 'Franklin Gothic', 
            'Garamond', 'Gill Sans', 'Helvetica', 'Optima', 'Palatino', 
            'Times New Roman'
        ])
        self.font_selector.currentTextChanged.connect(self.change_font)

        # Font Size SpinBox
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(8, 48)
        self.font_size_spinbox.setValue(12)
        self.font_size_spinbox.valueChanged.connect(self.change_font_size)

        # Line Spacing ComboBox
        self.line_spacing_combo = QComboBox()
        self.line_spacing_combo.addItems(['0.8', '0.9', '1', '1.15', '1.25', '1.3', '1.5', '2'])
        self.line_spacing_combo.setCurrentText('1.15')  # Set default line spacing
        self.line_spacing_combo.currentTextChanged.connect(self.set_line_spacing)

        # Paragraph Spacing SpinBoxes
        self.paragraph_before_spinbox = QSpinBox()
        self.paragraph_before_spinbox.setRange(0, 50)
        self.paragraph_before_spinbox.setValue(6)  # Default value for paragraph spacing before
        self.paragraph_before_spinbox.setPrefix("Before: ")
        self.paragraph_before_spinbox.valueChanged.connect(self.set_paragraph_spacing)

        self.paragraph_after_spinbox = QSpinBox()
        self.paragraph_after_spinbox.setRange(0, 50)
        self.paragraph_after_spinbox.setValue(6)  # Default value for paragraph spacing after
        self.paragraph_after_spinbox.setPrefix("After: ")
        self.paragraph_after_spinbox.valueChanged.connect(self.set_paragraph_spacing)

        # Table Buttons
        self.table_button = QPushButton('Insert Table')
        self.table_button.clicked.connect(self.insert_table)

        self.modify_table_button = QPushButton('Modify Table')
        self.modify_table_button.clicked.connect(self.modify_table)

        # Mode Toggle Button
        self.mode_toggle_button = QPushButton('Switch to Code Mode')
        self.mode_toggle_button.clicked.connect(self.toggle_mode)
        self.mode_toggle_button.setShortcut(QKeySequence("Ctrl+M"))

        # Dark Mode Toggle Button
        self.dark_mode_button = QPushButton('Dark Mode')
        self.dark_mode_button.setCheckable(True)
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)

        # Save, Open, New Document Buttons
        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_file)
        self.save_button.setShortcut(QKeySequence("Ctrl+S"))

        self.open_button = QPushButton('Open')
        self.open_button.clicked.connect(self.open_file)
        self.open_button.setShortcut(QKeySequence("Ctrl+O"))

        self.new_document_button = QPushButton('New Document')
        self.new_document_button.clicked.connect(self.new_document)
        self.new_document_button.setShortcut(QKeySequence("Ctrl+N"))

        # Transcribe Audio Button
        self.transcribe_button = QPushButton('Transcribe Audio')
        self.transcribe_button.clicked.connect(self.transcribe_audio)

        # Status Label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignLeft)

    def setup_toolbar_layout(self):
        """Arrange toolbar buttons into organized layouts."""
        # First row of toolbar
        self.toolbar_layout_1 = QHBoxLayout()
        self.toolbar_layout_1.addWidget(self.bold_button)
        self.toolbar_layout_1.addWidget(self.italic_button)
        self.toolbar_layout_1.addWidget(self.underline_button)
        self.toolbar_layout_1.addWidget(self.bullet_button)
        self.toolbar_layout_1.addWidget(self.numbering_button)
        self.toolbar_layout_1.addWidget(QLabel("Font:"))
        self.toolbar_layout_1.addWidget(self.font_selector)
        self.toolbar_layout_1.addWidget(QLabel("Size:"))
        self.toolbar_layout_1.addWidget(self.font_size_spinbox)
        self.toolbar_layout_1.addWidget(QLabel("Line Spacing:"))
        self.toolbar_layout_1.addWidget(self.line_spacing_combo)
        self.toolbar_layout_1.addWidget(self.paragraph_before_spinbox)
        self.toolbar_layout_1.addWidget(self.paragraph_after_spinbox)
        self.toolbar_layout_1.addWidget(self.table_button)
        self.toolbar_layout_1.addWidget(self.modify_table_button)

        # Second row of toolbar
        self.toolbar_layout_2 = QHBoxLayout()
        self.toolbar_layout_2.addWidget(self.mode_toggle_button)
        self.toolbar_layout_2.addWidget(self.dark_mode_button)
        self.toolbar_layout_2.addWidget(self.save_button)
        self.toolbar_layout_2.addWidget(self.open_button)
        self.toolbar_layout_2.addWidget(self.new_document_button)
        self.toolbar_layout_2.addWidget(self.transcribe_button)

    def setup_main_layout(self):
        """Set up the main application layout including toolbars and editor."""
        # Create vertical layout for toolbars and editor
        main_layout = QVBoxLayout()
        main_layout.addLayout(self.toolbar_layout_1)
        main_layout.addLayout(self.toolbar_layout_2)
        main_layout.addWidget(self.editor)

        # Create a central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

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

    def toggle_mode(self):
        """Toggle between Normal Mode and Code Mode."""
        if not self.is_code_mode:
            # Show a warning message box before switching to Code Mode
            reply = QMessageBox.warning(
                self, 'Switch to Code Mode',
                'Switching to Code Mode will cause all formatting to be lost. Do you want to continue?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                return  # Do not switch modes if the user chooses 'No'

        # Toggle mode
        self.is_code_mode = not self.is_code_mode

        if self.is_code_mode:
            # Switch to Code Mode
            cursor = self.editor.textCursor()
            cursor.select(QTextCursor.Document)
            plain_text = cursor.selection().toPlainText()  # Extract plain text
            self.editor.clear()
            self.editor.setAcceptRichText(False)  # Disable rich text
            self.editor.setPlainText(plain_text)  # Set plain text without formatting
            self.editor.setFont(QFont('Courier', 12))  # Use a monospaced font for code
            self.mode_toggle_button.setText('Switch to Normal Mode')

            # Disable rich text options
            self.bold_button.setDisabled(True)
            self.italic_button.setDisabled(True)
            self.underline_button.setDisabled(True)
            self.bullet_button.setDisabled(True)
            self.numbering_button.setDisabled(True)
            self.font_selector.setDisabled(True)
            self.font_size_spinbox.setDisabled(True)
            self.line_spacing_combo.setDisabled(True)
            self.paragraph_before_spinbox.setDisabled(True)
            self.paragraph_after_spinbox.setDisabled(True)
            self.table_button.setDisabled(True)
            self.modify_table_button.setDisabled(True)
            self.transcribe_button.setDisabled(True)  # Disable transcribe in Code Mode
        else:
            # Switch to Normal Mode
            self.editor.setAcceptRichText(True)  # Enable rich text
            self.editor.setFont(QFont('Avenir', 12))  # Reset to default font and size
            self.mode_toggle_button.setText('Switch to Code Mode')

            # Enable rich text options
            self.bold_button.setDisabled(False)
            self.italic_button.setDisabled(False)
            self.underline_button.setDisabled(False)
            self.bullet_button.setDisabled(False)
            self.numbering_button.setDisabled(False)
            self.font_selector.setDisabled(False)
            self.font_size_spinbox.setDisabled(False)
            self.line_spacing_combo.setDisabled(False)
            self.paragraph_before_spinbox.setDisabled(False)
            self.paragraph_after_spinbox.setDisabled(False)
            self.table_button.setDisabled(False)
            self.modify_table_button.setDisabled(False)
            self.transcribe_button.setDisabled(False)  # Enable transcribe in Normal Mode

    def make_bold(self):
        """Toggle bold formatting."""
        if not self.is_code_mode:
            fmt = self.editor.currentCharFormat()
            if fmt.fontWeight() == QFont.Bold:
                fmt.setFontWeight(QFont.Normal)
            else:
                fmt.setFontWeight(QFont.Bold)
            self.editor.setCurrentCharFormat(fmt)

    def make_italic(self):
        """Toggle italic formatting."""
        if not self.is_code_mode:
            fmt = self.editor.currentCharFormat()
            fmt.setFontItalic(not fmt.fontItalic())
            self.editor.setCurrentCharFormat(fmt)

    def make_underline(self):
        """Toggle underline formatting."""
        if not self.is_code_mode:
            fmt = self.editor.currentCharFormat()
            fmt.setFontUnderline(not fmt.fontUnderline())
            self.editor.setCurrentCharFormat(fmt)

    def insert_bullet_list(self):
        """Insert a bulleted list."""
        if not self.is_code_mode:
            cursor = self.editor.textCursor()
            cursor.beginEditBlock()
            list_format = QTextListFormat()
            list_format.setStyle(QTextListFormat.ListDisc)  # Bullet list
            cursor.createList(list_format)
            cursor.endEditBlock()

    def insert_numbered_list(self):
        """Insert a numbered list."""
        if not self.is_code_mode:
            cursor = self.editor.textCursor()
            cursor.beginEditBlock()
            list_format = QTextListFormat()
            list_format.setStyle(QTextListFormat.ListDecimal)  # Numbered list
            cursor.createList(list_format)
            cursor.endEditBlock()

    def change_font(self, font_name):
        """Change the font family."""
        if not self.is_code_mode:
            self.editor.setFontFamily(font_name)

    def change_font_size(self, size):
        """Change the font size."""
        if not self.is_code_mode:
            self.editor.setFontPointSize(size)

    def set_line_spacing(self, spacing_value):
        """Set the line spacing."""
        if not self.is_code_mode:
            try:
                spacing = float(spacing_value) * 100
                cursor = self.editor.textCursor()
                block_format = QTextBlockFormat()
                block_format.setLineHeight(spacing, QTextBlockFormat.ProportionalHeight)
                cursor.setBlockFormat(block_format)
                self.editor.setTextCursor(cursor)
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Please enter a valid line spacing value.")

    def set_paragraph_spacing(self):
        """Set the paragraph spacing before and after."""
        if not self.is_code_mode:
            cursor = self.editor.textCursor()
            block_format = QTextBlockFormat()
            block_format.setTopMargin(self.paragraph_before_spinbox.value())
            block_format.setBottomMargin(self.paragraph_after_spinbox.value())
            cursor.setBlockFormat(block_format)
            self.editor.setTextCursor(cursor)

    def insert_table(self):
        """Insert a table with user-specified rows and columns."""
        if not self.is_code_mode:
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

    def modify_table(self):
        """Modify the current table by adding or removing rows and columns."""
        if not self.is_code_mode:
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

    def save_file(self):
        """Save the current document. If it's a new document, prompt 'Save As'."""
        if self.current_file_path and self.is_modified:
            try:
                if self.current_file_path.lower().endswith('.odt'):
                    self.save_as_odt(self.current_file_path)
                elif self.current_file_path.lower().endswith('.odf'):
                    self.save_as_odf(self.current_file_path)
                elif self.current_file_path.lower().endswith('.pdf'):
                    self.save_as_pdf(self.current_file_path)
                elif self.is_code_mode and self.current_file_path.lower().endswith(('.py', '.js', '.html')):
                    self.save_as_txt(self.current_file_path)
                else:
                    self.save_as_txt(self.current_file_path)
                self.is_modified = False  # Mark as not modified after saving
                self.status_label.setText(f"Saved: {os.path.basename(self.current_file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")
        else:
            # Otherwise, save as a new file
            self.save_file_as()

    def save_file_as(self):
        """Save the document as a new file with selected format."""
        # Adjust save options based on the current mode
        if self.is_code_mode:
            save_options = ['py', 'js', 'html', 'txt']
        else:
            save_options = ['txt', 'odt', 'odf', 'pdf']
        
        # Ask user to select file type
        file_type, ok = QInputDialog.getItem(
            self, 'Save As', 'Select file type:', save_options, 0, False
        )
        if not ok:
            return
        
        # Define file filter based on selected file type
        filters = {
            'py': "Python Files (*.py)",
            'js': "JavaScript Files (*.js)",
            'html': "HTML Files (*.html)",
            'txt': "Text Files (*.txt)",
            'odt': "OpenDocument Text (*.odt)",
            'odf': "OpenDocument Format (*.odf)",
            'pdf': "PDF Files (*.pdf)"
        }
        filter_selected = filters.get(file_type, "All Files (*)")
        
        # Open a file dialog to select save location
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save File", f"document.{file_type}", filter_selected, options=QFileDialog.Options()
        )
        
        if file_name:
            # Automatically append the correct extension if not provided
            if not file_name.lower().endswith(f'.{file_type}'):
                file_name += f'.{file_type}'
            
            try:
                if file_name.lower().endswith('.odt'):
                    self.save_as_odt(file_name)
                elif file_name.lower().endswith('.odf'):
                    self.save_as_odf(file_name)
                elif file_name.lower().endswith('.pdf'):
                    self.save_as_pdf(file_name)
                else:
                    self.save_as_txt(file_name)
                self.current_file_path = file_name  # Store the current file path
                self.is_modified = False  # Mark as not modified after saving
                self.status_label.setText(f"Saved: {os.path.basename(file_name)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    def save_as_txt(self, file_name):
        """Save the document as a plain text (.txt) file."""
        content = self.editor.toPlainText()
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(content)

    def save_as_odt(self, file_name):
        """Save the document as an OpenDocument Text (.odt) file."""
        try:
            from odf.text import P
            from odf.opendocument import OpenDocumentText

            doc = OpenDocumentText()
            text_content = self.editor.toHtml()
            # Simple conversion from HTML to ODT
            # Note: For full fidelity, consider using a more robust converter
            # Here, we'll insert the plain text as paragraphs
            for line in text_content.split('\n'):
                p = P(text=line)
                doc.text.addElement(p)
            doc.save(file_name)
        except ImportError:
            QMessageBox.critical(self, "Dependency Error", "odfpy is not installed. Please install it to save as .odt.")
            return
        except Exception as e:
            raise e

    def save_as_odf(self, file_name):
        """Save the document as an OpenDocument Format (.odf) file."""
        # For simplicity, saving as .odf similar to .odt
        self.save_as_odt(file_name)

    def save_as_pdf(self, file_name):
        """Save the document as a PDF (.pdf) file."""
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(file_name)
        self.editor.document().print_(printer)

    def open_file(self):
        """Open an existing file."""
        # Define supported formats
        supported_formats = "Text Files (*.txt);;Python Files (*.py);;JavaScript Files (*.js);;HTML Files (*.html);;OpenDocument Text (*.odt);;OpenDocument Format (*.odf);;PDF Files (*.pdf);;All Files (*)"
        
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
            if file_name.lower().endswith(('.py', '.js', '.html', '.txt')):
                with open(file_name, 'r', encoding='utf-8') as file:
                    content = file.read()
                    # If it's a code file, switch to code mode and load the content
                    if file_name.lower().endswith(('.py', '.js', '.html')):
                        if not self.is_code_mode:
                            self.toggle_mode()  # Switch to Code Mode
                    else:
                        if self.is_code_mode:
                            self.toggle_mode()  # Switch to Normal Mode
                    self.editor.setPlainText(content)  # Use plain text for these files
            elif file_name.lower().endswith(('.odt', '.odf')):
                # Handle opening .odt and .odf files
                try:
                    doc = load(file_name)
                    content = ""
                    for element in doc.getElementsByType(P):
                        content += str(element) + '\n'
                    if self.is_code_mode:
                        self.toggle_mode()  # Switch to Normal Mode
                    self.editor.setPlainText(content)  # Set to plain text as a placeholder
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to parse OpenDocument file: {str(e)}")
                    return
            elif file_name.lower().endswith('.pdf'):
                # For PDF, attempt to extract text using a library like PyPDF2
                try:
                    import PyPDF2
                    with open(file_name, 'rb') as file:
                        reader = PyPDF2.PdfReader(file)
                        content = ""
                        for page in reader.pages:
                            content += page.extract_text() + '\n'
                    if self.is_code_mode:
                        self.toggle_mode()  # Switch to Normal Mode
                    self.editor.setPlainText(content)
                except ImportError:
                    QMessageBox.critical(self, "Dependency Error", "PyPDF2 is not installed. Please install it to open PDF files.")
                    return
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to extract text from PDF: {str(e)}")
                    return
            else:
                QMessageBox.warning(self, "Unsupported Format", "This file format is not currently supported for opening.")
                return

            self.current_file_path = file_name  # Store the path of the currently opened file
            self.is_modified = False  # Mark as not modified initially
            self.status_label.setText(f"Opened: {os.path.basename(file_name)}")
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
        self.status_label.setText("New document created.")
        # Reset to Normal Mode if in Code Mode
        if self.is_code_mode:
            self.toggle_mode()

    def toggle_dark_mode(self):
        """Toggle between Dark Mode and Normal Mode."""
        self.is_dark_mode = not self.is_dark_mode
        self.setStyleSheet(self.dark_stylesheet if self.is_dark_mode else self.normal_stylesheet)
        self.editor.setStyleSheet(self.dark_stylesheet if self.is_dark_mode else self.normal_stylesheet)
        mode = "Dark Mode" if self.is_dark_mode else "Light Mode"
        self.status_label.setText(f"Switched to {mode}.")

    def transcribe_audio(self):
        """Handle audio transcription process."""
        # Open a file dialog to select an audio file
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Audio File", "", "Audio Files (*.wav *.aiff *.flac *.m4a *.mp3 *.aac *.ogg)", options=QFileDialog.Options()
        )
        if not file_path:
            return  # Return if no file is selected

        # Define storage directory
        storage_dir = os.path.join(os.getcwd(), "saved_audio_files")
        os.makedirs(storage_dir, exist_ok=True)  # Create the directory if it doesn't exist

        # Copy the original file to storage directory
        stored_audio_path = os.path.join(storage_dir, os.path.basename(file_path))
        try:
            shutil.copy2(file_path, stored_audio_path)  # Copy the original file
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to copy audio file: {str(e)}")
            return

        # Start transcription in a separate thread to keep UI responsive
        self.transcription_thread = AudioTranscriptionThread(stored_audio_path)
        self.transcription_thread.transcription_finished.connect(self.handle_transcription_success)
        self.transcription_thread.transcription_failed.connect(self.handle_transcription_failure)
        self.transcription_thread.start()
        self.status_label.setText("Transcribing audio...")

    def handle_transcription_success(self, text):
        """Handle successful transcription."""
        self.editor.insertPlainText(text + '\n')
        self.is_modified = True
        self.status_label.setText("Audio transcription completed.")

    def handle_transcription_failure(self, error_message):
        """Handle transcription failure."""
        QMessageBox.critical(self, "Transcription Error", f"Could not transcribe audio: {error_message}")
        self.status_label.setText("Transcription failed.")

    def update_font_selection(self):
        """Update the font selector and size spinbox based on the current cursor position."""
        if not self.is_code_mode:
            try:
                cursor = self.editor.textCursor()
                char_format = cursor.charFormat()
                
                # Get the current font family and size
                current_font_family = char_format.fontFamily()
                current_font_size = char_format.fontPointSize()
                
                # Update the font selector
                if current_font_family:
                    index = self.font_selector.findText(current_font_family)
                    if index >= 0:
                        self.font_selector.blockSignals(True)
                        self.font_selector.setCurrentIndex(index)
                        self.font_selector.blockSignals(False)
                
                # Update the font size spinbox
                if current_font_size > 0:
                    self.font_size_spinbox.blockSignals(True)
                    self.font_size_spinbox.setValue(int(current_font_size))
                    self.font_size_spinbox.blockSignals(False)
            except Exception as e:
                QMessageBox.critical(self, "Font Selection Error", f"Failed to update font selection: {e}")

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

def main():
    """Initialize and run the Clarity Notes application."""
    app = QApplication(sys.argv)
    window = ClarityNotes()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
