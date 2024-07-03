from PIL import Image
import threading
import sys
from PyQt5.QtWidgets import QApplication, QFileDialog
from main_window import MainWindow
from constants import focalLengthsByLens, focalLengths, lensByFocalLength, lensCount, folder_path
from util import searchImages

Image.MAX_IMAGE_PIXELS = 933120000

def analyze_images(window):
    searchImages(folder_path)
    window.update_graphs(focalLengths, focalLengthsByLens, lensCount, lensByFocalLength)

def main():
    app = QApplication(sys.argv)
    global folder_path
    folder_path = QFileDialog.getExistingDirectory(None, "Select Directory", 'E:\\Pictures\\Photos')
    if folder_path:
        window = MainWindow(folder_path)
        window.showMaximized()
        # Start the image analysis in a separate thread
        analysis_thread = threading.Thread(target=analyze_images, args=(window,))
        analysis_thread.start()
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()