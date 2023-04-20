# asset manager for a wallpapers and more andoid application
# take in new assets covert asset to correct format and add to database
# update metadata and data base for assets
# create new thumbnail from existing assets to diplsay in app
# generate tags and keywords for assets to add to database and metadata
# kepp track of assets and their location
# keep track of assets and their metadata
# keep track of assets likes
# keep track of assets downloads

import os
import sys
import shutil
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTreeView
from PyQt5.QtWidgets import QGraphicsPixmapItem, QGraphicsScene
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QFileSystemModel, QFileDialog, QMessageBox, QHeaderView
from PyQt5.uic import loadUi
from PyQt5.QtGui import QImage, QImageReader, QPixmap
from aboutwindow import AboutWindow

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        myAppUI = os.path.join(os.path.dirname(__file__), "form.ui")
        loadUi(myAppUI, self)
        
        self.actionAbout_WM.triggered.connect(self.about)
        self.UploadToDatabaseButton.clicked.connect(self.add_asset)
        self.actionNew_Assets.triggered.connect(self.add_asset)
        self.load_directory_contents()
        self.Remove_Button.clicked.connect(self.remove_asset)

        # Initialize thumbnail scene
        self.thumbnail_scene = QGraphicsScene(self)
        # Connect tree view clicked signal to display thumbnail
        self.Main_treeView.clicked.connect(self.display_selected_thumbnail)

    # Add this method
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.display_selected_thumbnail(self.Main_treeView.currentIndex())

    def about(self):
        self.about_window = AboutWindow(self)
        self.about_window.show()

    def load_directory_contents(self):
        assets_dir = os.path.join(os.path.dirname(__file__), "bin", "assets")
        model = QFileSystemModel()
        model.setRootPath(assets_dir)
        self.Main_treeView.setModel(model)
        self.Main_treeView.setRootIndex(model.index(assets_dir))

        # Hide Size, Type, and Date Modified columns
        self.Main_treeView.setColumnHidden(1, True)
        self.Main_treeView.setColumnHidden(2, True)
        self.Main_treeView.setColumnHidden(3, True)

        # Set header to resize to contents
        self.Main_treeView.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)

        # Calculate the width required to fit the contents of the QTreeView
        content_width = self.Main_treeView.columnWidth(0) + self.Main_treeView.verticalScrollBar().width()

        # Set the new width for the Main_treeView
        self.Main_treeView.setFixedWidth(content_width)

        self.update_statusbar()

    def count_images(self, folder_path):
        image_count = 0
        for root, dirs, files in os.walk(folder_path):
            if "thumbnails" in root:
                continue
            for file in files:
                file_path = os.path.join(root, file)
                if self.is_image_file(file_path):
                    image_count += 1
        return image_count

    def update_statusbar(self):
        assets_dir = os.path.join(os.path.dirname(__file__), "bin", "assets")
        android_app_path = os.path.join(assets_dir, "android_application")
        raw_path = os.path.join(assets_dir, "raw")
        android_app_count = self.count_images(android_app_path)
        raw_count = self.count_images(raw_path)

        self.statusbar.showMessage(f"Android Application: {android_app_count}, Raw: {raw_count}")

    def is_image_file(self, file_path):
        image_reader = QImageReader(file_path)
        return image_reader.canRead()
    
    def add_asset(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)", options=options)
        if file:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Select Category")
            msg_box.setText("Choose the category for the selected asset:")
            wallpaper_button = msg_box.addButton("Wallpaper", QMessageBox.ActionRole)
            live_wallpaper_button = msg_box.addButton("Live Wallpaper", QMessageBox.ActionRole)
            more_button = msg_box.addButton("More", QMessageBox.ActionRole)
            msg_box.exec()

            if msg_box.clickedButton() == wallpaper_button:
                category = "wallpapers"
            elif msg_box.clickedButton() == live_wallpaper_button:
                category = "live_wallpapers"
            else:
                category = "more"

            raw_path = os.path.join(os.path.dirname(__file__), "bin", "assets", "raw", category)

            if category != "more":
                next_number = self.count_images(raw_path) + 1
                new_file_name = f"{category}_{next_number:04d}{os.path.splitext(file)[1]}"
            else:
                new_file_name = os.path.basename(file)

            ## Part 2 ##
            destination_file = os.path.join(raw_path, new_file_name)
            is_image = self.is_image_file(file)

            if is_image:
                thumbnail_folder = os.path.join(os.path.dirname(__file__), "bin", "assets", "raw", category, "thumbnails")
                os.makedirs(thumbnail_folder, exist_ok=True)
                thumbnail_name = self.create_thumbnail(file, thumbnail_folder, category, new_file_name)
                if thumbnail_name:
                    shutil.copy(file, destination_file)
                    self.load_directory_contents()
                    self.display_image(os.path.join(thumbnail_folder, thumbnail_name))
                else:
                    QMessageBox.warning(self, "Error", "Failed to create thumbnail for the selected asset.")
            else:
                QMessageBox.warning(self, "Error", "The selected file is not an image. Please select an image file.")


    def create_thumbnail(self, original_path, thumbnail_folder, category, original_name, thumbnail_size=(200, 200)):
        if self.is_image_file(original_path):
            image = QImage(original_path)
            image = image.scaled(thumbnail_size[0], thumbnail_size[1], aspectRatioMode=QtCore.Qt.KeepAspectRatio)
            thumbnail_name = f"thumbnail_{original_name}"
            thumbnail_path = os.path.join(thumbnail_folder, thumbnail_name)
            image.save(thumbnail_path)
            return thumbnail_name
        else:
            return None
        
    def display_selected_thumbnail(self, index):
        file_path = self.Main_treeView.model().filePath(index)
        if os.path.isfile(file_path) and self.is_image_file(file_path):
            self.display_image(file_path)
        else:
            self.clear_thumbnail()
        
    def display_selected_thumbnail(self, index):
        file_path = self.Main_treeView.model().filePath(index)
        if os.path.isfile(file_path) and self.is_image_file(file_path):
            self.display_image(file_path)
        else:
            self.show_black_screen()
            
    def display_image(self, image_path):
        image = QImage(image_path)
        pixmap = QPixmap.fromImage(image)
        self.thumbnail_scene.clear()
        self.thumbnail_scene.addPixmap(pixmap)
        self.Image_graphicsView.setScene(self.thumbnail_scene)

    def clear_thumbnail(self):
        self.thumbnail_scene.clear()
        
    def show_black_screen(self):
        self.thumbnail_scene.clear()
        black_rect = QtGui.QColor(0, 0, 0)
        self.thumbnail_scene.setBackgroundBrush(black_rect)
        self.Image_graphicsView.setScene(self.thumbnail_scene)
        
    def remove_asset(self):
        selected_indexes = self.Main_treeView.selectedIndexes()
        if selected_indexes:
            selected_index = selected_indexes[0]
            file_path = self.Main_treeView.model().filePath(selected_index)
            if os.path.isfile(file_path):
                file_name = os.path.basename(file_path)

                # Check if the selected file is a thumbnail
                if "thumbnail_" in file_name:
                    return

                thumbnail_folder = os.path.join(os.path.dirname(file_path), "thumbnails")
                thumbnail_name = f"thumbnail_{file_name}"
                thumbnail_path = os.path.join(thumbnail_folder, thumbnail_name)

                reply = QMessageBox.question(self, "Remove Asset", f"Are you sure you want to remove '{file_name}'\n'{thumbnail_name}'?", QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    os.remove(file_path)
                    if os.path.isfile(thumbnail_path):
                        os.remove(thumbnail_path)
                    self.load_directory_contents()
        else:
            QMessageBox.warning(self, "Remove Asset", "Please select an asset to remove.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())