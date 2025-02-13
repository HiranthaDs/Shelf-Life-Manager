from PyQt5.QtWidgets import QApplication
from ui_main import InventoryApp
import sys
import database

if __name__ == "__main__":
    database.create_tables()  # Ensure database and tables exist before running
    app = QApplication(sys.argv)
    window = InventoryApp()
    window.show()
    sys.exit(app.exec_())
