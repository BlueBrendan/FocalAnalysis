import os
from constants import focal_lengths_by_lens_dict, lens_by_focal_length_dict
import exifread
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QScrollArea

lens_set = set()
focal_length_set = set()

def format_focal_length(focal_length):
    if focal_length.is_integer():
        return str(int(focal_length))
    else:
        return f"{focal_length:.1f}"

def check_lens(lens, focalLength):
    lens = lens.strip('\x00')
    if lens in lens_set:
        if focalLength in focal_lengths_by_lens_dict[lens]:
            focal_lengths_by_lens_dict[lens][focalLength] += 1
        else:
            focal_lengths_by_lens_dict[lens][focalLength] = 1
    else:
        focal_lengths_by_lens_dict[lens] = {focalLength: 1}

def check_focal_length(lens, focalLength):
    if focalLength in focal_length_set:
        lens_by_focal_length_dict[focalLength][lens] = lens_by_focal_length_dict[focalLength].get(lens, 0) + 1
    else:
        lens_by_focal_length_dict[focalLength] = {lens: 1}

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
    lens_set.clear()
    focal_length_set.clear()
    progress = 0
    progress_signal.emit(progress)
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.nef']  # Add more if needed
    processed_files = 0
    valid_image_files = []

    # First pass: gather all valid image files
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if os.path.splitext(file_name.lower())[1] in valid_extensions:
                file_path = os.path.join(root, file_name)
                valid_image_files.append(file_path)

    for file_path in valid_image_files:
        # image_files_count += 1
        # self.progress_bar.setValue(image_files_count)
        try:
            tags = is_valid_image(file_path)
            if tags:
                lens = tags.get('EXIF LensModel')
                focal_length_tag = tags.get('EXIF FocalLength')
                if lens and focal_length_tag:
                    lens = str(lens)
                    focal_length = round(convert_focal_length(focal_length_tag))
                    if focal_length is not None:
                        check_lens(lens, focal_length)
                        check_focal_length(lens, focal_length)
                        lens_set.add(lens)
                        focal_length_set.add(focal_length)
                else:
                    print(f"Missing EXIF data for {file_name}")
            processed_files += 1
            progress = int((processed_files / len(valid_image_files)) * 100)
            progress_signal.emit(progress)
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            continue

    # total_files = len(valid_image_files)
    # if total_files == 0:
    #     print("No valid image files found.")
    #     return  # Exit if no valid image files are found

    # for root, _, files in os.walk(folder_path):
    #     for file_name in files:
    #         try:
    #             file_path = os.path.join(root, file_name)
    #             if os.path.splitext(file_name.lower())[1] not in valid_extensions:
    #                 continue
    #             tags = is_valid_image(file_path)
    #             if tags:
    #                 lens = tags.get('EXIF LensModel')
    #                 print(lens)
    #                 focal_length_tag = tags.get('EXIF FocalLength')
    #                 if lens and focal_length_tag:
    #                     lens = str(lens)
    #                     focal_length = round(convert_focal_length(focal_length_tag))
    #                     if focal_length is not None:
    #                         check_lens(lens, focal_length)
    #                         check_focal_length(lens, focal_length)
    #                         lens_set.add(lens)
    #                         focal_length_set.add(focal_length)
    #                 else:
    #                     print(f"Missing EXIF data for {file_name}")
    #             processed_files += 1
    #             progress = int((processed_files / total_files) * 100)
    #             progress_signal.emit(progress)
    #         except Exception as e:
    #             print(f"Error processing file {file_path}: {e}")
    #             continue

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