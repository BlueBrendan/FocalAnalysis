import os
from PIL import Image, ExifTags
from constants import lensModelExif, focalLengthIn35mmExif, focalLengthsByLens, lensCount, focalLengths, lensByFocalLength
import exifread

def format_focal_length(focal_length):
    if focal_length.is_integer():
        return str(int(focal_length))
    else:
        return f"{focal_length:.1f}"

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
        lensByFocalLength[focalLength][lens] = lensByFocalLength[focalLength].get(lens, 0) + 1
    else:
        focalLengths[focalLength] = 1
        lensByFocalLength[focalLength] = {lens: 1}

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
            return float(focal_length)
    return None
    

def searchImages(folder_path):
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.raw', '.nef']  # Add more if needed
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            try:
                file_path = os.path.join(root, file_name)
                # Check if the file has a valid image extension
                if os.path.splitext(file_name.lower())[1] not in valid_extensions:
                    continue
                tags = is_valid_image(file_path)
                if tags:
                    lens = tags.get('EXIF LensModel')
                    focal_length_tag = tags.get('EXIF FocalLength')
                    if lens and focal_length_tag:
                        lens = str(lens)
                        focal_length = convert_focal_length(focal_length_tag)
                        if focal_length is not None:
                            checkLens(lens, focal_length)
                            checkFocalLength(lens, focal_length)
                    else:
                        print(f"Missing EXIF data for {file_name}")
            except Exception as e:
                print(f"Error processing file {file_path}: {e}")
                continue 