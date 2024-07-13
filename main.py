from PIL import Image
import sys
from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtGui import QIcon
from main_window import MainWindow
from constants import focal_lengths_by_lens_dict, lens_by_focal_length_dict, folder_path
from util import ImageProcessingThread
import os
import ctypes

Image.MAX_IMAGE_PIXELS = 933120000

def main():
    myappid = 'focalAnalysis' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icon128.ico'))
    last_directory = os.path.expanduser("~")
    global folder_path
    
    folder_path = QFileDialog.getExistingDirectory(None, "Select Directory", last_directory)
    if folder_path:
        last_directory = folder_path
        window = MainWindow(folder_path)
        window.showMaximized()
        # Start the image analysis in a separate thread
        analysis_thread = ImageProcessingThread(folder_path)
        analysis_thread.progress_updated.connect(window.update_progress)
        analysis_thread.analysis_finished.connect(lambda: window.create_graph(focal_lengths_by_lens_dict, lens_by_focal_length_dict))
        analysis_thread.start()
        
        sys.exit(app.exec())

if __name__ == "__main__":
    main()