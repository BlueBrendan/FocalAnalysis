from PIL import Image
import sys
from PyQt5.QtWidgets import QApplication, QFileDialog
from main_window import MainWindow
from constants import focal_lenghts_by_lens, focal_lengths, lens_by_focal_length, lens_count, folder_path
from util import ImageProcessingThread

Image.MAX_IMAGE_PIXELS = 933120000

def main():
    app = QApplication(sys.argv)
    global folder_path
    folder_path = QFileDialog.getExistingDirectory(None, "Select Directory", 'E:\\Pictures\\Photos')
    if folder_path:
        window = MainWindow(folder_path)
        window.showMaximized()
        
        # Start the image analysis in a separate thread
        analysis_thread = ImageProcessingThread(folder_path)
        analysis_thread.progress_updated.connect(window.update_progress)
        analysis_thread.analysis_finished.connect(lambda: window.create_graph(focal_lengths, focal_lenghts_by_lens, lens_count, lens_by_focal_length))
        analysis_thread.start()
        
        sys.exit(app.exec_())

if __name__ == "__main__":
    main()