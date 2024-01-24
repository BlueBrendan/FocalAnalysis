from PIL import Image
import os
import sys
from PyQt5.QtWidgets import QApplication, QFileDialog
from main_window import MainWindow
from constants import lensModelExif, focalLengthIn35mmExif

Image.MAX_IMAGE_PIXELS = 933120000

def get_folder_path():
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    folder_path = QFileDialog.getExistingDirectory(None, "Select Folder", options=options)
    return folder_path

focalLengthsByLens = {} # {lens:{focalLength: count}}
focalLengths = {} # {focal length: count}
lensByFocalLength = {} # {focal length:{lens: count}}
lensCount = {} # {lens: count}

def checkLens(lens, focalLength):
    lens = lens.strip('\x00')
    if lens in focalLengthsByLens:
        lensCount[lens] += 1
        if focalLength in focalLengthsByLens[lens]:
            focalLengthsByLens[lens][focalLength] += 1
        else:
            focalLengthsByLens[lens][focalLength] = 1
    else:
        focalLengthsByLens[lens] = {focalLength: 1}
        lensCount[lens] = 1

def checkFocalLength(lens, focalLength):
    
    if focalLength in focalLengths:
        focalLengths[focalLength] += 1
        lensByFocalLength[str(focalLength)][lens] = lensByFocalLength[str(focalLength)].get(lens, 0) + 1
    else:
        focalLengths[focalLength] = 1
        lensByFocalLength[str(focalLength)] = {lens: 1}

def is_valid_image(file_path):
    try:
        img = Image.open(file_path)
        img.verify()
        return True
    except (IOError, SyntaxError):
        return False

def searchImages(folder_path):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.raw', '.nef']  # Add more if needed

    for root, _, files in os.walk(folder_path):
        for file_name in files:
            try:
                file_path = os.path.join(root, file_name)
                # Check if the file has a valid image extension
                if os.path.splitext(file_name.lower())[1] not in valid_extensions:
                    continue
                if is_valid_image(file_path):
                    img = Image.open(file_path)
                    exif_data = img._getexif()
                    try:
                        checkLens(exif_data[lensModelExif], exif_data[focalLengthIn35mmExif])
                        checkFocalLength(exif_data[lensModelExif], exif_data[focalLengthIn35mmExif])
                    except KeyError:
                        pass
            except:
                pass

if __name__ == "__main__":
    folder_path = 'E:\\Pictures\\Photos\\2023'  
    searchImages(folder_path)
    if len(focalLengthsByLens.items()) > 0:
        app = QApplication(sys.argv)
        window = MainWindow(focalLengths, focalLengthsByLens, lensCount, lensByFocalLength)
        window.show()
        sys.exit(app.exec_())