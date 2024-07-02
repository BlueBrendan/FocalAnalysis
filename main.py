from PIL import Image

import sys
from PyQt5.QtWidgets import QApplication, QFileDialog
from main_window import MainWindow
from constants import focalLengthsByLens, focalLengths, lensByFocalLength, lensCount, folder_path
from util import searchImages

Image.MAX_IMAGE_PIXELS = 933120000


def main():
    app = QApplication(sys.argv)
    global folder_path
    folder_path = QFileDialog.getExistingDirectory(None, "Select Directory", 'E:\\Pictures\\Photos')
    searchImages(folder_path)
    if folder_path and len(focalLengthsByLens.items()) > 0:
        window = MainWindow(focalLengths, focalLengthsByLens, lensCount, lensByFocalLength, folder_path)
        window.showMaximized()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()