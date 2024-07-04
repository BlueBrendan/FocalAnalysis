import os
from constants import focal_lenghts_by_lens, lens_count, focal_lengths, lens_by_focal_length
import exifread
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QScrollArea

def format_focal_length(focal_length):
    if focal_length.is_integer():
        return str(int(focal_length))
    else:
        return f"{focal_length:.1f}"

def check_lens(lens, focalLength):
    lens = lens.strip('\x00')
    if lens in focal_lenghts_by_lens:
        lens_count[lens] += 1
        if focalLength in focal_lenghts_by_lens[lens]:
            focal_lenghts_by_lens[lens][focalLength] += 1
        else:
            focal_lenghts_by_lens[lens][focalLength] = 1
    else:
        focal_lenghts_by_lens[lens] = {focalLength: 1}
        lens_count[lens] = 1

def checkFocalLength(lens, focalLength):
    if focalLength in focal_lengths:
        focal_lengths[focalLength] += 1
        lens_by_focal_length[focalLength][lens] = lens_by_focal_length[focalLength].get(lens, 0) + 1
    else:
        focal_lengths[focalLength] = 1
        lens_by_focal_length[focalLength] = {lens: 1}

def is_valid_image(file_path):
    try:
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f)
        return tags
    except (IOError, SyntaxError):
        return False

def convert_focal_length(focal_length_tag):
    if focal_length_tag.values:
        focal_length = focal_length_tag.values[0]
        if isinstance(focal_length, exifread.utils.Ratio):
            return float(focal_length.num) / float(focal_length.den)
        else:
            return int(focal_length)
    return None
    

def search_images(folder_path, progress_signal):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']  # Add more if needed
    total_files = sum([len(files) for r, d, files in os.walk(folder_path)])
    processed_files = 0

    for root, _, files in os.walk(folder_path):
        for i, file_name in enumerate(files):
            try:
                file_path = os.path.join(root, file_name)
                if os.path.splitext(file_name.lower())[1] not in valid_extensions:
                    continue
                tags = is_valid_image(file_path)
                if tags:
                    lens = tags.get('EXIF LensModel')
                    focal_length_tag = tags.get('EXIF FocalLength')
                    if lens and focal_length_tag:
                        lens = str(lens)
                        focal_length = round(convert_focal_length(focal_length_tag))
                        if focal_length is not None:
                            check_lens(lens, focal_length)
                            checkFocalLength(lens, focal_length)
                    else:
                        print(f"Missing EXIF data for {file_name}")
                processed_files += 1
                progress = int((processed_files / total_files) * 100)
                progress_signal.emit(progress)
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                continue

class ImageProcessingThread(QThread):
    progress_updated = pyqtSignal(int)
    analysis_finished = pyqtSignal()

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path

    def run(self):
        search_images(self.folder_path, self.progress_updated)
        self.analysis_finished.emit()

class CustomScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

    def scrollHorizontally(self, delta):
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta)