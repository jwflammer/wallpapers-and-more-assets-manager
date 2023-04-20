# Asset manager for a wallpapers and more Android application
# Takes in new assets, converts assets to the correct format, and adds them to the database
# Updates metadata and database for assets
# Creates new thumbnails from existing assets to display in the app
# Generates tags and keywords for assets to add to the database and metadata
# Keeps track of assets and their location
# Keeps track of assets and their metadata
# Keeps track of assets likes
# Keeps track of assets downloads

import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt5.uic import loadUi


class AboutWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Load the UI file
        myAppUI = os.path.join(os.path.dirname(__file__), "about_form.ui")
        loadUi(myAppUI, self)
        
        # connect OkayButton to close window
        self.OkayButton.clicked.connect(self.close)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = AboutWindow()
    widget.show()
    sys.exit(app.exec())
