import sys
import json
import datetime
import csv
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, 
                             QComboBox, QFormLayout, QTableWidget, QTableWidgetItem, QTabWidget, 
                             QToolBar, QAction, QFileDialog, QDateEdit, QMenu)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QDate
import os

# File path for storing data
data_file_path = os.path.expanduser("~/Library/Application Support/ClarityFinances/finance_data.json")

# Ensure directory exists
os.makedirs(os.path.dirname(data_file_path), exist_ok=True)

# Load existing data or initialize
def load_data():
    if os.path.exists(data_file_path):
        with open(data_file_path, 'r') as file:
            return json.load(file)
    return {"memos": [], "receipts": [], "expenses": [], "expense_categories": ["Professional Fees Paid", "Salaries and Clerkage", "Rent", "Books and Subscriptions", "Printing and Stationary", "Travelling and Conveyance", "Business Development", "Misc. Office Expenses"]}

def save_data(data):
    with open(data_file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Initialize data
finance_data = load_data()

class ClarityFinancesApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Set the font
        self.setFont(QFont('Palatino', 14))

        # Main layout
        main_layout = QVBoxLayout()

        # Toolbar
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)

        # Tab Widget for Display
        self.tab_widget = QTabWidget()
        self.update_tabs()
        main_layout.addWidget(self.tab_widget)

        self.setLayout(main_layout)
        self.setWindowTitle("Clarity Finances")

        # Set the window size (width, height)
        self.resize(800, 600) 

        # Select the current FY and month on launch
        self.set_current_fy_and_month()

        self.show()

    # Create toolbar with buttons for actions
    def create_toolbar(self):
        toolbar = QToolBar()

        add_memo_action = QAction("Add Memo", self)
        add_receipt_action = QAction("Add Receipt", self)
        add_expense_action = QAction("Add Expense", self)
        export_json_action = QAction("Export to JSON", self)
        export_csv_action = QAction("Export to CSV", self)

        add_memo_action.triggered.connect(self.add_memo)
        add_receipt_action.triggered.connect(self.add_receipt)
        add_expense_action.triggered.connect(self.add_expense)
        export_json_action.triggered.connect(self.export_report_json)
        export_csv_action.triggered.connect(self.export_report_csv)

        toolbar.addAction(add_memo_action)
        toolbar.addAction(add_receipt_action)
        toolbar.addAction(add_expense_action)
        toolbar.addAction(export_json_action)
        toolbar.addAction(export_csv_action)

        return toolbar

    # Set current FY and month by default when the app opens
    def set_current_fy_and_month(self):
        current_date = datetime.datetime.now()
        current_fy_start = current_date.year if current_date.month >= 4 else current_date.year - 1

        # Select current FY in FY selector
        index = self.fy_selector.findData(current_fy_start)
        if index >= 0:
            self.fy_selector.setCurrentIndex(index)

        # Select current month in Month selector
        current_month_index = current_date.month - 4 if current_date.month >= 4 else current_date.month + 8
        if current_month_index >= 0 and current_month_index < self.month_selector.count():
            self.month_selector.setCurrentIndex(current_month_index)

    # Update tabs for Memos, Receipts, and Expenses
    def update_tabs(self):
        self.tab_widget.clear()

        # Memos tab
        memo_tab = QWidget()
        memo_layout = QVBoxLayout()
        self.memo_table = QTableWidget(len(finance_data['memos']), 6)
        self.memo_table.setHorizontalHeaderLabels(['Memo No', 'Date', 'Client', 'Amount', 'Received', 'Outstanding'])
        self.memo_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.memo_table.customContextMenuRequested.connect(self.memo_table_menu)

        for row, memo in enumerate(finance_data['memos']):
            self.memo_table.setItem(row, 0, QTableWidgetItem(memo['memo_no']))
            self.memo_table.setItem(row, 1, QTableWidgetItem(memo['date']))
            self.memo_table.setItem(row, 2, QTableWidgetItem(memo['client_name']))
            self.memo_table.setItem(row, 3, QTableWidgetItem(memo['amount']))

            # Calculate amount received for this memo
            total_received = sum(float(receipt['amount']) for receipt in finance_data['receipts'] if receipt['memo_link'] and receipt['memo_link'].startswith(memo['memo_no']))
            self.memo_table.setItem(row, 4, QTableWidgetItem(str(total_received)))

            # Calculate outstanding amount
            outstanding = float(memo['amount']) - total_received
            self.memo_table.setItem(row, 5, QTableWidgetItem(str(outstanding)))

        memo_layout.addWidget(self.memo_table)

        # Financial Year selection for totals
        self.fy_selector = QComboBox()
        self.populate_fy_selector()
        self.fy_selector.currentIndexChanged.connect(self.update_fy_data)

        # Month selection for totals
        self.month_selector = QComboBox()
        self.populate_month_selector()
        self.month_selector.currentIndexChanged.connect(self.update_memo_summary)
        self.month_selector.currentIndexChanged.connect(self.update_receipt_summary)
        self.month_selector.currentIndexChanged.connect(self.update_expense_summary)

        memo_layout.addWidget(QLabel("Select Financial Year:"))
        memo_layout.addWidget(self.fy_selector)

        memo_layout.addWidget(QLabel("Select Month for Summary:"))
        memo_layout.addWidget(self.month_selector)

        # Summary
        self.memo_summary_label = QLabel()
        memo_layout.addWidget(self.memo_summary_label)
        self.update_memo_summary()

        memo_tab.setLayout(memo_layout)
        self.tab_widget.addTab(memo_tab, "Memos")

        # Receipts tab
        receipt_tab = QWidget()
        receipt_layout = QVBoxLayout()
        self.receipt_table = QTableWidget(len(finance_data['receipts']), 3)
        self.receipt_table.setHorizontalHeaderLabels(['Date', 'Amount', 'Memo Linked'])
        self.receipt_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.receipt_table.customContextMenuRequested.connect(self.receipt_table_menu)

        for row, receipt in enumerate(finance_data['receipts']):
            self.receipt_table.setItem(row, 0, QTableWidgetItem(receipt['date']))
            self.receipt_table.setItem(row, 1, QTableWidgetItem(receipt['amount']))
            self.receipt_table.setItem(row, 2, QTableWidgetItem(receipt['memo_link'] or "Not linked"))

        receipt_layout.addWidget(self.receipt_table)

        # Summary
        self.receipt_summary_label = QLabel()
        receipt_layout.addWidget(self.receipt_summary_label)
        self.update_receipt_summary()

        receipt_tab.setLayout(receipt_layout)
        self.tab_widget.addTab(receipt_tab, "Receipts")

        # Expenses tab
        expense_tab = QWidget()
        expense_layout = QVBoxLayout()
        self.expense_table = QTableWidget(len(finance_data['expenses']), 5)
        self.expense_table.setHorizontalHeaderLabels(['Date', 'Category', 'Gross Amount', 'TDS', 'Net Amount'])
        self.expense_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.expense_table.customContextMenuRequested.connect(self.expense_table_menu)

        for row, expense in enumerate(finance_data['expenses']):
            self.expense_table.setItem(row, 0, QTableWidgetItem(expense['date']))
            self.expense_table.setItem(row, 1, QTableWidgetItem(expense['category']))
            self.expense_table.setItem(row, 2, QTableWidgetItem(expense['gross']))
            self.expense_table.setItem(row, 3, QTableWidgetItem(expense['tds']))
            self.expense_table.setItem(row, 4, QTableWidgetItem(expense['net']))

        expense_layout.addWidget(self.expense_table)

        # Summary
        self.expense_summary_label = QLabel()
        expense_layout.addWidget(self.expense_summary_label)
        self.update_expense_summary()

        expense_tab.setLayout(expense_layout)
        self.tab_widget.addTab(expense_tab, "Expenses")

    # Populate financial year selector
    def populate_fy_selector(self):
        current_year = datetime.datetime.now().year
        fy_start_years = list(range(current_year - 5, current_year + 1))  # Allow users to view past 5 FYs
        for start_year in fy_start_years:
            self.fy_selector.addItem(f"{start_year}-{start_year + 1}", start_year)

    # Populate month selector with month names and years
    def populate_month_selector(self):
        current_fy_start = self.fy_selector.currentData()
        months = [("April", 4), ("May", 5), ("June", 6), ("July", 7), ("August", 8), 
                  ("September", 9), ("October", 10), ("November", 11), ("December", 12), 
                  ("January", 1), ("February", 2), ("March", 3)]
        self.month_selector.clear()
        for month_name, month_number in months:
            if month_number < 4:
                self.month_selector.addItem(f"{month_name} {current_fy_start + 1}", month_number)
            else:
                self.month_selector.addItem(f"{month_name} {current_fy_start}", month_number)

    # Update financial year data when FY changes
    def update_fy_data(self):
        self.populate_month_selector()
        self.update_memo_summary()
        self.update_receipt_summary()
        self.update_expense_summary()

    # Context menu for Memo Table (Right-click Edit/Delete)
    def memo_table_menu(self, position):
        menu = QMenu()
        edit_action = menu.addAction("Edit Memo")
        delete_action = menu.addAction("Delete Memo")
        action = menu.exec_(self.memo_table.viewport().mapToGlobal(position))
        
        if action == edit_action:
            row = self.memo_table.currentRow()
            self.edit_memo(row)
        elif action == delete_action:
            row = self.memo_table.currentRow()
            self.delete_memo(row)

    # Context menu for Receipt Table (Right-click Edit/Delete)
    def receipt_table_menu(self, position):
        menu = QMenu()
        edit_action = menu.addAction("Edit Receipt")
        delete_action = menu.addAction("Delete Receipt")
        action = menu.exec_(self.receipt_table.viewport().mapToGlobal(position))
        
        if action == edit_action:
            row = self.receipt_table.currentRow()
            self.edit_receipt(row)
        elif action == delete_action:
            row = self.receipt_table.currentRow()
            self.delete_receipt(row)

    # Context menu for Expense Table (Right-click Edit/Delete)
    def expense_table_menu(self, position):
        menu = QMenu()
        edit_action = menu.addAction("Edit Expense")
        delete_action = menu.addAction("Delete Expense")
        action = menu.exec_(self.expense_table.viewport().mapToGlobal(position))
        
        if action == edit_action:
            row = self.expense_table.currentRow()
            self.edit_expense(row)
        elif action == delete_action:
            row = self.expense_table.currentRow()
            self.delete_expense(row)

    # Update memo summary when month is selected
    def update_memo_summary(self):
        selected_month = self.month_selector.currentData()

        # Calculate totals for memos
        total_monthly_memos, total_fy_memos = self.calculate_totals(finance_data['memos'], selected_month)

        # Update the memo summary label
        self.memo_summary_label.setText(f"--- Memos ---\nTotal for Selected Month: {total_monthly_memos}\nTotal for FY: {total_fy_memos}")

    # Update receipt summary when month is selected
    def update_receipt_summary(self):
        selected_month = self.month_selector.currentData()

        # Calculate totals for receipts
        total_monthly_receipts, total_fy_receipts = self.calculate_totals(finance_data['receipts'], selected_month, key='amount')

        # Update the receipt summary label
        self.receipt_summary_label.setText(f"--- Receipts ---\nTotal for Selected Month: {total_monthly_receipts}\nTotal for FY: {total_fy_receipts}")

    # Update expense summary when month is selected
    def update_expense_summary(self):
        selected_month = self.month_selector.currentData()

        # Calculate totals for expenses
        total_monthly_expenses, total_fy_expenses = self.calculate_totals(finance_data['expenses'], selected_month, key='net')

        # Update the expense summary label
        self.expense_summary_label.setText(f"--- Expenses ---\nTotal for Selected Month: {total_monthly_expenses}\nTotal for FY: {total_fy_expenses}")

    # Calculate totals for selected month and financial year
    def calculate_totals(self, data, selected_month, key=None):
        current_fy_start = self.fy_selector.currentData()
        fy_start_month = 4  # April, assuming FY is April-March

        total_monthly = 0
        total_fy = 0
        for entry in data:
            entry_date = datetime.datetime.strptime(entry['date'], '%Y-%m-%d')
            amount = float(entry[key]) if key else float(entry['amount'])
            if entry_date.month == selected_month and entry_date.year in [current_fy_start, current_fy_start + 1]:
                total_monthly += amount
            if (entry_date.year == current_fy_start and entry_date.month >= fy_start_month) or (entry_date.year == current_fy_start + 1 and entry_date.month < fy_start_month):
                total_fy += amount
        return total_monthly, total_fy


    # Add Memo Functionality
    def add_memo(self):
        self.memo_window = QWidget()
        self.memo_window.setFont(QFont('Palatino', 14))
        self.memo_window.setWindowTitle("Add Memo/Invoice")
        layout = QFormLayout()

        self.memo_no = QLineEdit()
        self.memo_date = QDateEdit()
        self.memo_date.setCalendarPopup(True)
        self.memo_date.setDate(QDate.currentDate())
        self.client_name = QLineEdit()
        self.memo_amount = QLineEdit()

        layout.addRow("Memo No:", self.memo_no)
        layout.addRow("Date:", self.memo_date)
        layout.addRow("Client Name:", self.client_name)
        layout.addRow("Amount:", self.memo_amount)

        save_button = QPushButton("Save Memo")
        save_button.clicked.connect(self.save_memo)
        layout.addWidget(save_button)

        self.memo_window.setLayout(layout)
        self.memo_window.show()

    def save_memo(self):
        memo = {
            "memo_no": self.memo_no.text(),
            "date": self.memo_date.date().toString("yyyy-MM-dd"),
            "client_name": self.client_name.text(),
            "amount": self.memo_amount.text(),
            "paid": False
        }
        finance_data['memos'].append(memo)
        save_data(finance_data)
        self.memo_window.close()
        self.update_tabs()

    def edit_memo(self, index):
        memo = finance_data['memos'][index]
        self.memo_window = QWidget()
        self.memo_window.setFont(QFont('Palatino', 14))
        self.memo_window.setWindowTitle("Edit Memo")
        layout = QFormLayout()

        self.memo_no = QLineEdit(memo['memo_no'])
        self.memo_date = QDateEdit()
        self.memo_date.setCalendarPopup(True)
        self.memo_date.setDate(QDate.fromString(memo['date'], 'yyyy-MM-dd'))
        self.client_name = QLineEdit(memo['client_name'])
        self.memo_amount = QLineEdit(memo['amount'])

        layout.addRow("Memo No:", self.memo_no)
        layout.addRow("Date:", self.memo_date)
        layout.addRow("Client Name:", self.client_name)
        layout.addRow("Amount:", self.memo_amount)

        save_button = QPushButton("Save Memo")
        save_button.clicked.connect(lambda: self.update_memo(index))
        layout.addWidget(save_button)

        self.memo_window.setLayout(layout)
        self.memo_window.show()

    def update_memo(self, index):
        memo = finance_data['memos'][index]
        memo['memo_no'] = self.memo_no.text()
        memo['date'] = self.memo_date.date().toString("yyyy-MM-dd")
        memo['client_name'] = self.client_name.text()
        memo['amount'] = self.memo_amount.text()

        save_data(finance_data)
        self.memo_window.close()
        self.update_tabs()

    def delete_memo(self, index):
        del finance_data['memos'][index]
        save_data(finance_data)
        self.update_tabs()

    # Add Receipt Functionality
    def add_receipt(self):
        self.receipt_window = QWidget()
        self.receipt_window.setFont(QFont('Palatino', 14))
        self.receipt_window.setWindowTitle("Add Receipt")
        layout = QFormLayout()

        self.receipt_date = QDateEdit()
        self.receipt_date.setCalendarPopup(True)
        self.receipt_date.setDate(QDate.currentDate())
        self.receipt_amount = QLineEdit()
        self.memo_link = QComboBox()
        self.memo_link.addItem("Not linked to any memo")
        for memo in finance_data['memos']:
            self.memo_link.addItem(f"{memo['memo_no']} - {memo['client_name']}")

        layout.addRow("Date:", self.receipt_date)
        layout.addRow("Amount:", self.receipt_amount)
        layout.addRow("Against Memo:", self.memo_link)

        save_button = QPushButton("Save Receipt")
        save_button.clicked.connect(self.save_receipt)
        layout.addWidget(save_button)

        self.receipt_window.setLayout(layout)
        self.receipt_window.show()

    def save_receipt(self):
        receipt = {
            "date": self.receipt_date.date().toString("yyyy-MM-dd"),
            "amount": self.receipt_amount.text(),
            "memo_link": self.memo_link.currentText() if self.memo_link.currentIndex() != 0 else None
        }
        finance_data['receipts'].append(receipt)
        save_data(finance_data)
        self.receipt_window.close()
        self.update_tabs()

    def edit_receipt(self, index):
        receipt = finance_data['receipts'][index]
        self.receipt_window = QWidget()
        self.receipt_window.setFont(QFont('Palatino', 14))
        self.receipt_window.setWindowTitle("Edit Receipt")
        layout = QFormLayout()

        self.receipt_date = QDateEdit()
        self.receipt_date.setCalendarPopup(True)
        self.receipt_date.setDate(QDate.fromString(receipt['date'], 'yyyy-MM-dd'))
        self.receipt_amount = QLineEdit(receipt['amount'])
        self.memo_link = QComboBox()
        self.memo_link.addItem("Not linked to any memo")
        for memo in finance_data['memos']:
            self.memo_link.addItem(f"{memo['memo_no']} - {memo['client_name']}")
        if receipt['memo_link']:
            self.memo_link.setCurrentText(receipt['memo_link'])

        layout.addRow("Date:", self.receipt_date)
        layout.addRow("Amount:", self.receipt_amount)
        layout.addRow("Against Memo:", self.memo_link)

        save_button = QPushButton("Save Receipt")
        save_button.clicked.connect(lambda: self.update_receipt(index))
        layout.addWidget(save_button)

        self.receipt_window.setLayout(layout)
        self.receipt_window.show()

    def update_receipt(self, index):
        receipt = finance_data['receipts'][index]
        receipt['date'] = self.receipt_date.date().toString("yyyy-MM-dd")
        receipt['amount'] = self.receipt_amount.text()
        receipt['memo_link'] = self.memo_link.currentText() if self.memo_link.currentIndex() != 0 else None

        save_data(finance_data)
        self.receipt_window.close()
        self.update_tabs()

    def delete_receipt(self, index):
        del finance_data['receipts'][index]
        save_data(finance_data)
        self.update_tabs()

    # Add Expense Functionality
    def add_expense(self):
        self.expense_window = QWidget()
        self.expense_window.setFont(QFont('Palatino', 14))
        self.expense_window.setWindowTitle("Add Expense")
        layout = QFormLayout()

        self.expense_date = QDateEdit()
        self.expense_date.setCalendarPopup(True)
        self.expense_date.setDate(QDate.currentDate())
        self.expense_category = QComboBox()
        self.expense_category.addItems(finance_data['expense_categories'])
        self.expense_gross = QLineEdit()
        self.expense_tds = QLineEdit()
        self.expense_net = QLineEdit()

        layout.addRow("Date:", self.expense_date)
        layout.addRow("Category:", self.expense_category)
        layout.addRow("Gross Amount:", self.expense_gross)
        layout.addRow("TDS:", self.expense_tds)
        layout.addRow("Net Amount:", self.expense_net)

        save_button = QPushButton("Save Expense")
        save_button.clicked.connect(self.save_expense)
        layout.addWidget(save_button)

        self.expense_window.setLayout(layout)
        self.expense_window.show()

    def save_expense(self):
        expense = {
            "date": self.expense_date.date().toString("yyyy-MM-dd"),
            "category": self.expense_category.currentText(),
            "gross": self.expense_gross.text(),
            "tds": self.expense_tds.text(),
            "net": self.expense_net.text()
        }
        finance_data['expenses'].append(expense)
        save_data(finance_data)
        self.expense_window.close()
        self.update_tabs()

    def edit_expense(self, index):
        expense = finance_data['expenses'][index]
        self.expense_window = QWidget()
        self.expense_window.setFont(QFont('Palatino', 14))
        self.expense_window.setWindowTitle("Edit Expense")
        layout = QFormLayout()

        self.expense_date = QDateEdit()
        self.expense_date.setCalendarPopup(True)
        self.expense_date.setDate(QDate.fromString(expense['date'], 'yyyy-MM-dd'))
        self.expense_category = QComboBox()
        self.expense_category.addItems(finance_data['expense_categories'])
        self.expense_category.setCurrentText(expense['category'])
        self.expense_gross = QLineEdit(expense['gross'])
        self.expense_tds = QLineEdit(expense['tds'])
        self.expense_net = QLineEdit(expense['net'])

        layout.addRow("Date:", self.expense_date)
        layout.addRow("Category:", self.expense_category)
        layout.addRow("Gross Amount:", self.expense_gross)
        layout.addRow("TDS:", self.expense_tds)
        layout.addRow("Net Amount:", self.expense_net)

        save_button = QPushButton("Save Expense")
        save_button.clicked.connect(lambda: self.update_expense(index))
        layout.addWidget(save_button)

        self.expense_window.setLayout(layout)
        self.expense_window.show()

    def update_expense(self, index):
        expense = finance_data['expenses'][index]
        expense['date'] = self.expense_date.date().toString("yyyy-MM-dd")
        expense['category'] = self.expense_category.currentText()
        expense['gross'] = self.expense_gross.text()
        expense['tds'] = self.expense_tds.text()
        expense['net'] = self.expense_net.text()

        save_data(finance_data)
        self.expense_window.close()
        self.update_tabs()

    def delete_expense(self, index):
        del finance_data['expenses'][index]
        save_data(finance_data)
        self.update_tabs()

    # Export report functionality - JSON
    def export_report_json(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Report", "", "JSON Files (*.json);;All Files (*)", options=options)
        if file_path:
            with open(file_path, 'w') as export_file:
                json.dump(finance_data, export_file, indent=4)

    # Export report functionality - CSV
    def export_report_csv(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Report", "", "CSV Files (*.csv);;All Files (*)", options=options)
        if file_path:
            with open(file_path, 'w', newline='') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(['Type', 'Date', 'Category/Client', 'Amount', 'Memo Linked', 'TDS', 'Net Amount'])
                for memo in finance_data['memos']:
                    writer.writerow(['Memo', memo['date'], memo['client_name'], memo['amount'], '', '', ''])
                for receipt in finance_data['receipts']:
                    writer.writerow(['Receipt', receipt['date'], '', receipt['amount'], receipt['memo_link'], '', ''])
                for expense in finance_data['expenses']:
                    writer.writerow(['Expense', expense['date'], expense['category'], expense['gross'], '', expense['tds'], expense['net']])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont('Palatino', 14))
    window = ClarityFinancesApp()
    sys.exit(app.exec_())
