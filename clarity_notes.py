import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QPushButton, QVBoxLayout, QWidget, QHBoxLayout,
    QComboBox, QFileDialog, QSpinBox, QInputDialog, QMessageBox
)
from PyQt5.QtGui import QFont, QTextCursor, QTextTableFormat, QKeySequence, QTextBlockFormat, QTextListFormat
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrinter

class ClarityNotes(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize mode
        self.is_code_mode = False  # False = Normal Mode, True = Code Mode
        self.is_modified = False  # Track if the document is modified

        # Create the main text editor with default font Avenir
        self.editor = QTextEdit()
        self.editor.setFont(QFont('Avenir', 12))
        self.editor.cursorPositionChanged.connect(self.update_font_selection)  # Connect cursor movement to font update
        self.editor.textChanged.connect(self.mark_as_modified)  # Track modifications

        # Set default line and paragraph spacing
        self.set_default_spacing()

        # Create toolbar buttons
        self.bold_button = QPushButton('Bold')
        self.bold_button.clicked.connect(self.make_bold)
        self.bold_button.setShortcut(QKeySequence("Ctrl+B"))

        self.italic_button = QPushButton('Italic')
        self.italic_button.clicked.connect(self.make_italic)
        self.italic_button.setShortcut(QKeySequence("Ctrl+I"))

        self.underline_button = QPushButton('Underline')
        self.underline_button.clicked.connect(self.make_underline)
        self.underline_button.setShortcut(QKeySequence("Ctrl+U"))

        self.bullet_button = QPushButton('Bullets')
        self.bullet_button.clicked.connect(self.insert_bullet_list)

        self.numbering_button = QPushButton('Numbering')
        self.numbering_button.clicked.connect(self.insert_numbered_list)

        self.font_selector = QComboBox()
        self.font_selector.addItems([
            'Avenir', 'Arial', 'Book Antiqua', 'Charter', 'Franklin Gothic', 
            'Garamond', 'Gill Sans', 'Helvetica', 'Optima', 'Palatino', 
            'Times New Roman'
        ])
        self.font_selector.currentTextChanged.connect(self.change_font)

        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(8, 48)
        self.font_size_spinbox.setValue(12)
        self.font_size_spinbox.valueChanged.connect(self.change_font_size)

        # Line spacing combo box with new options
        self.line_spacing_combo = QComboBox()
        self.line_spacing_combo.addItems(['0.8', '0.9', '1', '1.15', '1.25', '1.3', '1.5', '2'])
        self.line_spacing_combo.setCurrentText('1.15')  # Set default line spacing
        self.line_spacing_combo.currentTextChanged.connect(self.set_line_spacing)

        # Paragraph spacing spin boxes with a reasonable range
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

        self.table_button = QPushButton('Insert Table')
        self.table_button.clicked.connect(self.insert_table)

        self.modify_table_button = QPushButton('Modify Table')
        self.modify_table_button.clicked.connect(self.modify_table)

        self.mode_toggle_button = QPushButton('Switch to Code Mode')
        self.mode_toggle_button.clicked.connect(self.toggle_mode)
        self.mode_toggle_button.setShortcut(QKeySequence("Ctrl+M"))

        self.save_button = QPushButton('Save')
        self.save_button.clicked.connect(self.save_file)
        self.save_button.setShortcut(QKeySequence("Ctrl+S"))

        self.new_document_button = QPushButton('New Document')
        self.new_document_button.clicked.connect(self.new_document)
        self.new_document_button.setShortcut(QKeySequence("Ctrl+N"))

        self.dark_mode_button = QPushButton('Dark Mode')
        self.dark_mode_button.setCheckable(True)
        self.dark_mode_button.clicked.connect(self.toggle_dark_mode)

        # Set up stylesheets for dark and normal modes
        self.dark_stylesheet = "background-color: #2E2E2E; color: white;"
        self.normal_stylesheet = ""

        # Set up the toolbar layout
        # First row
        toolbar_layout_1 = QHBoxLayout()
        toolbar_layout_1.addWidget(self.bold_button)
        toolbar_layout_1.addWidget(self.italic_button)
        toolbar_layout_1.addWidget(self.underline_button)
        toolbar_layout_1.addWidget(self.bullet_button)  # Add bullet button
        toolbar_layout_1.addWidget(self.numbering_button)  # Add numbering button
        toolbar_layout_1.addWidget(self.font_selector)
        toolbar_layout_1.addWidget(self.font_size_spinbox)
        toolbar_layout_1.addWidget(self.line_spacing_combo)  # Add line spacing combo
        toolbar_layout_1.addWidget(self.paragraph_before_spinbox)  # Add paragraph spacing controls
        toolbar_layout_1.addWidget(self.paragraph_after_spinbox)  # Add paragraph spacing controls
        toolbar_layout_1.addWidget(self.table_button)
        toolbar_layout_1.addWidget(self.modify_table_button)

        # Second row
        toolbar_layout_2 = QHBoxLayout()
        toolbar_layout_2.addWidget(self.mode_toggle_button)  # Move to the second row
        toolbar_layout_2.addWidget(self.dark_mode_button)
        toolbar_layout_2.addWidget(self.save_button)
        toolbar_layout_2.addWidget(self.new_document_button)

        # Set up the main layout
        layout = QVBoxLayout()
        layout.addLayout(toolbar_layout_1)
        layout.addLayout(toolbar_layout_2)  # Add second row to the main layout
        layout.addWidget(self.editor)

        # Set up the central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Set up the main window
        self.setWindowTitle('Clarity Notes')
        self.setGeometry(100, 100, 800, 600)

        # Track dark mode status
        self.is_dark_mode = False

    def set_default_spacing(self):
        # Set default line spacing to 1.15 and paragraph spacing to 6 before and 6 after
        cursor = self.editor.textCursor()
        block_format = cursor.blockFormat()
        block_format.setLineHeight(115, QTextBlockFormat.ProportionalHeight)  # 1.15 line spacing
        block_format.setTopMargin(6)  # 6 points before paragraph
        block_format.setBottomMargin(6)  # 6 points after paragraph
        cursor.setBlockFormat(block_format)
        self.editor.setTextCursor(cursor)

    def mark_as_modified(self):
        self.is_modified = True

    def toggle_mode(self):
        if not self.is_code_mode:
            # Show a warning message box before switching to Code Mode
            reply = QMessageBox.warning(
                self, 'Switch to Code Mode',
                'Switching to Code Mode will cause all formatting to be lost. Do you want to continue?',
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.No:
                return  # Do not switch modes if the user chooses 'No'

        # Toggle between Normal Mode and Code Mode
        self.is_code_mode = not self.is_code_mode
        
        if self.is_code_mode:
            # Switch to Code Mode
            # Convert to plain text to strip away all formatting
            plain_text = self.editor.toPlainText()  # Extract plain text, removing formatting
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

    def make_bold(self):
        if not self.is_code_mode:
            # Toggle bold
            if self.editor.fontWeight() == QFont.Bold:
                self.editor.setFontWeight(QFont.Normal)
            else:
                self.editor.setFontWeight(QFont.Bold)

    def make_italic(self):
        if not self.is_code_mode:
            # Toggle italic
            state = self.editor.fontItalic()
            self.editor.setFontItalic(not state)

    def make_underline(self):
        if not self.is_code_mode:
            # Toggle underline
            state = self.editor.fontUnderline()
            self.editor.setFontUnderline(not state)

    def insert_bullet_list(self):
        if not self.is_code_mode:
            cursor = self.editor.textCursor()
            cursor.beginEditBlock()
            list_format = QTextListFormat()
            list_format.setStyle(QTextListFormat.ListDisc)  # Bullet list
            cursor.createList(list_format)
            cursor.endEditBlock()

    def insert_numbered_list(self):
        if not self.is_code_mode:
            cursor = self.editor.textCursor()
            cursor.beginEditBlock()
            list_format = QTextListFormat()
            list_format.setStyle(QTextListFormat.ListDecimal)  # Numbered list
            cursor.createList(list_format)
            cursor.endEditBlock()

    def change_font(self, font_name):
        if not self.is_code_mode:
            self.editor.setFontFamily(font_name)

    def change_font_size(self, size):
        if not self.is_code_mode:
            self.editor.setFontPointSize(size)

    def set_line_spacing(self, spacing_value):
        if not self.is_code_mode:
            cursor = self.editor.textCursor()
            block_format = cursor.blockFormat()
            block_format.setLineHeight(float(spacing_value) * 100, QTextBlockFormat.ProportionalHeight)
            cursor.setBlockFormat(block_format)
            self.editor.setTextCursor(cursor)

    def set_paragraph_spacing(self):
        if not self.is_code_mode:
            cursor = self.editor.textCursor()
            block_format = cursor.blockFormat()
            block_format.setTopMargin(self.paragraph_before_spinbox.value())
            block_format.setBottomMargin(self.paragraph_after_spinbox.value())
            cursor.setBlockFormat(block_format)
            self.editor.setTextCursor(cursor)

    def insert_table(self):
        if not self.is_code_mode:
            # Ask the user for rows and columns
            rows, ok1 = QInputDialog.getInt(self, 'Insert Table', 'Number of rows:', 2, 1)
            columns, ok2 = QInputDialog.getInt(self, 'Insert Table', 'Number of columns:', 2, 1)
            if ok1 and ok2:
                cursor = self.editor.textCursor()
                fmt = QTextTableFormat()
                fmt.setBorder(1)
                fmt.setCellPadding(5)  # Set padding for better visibility
                fmt.setCellSpacing(2)  # Set spacing between cells
                cursor.insertTable(rows, columns, fmt)

    def modify_table(self):
        if not self.is_code_mode:
            # Get the current table
            cursor = self.editor.textCursor()
            table = cursor.currentTable()
            
            if table is None:
                QMessageBox.warning(self, 'No Table Found', 'No table found at the current cursor position.')
                return

            # Ask for the number of rows and columns to modify
            rows_to_modify, ok1 = QInputDialog.getInt(self, 'Modify Table', 'Number of rows to add (+) or remove (-):', 0, -table.rows(), 100)
            columns_to_modify, ok2 = QInputDialog.getInt(self, 'Modify Table', 'Number of columns to add (+) or remove (-):', 0, -table.columns(), 100)

            # Ensure valid row and column modifications
            if ok1 and rows_to_modify != 0:
                if rows_to_modify > 0:
                    table.appendRows(rows_to_modify)
                elif rows_to_modify < 0:
                    rows_to_remove = abs(rows_to_modify)
                    if rows_to_remove <= table.rows():
                        table.removeRows(table.rows() - rows_to_remove, rows_to_remove)

            if ok2 and columns_to_modify != 0:
                if columns_to_modify > 0:
                    table.appendColumns(columns_to_modify)
                elif columns_to_modify < 0:
                    cols_to_remove = abs(columns_to_modify)
                    if cols_to_remove <= table.columns():
                        table.removeColumns(table.columns() - cols_to_remove, cols_to_remove)

    def save_file(self):
        # Adjust save options based on the current mode
        if self.is_code_mode:
            save_options = ['py', 'js', 'html', 'txt']
        else:
            save_options = ['txt', 'odt', 'odf', 'pdf']
            
        # Ask user to select file type
        file_type, ok = QInputDialog.getItem(self, 'Save As', 'Select file type:', save_options, 0, False)
        if not ok:
            return
        
        # Automatically append the correct extension if not provided
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", f"document.{file_type}", options=QFileDialog.Options())
        
        if file_name:
            if not file_name.endswith(f'.{file_type}'):
                file_name += f'.{file_type}'  # Append the correct extension if missing

            try:
                if file_name.endswith('.odt'):
                    self.save_as_odt(file_name)
                elif file_name.endswith('.odf'):
                    self.save_as_odf(file_name)
                elif file_name.endswith('.pdf'):
                    self.save_as_pdf(file_name)
                else:
                    self.save_as_txt(file_name)
                self.is_modified = False  # Mark as not modified after saving
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    def save_as_txt(self, file_name):
        content = self.editor.toPlainText()
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(content)

    def save_as_odt(self, file_name):
        # Save the document as HTML with rich formatting for .odt
        content = self.editor.toHtml()
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(content)

    def save_as_odf(self, file_name):
        # Save the document as HTML with rich formatting for .odf
        content = self.editor.toHtml()
        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(content)

    def save_as_pdf(self, file_name):
        printer = QPrinter(QPrinter.HighResolution)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(file_name)
        self.editor.document().print_(printer)

    def new_document(self):
        # Check if there is unsaved work
        if self.is_modified:
            reply = QMessageBox.question(self, 'Unsaved Work', 'Do you want to save the current document before creating a new one?',
                                         QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel, QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return  # Do not proceed if cancel is selected
        
        # Clear the editor for a new document
        self.editor.clear()
        self.is_modified = False  # Reset modified status
        self.editor.setFocus()  # Set focus to the editor

    def toggle_dark_mode(self):
        self.is_dark_mode = not self.is_dark_mode
        self.setStyleSheet(self.dark_stylesheet if self.is_dark_mode else self.normal_stylesheet)
        self.editor.setStyleSheet(self.dark_stylesheet if self.is_dark_mode else self.normal_stylesheet)

    def update_font_selection(self):
        if not self.is_code_mode:
            # Get the current cursor's character format
            cursor = self.editor.textCursor()
            char_format = cursor.charFormat()
            
            # Get the current font family and size
            current_font_family = char_format.fontFamily()
            current_font_size = char_format.fontPointSize()
            
            # Update the font selector and size spinbox
            if current_font_family:
                index = self.font_selector.findText(current_font_family)
                if index >= 0:
                    self.font_selector.setCurrentIndex(index)
            
            if current_font_size:
                self.font_size_spinbox.setValue(int(current_font_size))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ClarityNotes()
    window.show()
    sys.exit(app.exec_())
