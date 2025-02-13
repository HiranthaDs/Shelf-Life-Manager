import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QVBoxLayout, QCalendarWidget, QTableWidgetItem, \
    QMessageBox, QLineEdit, QInputDialog, QHBoxLayout, QPushButton, QStyle
from PyQt5.QtCore import QDate, QPoint
from PyQt5.QtGui import QIcon, QPalette, QColor
from PyQt5.uic import loadUi
from database import create_tables, add_product, get_products, update_product, delete_product
from datetime import datetime, timedelta


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("ui_main.ui", self)
        create_tables()  # Ensure tables are created
        self.setup_ui()
        self.load_products()
        self.is_showing_expiring_soon = False  # Toggle for showing expiring soon items

    def setup_ui(self):
        """Initialize UI components and connections."""
        self.setWindowTitle("Inventory Management")
        self.setWindowIcon(QIcon("icons/app_icon.png"))  # Set application icon
        self.setStyleSheet("background-color: #f4f4f4; color: #333;")  # Set background color

        # Apply modern styling to buttons
        self.apply_button_styles()

        # Calendar dialog setup
        self.calendar_dialog = QDialog(self)
        self.calendar_dialog.setWindowTitle("Select Expiry Date")
        self.calendar = QCalendarWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        self.calendar_dialog.setLayout(layout)
        self.calendar.clicked.connect(self.set_expiry_date)

        # Connect signals
        self.btn_add.clicked.connect(self.add_product)
        self.btn_update.clicked.connect(self.update_product)
        self.btn_delete.clicked.connect(self.delete_product)
        self.btn_calendar.clicked.connect(self.show_calendar)
        self.tableWidget.itemSelectionChanged.connect(self.load_selected_product)
        self.txt_quantity.textChanged.connect(self.calculate_total_price)
        self.txt_price.textChanged.connect(self.calculate_total_price)
        self.btn_show_expiring.clicked.connect(self.toggle_expiring_soon)  # Connect the toggle button

    def apply_button_styles(self):
        """Apply modern styling to buttons."""
        self.btn_add.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.btn_update.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.btn_show_expiring.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #fb8c00;
            }
        """)

        self.btn_calendar.setStyleSheet("""
            QPushButton {
                background-color: #607D8B;
                color: white;
                border-radius: 15px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #455A64;
            }
        """)

    def show_calendar(self):
        """Show the calendar dialog near the calendar button."""
        button_pos = self.btn_calendar.mapToGlobal(QPoint(0, 0))
        self.calendar_dialog.move(button_pos)
        self.calendar_dialog.exec_()

    def set_expiry_date(self, date):
        """Set the selected date in the expiry date field."""
        self.txt_expiry.setText(date.toString("yyyy-MM-dd"))
        self.calendar_dialog.hide()

    def calculate_total_price(self):
        """Calculate and display the total price."""
        try:
            quantity = float(self.txt_quantity.text()) if self.txt_quantity.text() else 0
            price = float(self.txt_price.text()) if self.txt_price.text() else 0
            self.txt_total_price.setText(f"{quantity * price:.2f}")
        except ValueError:
            self.txt_total_price.setText("0.00")

    def load_products(self):
        """Load all products into the table."""
        products = get_products()
        self.tableWidget.setRowCount(len(products))
        for row, product in enumerate(products):
            for col, data in enumerate(product):
                item = QTableWidgetItem(str(data))
                if col == 7:  # Check if the expiry date is within 30 days
                    expiry_date = datetime.strptime(product[7], "%Y-%m-%d")
                    today = datetime.today()
                    if today <= expiry_date <= today + timedelta(days=30):
                        item.setBackground(QColor(255, 0, 0))  # Set background color to red for expiring soon items
                self.tableWidget.setItem(row, col, item)

    def load_selected_product(self):
        """Load the selected product into the form fields."""
        selected = self.tableWidget.selectedItems()
        if selected:
            row = selected[0].row()
            self.txt_item_code.setText(self.tableWidget.item(row, 1).text())
            self.txt_name.setText(self.tableWidget.item(row, 2).text())
            self.txt_batch.setText(self.tableWidget.item(row, 3).text())
            self.txt_quantity.setText(self.tableWidget.item(row, 4).text())
            self.txt_price.setText(self.tableWidget.item(row, 5).text())
            self.txt_total_price.setText(self.tableWidget.item(row, 6).text())
            self.txt_expiry.setText(self.tableWidget.item(row, 7).text())
            self.txt_location.setText(self.tableWidget.item(row, 8).text())
            self.txt_supplier.setText(self.tableWidget.item(row, 9).text())

    def add_product(self):
        """Add a new product to the database."""
        try:
            # Validate inputs
            if not all([
                self.txt_item_code.text(),
                self.txt_name.text(),
                self.txt_batch.text(),
                self.txt_quantity.text(),
                self.txt_price.text(),
                self.txt_expiry.text(),
                self.txt_location.text(),
                self.txt_supplier.text()
            ]):
                QMessageBox.warning(self, "Error", "All fields are required!")
                return

            # Add product to database
            add_product(
                self.txt_item_code.text(),
                self.txt_name.text(),
                self.txt_batch.text(),
                int(self.txt_quantity.text()),
                float(self.txt_price.text()),
                self.txt_expiry.text(),
                self.txt_location.text(),
                self.txt_supplier.text()
            )
            self.load_products()
            self.clear_fields()
            QMessageBox.information(self, "Success", "Product added successfully!")
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Invalid input: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def update_product(self):
        """Update the selected product in the database."""
        selected = self.tableWidget.selectedItems()
        if selected:
            try:
                product_id = int(self.tableWidget.item(selected[0].row(), 0).text())
                update_product(
                    product_id,
                    self.txt_item_code.text(),
                    self.txt_name.text(),
                    self.txt_batch.text(),
                    int(self.txt_quantity.text()),
                    float(self.txt_price.text()),
                    self.txt_expiry.text(),
                    self.txt_location.text(),
                    self.txt_supplier.text()
                )
                self.load_products()
                QMessageBox.information(self, "Success", "Product updated successfully!")
            except ValueError:
                QMessageBox.warning(self, "Error", "Please select a product and enter valid values")
        else:
            QMessageBox.warning(self, "Error", "Please select a product to update")

    def delete_product(self):
        """Delete the selected product from the database."""
        # Request password before deleting
        password, ok = QInputDialog.getText(self, "Password", "Enter password to delete product:")

        if ok and password == "123":  # Check if password is correct
            selected = self.tableWidget.selectedItems()
            if selected:
                product_id = int(self.tableWidget.item(selected[0].row(), 0).text())
                delete_product(product_id)
                self.load_products()
                self.clear_fields()
                QMessageBox.information(self, "Success", "Product deleted successfully!")
            else:
                QMessageBox.warning(self, "Error", "Please select a product to delete")
        else:
            QMessageBox.warning(self, "Error", "Incorrect password or cancelled")

    def clear_fields(self):
        """Clear all input fields."""
        for widget in self.findChildren(QLineEdit):
            widget.clear()

    def toggle_expiring_soon(self):
        """Toggle between showing all products and products expiring soon."""
        if self.is_showing_expiring_soon:
            self.load_products()  # Load all products
            self.btn_show_expiring.setText("Show Expiring Soon")
        else:
            self.show_expiring_soon()  # Show only expiring soon products
            self.btn_show_expiring.setText("Show All Products")

        # Toggle the state
        self.is_showing_expiring_soon = not self.is_showing_expiring_soon

    def show_expiring_soon(self):
        """Show products that are expiring soon (within 30 days)."""
        today = datetime.today()
        expiring_soon = []

        # Retrieve all products and filter by expiry date
        products = get_products()
        for product in products:
            expiry_date_str = product[7]  # Get expiry date from the 8th column (index 7)
            try:
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d")
                if today <= expiry_date <= today + timedelta(days=30):
                    expiring_soon.append(product)
            except ValueError:
                continue

        # Display products expiring soon in the table
        self.tableWidget.setRowCount(len(expiring_soon))
        for row, product in enumerate(expiring_soon):
            for col, data in enumerate(product):
                item = QTableWidgetItem(str(data))
                if col == 7:  # Check if the expiry date is within 30 days
                    expiry_date = datetime.strptime(product[7], "%Y-%m-%d")
                    if today <= expiry_date <= today + timedelta(days=30):
                        item.setBackground(QColor(255, 0, 0))  # Set background color to red for expiring soon items
                self.tableWidget.setItem(row, col, item)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
