from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QProgressBar, QPushButton, QFileDialog, QLabel, QApplication, QComboBox, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from constants import (
    focalLengthsByLens, focalLengths, lensByFocalLength, lensCount,
    defaultSelectionDropdownSelection,
    defaultFocalLengthOrderingDropdownSelection,
    imageCountDropdownSelection,
    defaultLensOrderingDropdownSelection,
    focalLengthCategory,
    lensCategory,
    graph_font
)
from BarGraphWidget import BarGraphWidget
from CustomScrollArea import CustomScrollArea
from util import searchImages, format_focal_length
from PyQt5.QtCore import Qt
from os.path import expanduser

class MainWindow(QMainWindow):
    def __init__(self, folder_path):
        super().__init__()
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout()
        main_widget.setLayout(self.main_layout)
        self.folderPath = folder_path

        title_font = QFont(graph_font, 17)
        title_font.setBold(True)
        subtitle_font = QFont(graph_font, 14)
        self.normal_font = QFont(graph_font, 12)

        self.fl_distribution_top_controls = QHBoxLayout()
        self.fl_distribution_top_controls.setContentsMargins(15, 15, 15, 0)
        self.main_layout.addLayout(self.fl_distribution_top_controls)

        self.fl_distribution_category_dropdown = QComboBox()
        self.fl_distribution_category_dropdown.setFont(self.normal_font)
        self.fl_distribution_ordering_dropdown = QComboBox()
        self.fl_distribution_ordering_dropdown.setFont(self.normal_font)
        self.create_fl_distribution_top_controls([])
        self.fl_distribution_top_controls.addItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.current_dir_label = QLabel(f"Current Directory: {folder_path}")
        self.current_dir_label.setFont(self.normal_font)
        self.current_dir_label.setContentsMargins(0, 0, 10, 0)
        change_dir_button = QPushButton("Change Directory")
        change_dir_button.setFont(self.normal_font)
        change_dir_button.clicked.connect(self.change_directory)
        self.fl_distribution_top_controls.addWidget(self.current_dir_label)
        self.fl_distribution_top_controls.addWidget(change_dir_button)

        self.fl_distribution_title_label = QLabel("Focal Length Distribution")
        self.fl_distribution_title_label.setAlignment(Qt.AlignCenter)
        self.fl_distribution_title_label.setFont(title_font)
        self.main_layout.addWidget(self.fl_distribution_title_label)

        self.fl_distribution_subtitle_label = QLabel("Images Selected: 0/0 (0%)")
        self.fl_distribution_subtitle_label.setAlignment(Qt.AlignCenter)
        self.fl_distribution_subtitle_label.setFont(subtitle_font)
        self.main_layout.addWidget(self.fl_distribution_subtitle_label)

        self.fl_distribution_scroll_area = CustomScrollArea()
        self.fl_distribution_scroll_area.setWidgetResizable(True)
        self.fl_distribution_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.main_layout.addWidget(self.fl_distribution_scroll_area)

        self.fl_distribution_graph = BarGraphWidget([], [], self.fl_distribution_subtitle_label, 0, focalLengthCategory, parent=self.fl_distribution_scroll_area)
        self.fl_distribution_scroll_area.setWidget(self.fl_distribution_graph)

        self.fl_distribution_category_dropdown.currentIndexChanged.connect(lambda: self.change_fl_distribution_category_dropdown())
        self.fl_distribution_ordering_dropdown.currentIndexChanged.connect(lambda: self.change_fl_distribution_ordering_dropdown())

        self.lens_distribution_top_controls = QHBoxLayout()
        self.lens_distribution_top_controls.setContentsMargins(15, 15, 0, 0)
        self.main_layout.addLayout(self.lens_distribution_top_controls)

        self.lens_distribution_category_dropdown = QComboBox()
        self.lens_distribution_category_dropdown.setFont(self.normal_font)
        self.lens_distribution_ordering_dropdown = QComboBox()
        self.lens_distribution_ordering_dropdown.setFont(self.normal_font)
        self.create_lens_distribution_top_controls([])
        self.lens_distribution_top_controls.addItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.lens_distribution_title_label = QLabel("Lens Distribution")
        self.lens_distribution_title_label.setAlignment(Qt.AlignCenter)
        self.lens_distribution_title_label.setFont(title_font)
        self.main_layout.addWidget(self.lens_distribution_title_label)

        self.lens_distribution_subtitle_label = QLabel("Images Selected: 0/0 (0%)")
        self.lens_distribution_subtitle_label.setAlignment(Qt.AlignCenter)
        self.lens_distribution_subtitle_label.setFont(subtitle_font)
        self.main_layout.addWidget(self.lens_distribution_subtitle_label)

        self.lens_distribution_scroll_area = CustomScrollArea()
        self.lens_distribution_scroll_area.setWidgetResizable(True)
        self.lens_distribution_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.main_layout.addWidget(self.lens_distribution_scroll_area)

        self.lens_distribution_graph = BarGraphWidget([], [], self.lens_distribution_subtitle_label, 0, lensCategory)
        self.lens_distribution_scroll_area.setWidget(self.lens_distribution_graph)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setTextVisible(True)
        self.main_layout.addWidget(self.progress_bar)

        self.lens_distribution_category_dropdown.currentIndexChanged.connect(lambda: self.change_lens_distribution_category_dropdown())
        self.lens_distribution_ordering_dropdown.currentIndexChanged.connect(lambda: self.change_lens_distribution_ordering_dropdown())

    def update_graphs(self, focalLengthCountDict, lensFocalLengthCountDict, lensImageCountDict, focalLengthLensDict):
        self.progress_bar.hide()
        self.focalLengths = focalLengthCountDict
        self.focalLengthsByLens = lensFocalLengthCountDict
        self.lensFocalLengthCountDict = lensFocalLengthCountDict
        self.lensImageCountDict = lensImageCountDict
        self.focalLengthLensDict = focalLengthLensDict
        self.sortedFocalLengthDict = sorted(self.focalLengths.items())
        self.change_fl_distribution_category_dropdown()
        self.change_lens_distribution_category_dropdown()

        self.fl_distribution_graph.setData(self.fl_distribution_categories, self.fl_distribution_values, self.fl_distribution_total_image_count)
        self.lens_distribution_graph.setData(self.lens_distribution_categories, self.lens_distribution_values, self.lens_distribution_total_image_count)

    def create_fl_distribution_top_controls(self, keys):
        self.fl_distribution_category_dropdown.addItem(defaultSelectionDropdownSelection)
        self.fl_distribution_category_dropdown.setCurrentText(defaultSelectionDropdownSelection)
        self.fl_distribution_category_dropdown.addItems(list(map(str, sorted(keys))))

        self.fl_distribution_ordering_dropdown.addItem(imageCountDropdownSelection)
        self.fl_distribution_ordering_dropdown.addItem(defaultFocalLengthOrderingDropdownSelection)
        self.fl_distribution_ordering_dropdown.setCurrentText(imageCountDropdownSelection)
        self.create_dropdown_row(self.fl_distribution_top_controls, {f'{defaultLensOrderingDropdownSelection}:': self.fl_distribution_category_dropdown, 'Ordering:': self.fl_distribution_ordering_dropdown})

    def create_lens_distribution_top_controls(self, keys):
        self.lens_distribution_category_dropdown.addItem(defaultSelectionDropdownSelection)
        self.lens_distribution_category_dropdown.setCurrentText(defaultSelectionDropdownSelection)
        self.lens_distribution_category_dropdown.addItems([format_focal_length(key) for key in sorted(list(keys))])

        self.lens_distribution_ordering_dropdown.addItem(imageCountDropdownSelection)
        self.lens_distribution_ordering_dropdown.addItem(defaultLensOrderingDropdownSelection)
        self.lens_distribution_ordering_dropdown.setCurrentText(imageCountDropdownSelection)
        self.create_dropdown_row(self.lens_distribution_top_controls, {f"{defaultFocalLengthOrderingDropdownSelection}:": self.lens_distribution_category_dropdown, 'Ordering:': self.lens_distribution_ordering_dropdown})

    def create_dropdown_row(self, layout, dropdowns):
        for label, dropdown in dropdowns.items():
            dropdown_label = QLabel(label)
            dropdown_label.setFont(self.normal_font)
            layout.addWidget(dropdown_label)
            layout.addWidget(dropdown)
            layout.addItem(QSpacerItem(20, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))

    def change_fl_distribution_category_dropdown(self):
        dropdown_selection = self.fl_distribution_category_dropdown.currentText()
        if dropdown_selection == defaultSelectionDropdownSelection:
            self.fl_distribution_categories, self.fl_distribution_values = zip(*self.sortedFocalLengthDict)
        else:
            self.fl_distribution_categories = tuple(sorted(self.focalLengthsByLens[dropdown_selection].keys()))
            self.fl_distribution_values = tuple(self.focalLengthsByLens[dropdown_selection][key] for key in self.fl_distribution_categories)
        self.fl_distribution_total_image_count = sum(self.fl_distribution_values)
        self.change_fl_distribution_ordering_dropdown()

    def change_fl_distribution_ordering_dropdown(self):
        dropdown_selection = self.fl_distribution_ordering_dropdown.currentText()
        if dropdown_selection == defaultFocalLengthOrderingDropdownSelection:
            sorted_pairs = sorted(zip(self.fl_distribution_categories, self.fl_distribution_values))
            self.fl_distribution_categories, self.fl_distribution_values = zip(*sorted_pairs)
        elif dropdown_selection == imageCountDropdownSelection:
            sorted_pairs = sorted(zip(self.fl_distribution_values, self.fl_distribution_categories), reverse=True)
            self.fl_distribution_values, self.fl_distribution_categories = zip(*sorted_pairs)
        self.fl_distribution_graph.setData(self.fl_distribution_categories, self.fl_distribution_values, self.fl_distribution_total_image_count)
        
    def change_lens_distribution_category_dropdown(self):
        dropdown_selection = self.lens_distribution_category_dropdown.currentText()
        if dropdown_selection == defaultSelectionDropdownSelection:
            self.lens_distribution_categories = tuple(self.lensImageCountDict.keys())
            self.lens_distribution_values = tuple(self.lensImageCountDict.values())
        else:
            self.lens_distribution_categories = tuple(sorted(self.focalLengthLensDict[float(dropdown_selection)].keys()))
            self.lens_distribution_values = tuple(self.focalLengthLensDict[float(dropdown_selection)][key] for key in self.lens_distribution_categories)
        self.lens_distribution_total_image_count = sum(self.lens_distribution_values)
        self.change_lens_distribution_ordering_dropdown()

    def change_lens_distribution_ordering_dropdown(self):
        dropdown_selection = self.lens_distribution_ordering_dropdown.currentText()
        if dropdown_selection == defaultLensOrderingDropdownSelection:
            sorted_pairs = sorted(zip(self.lens_distribution_categories, self.lens_distribution_values))
            self.lens_distribution_categories, self.lens_distribution_values = zip(*sorted_pairs)
        elif dropdown_selection == imageCountDropdownSelection:
            sorted_pairs = sorted(zip(self.lens_distribution_values, self.lens_distribution_categories), reverse=True)
            self.lens_distribution_values, self.lens_distribution_categories = zip(*sorted_pairs)
        self.lens_distribution_graph.setData(self.lens_distribution_categories, self.lens_distribution_values, self.lens_distribution_total_image_count)

    # Modify the change_directory function to include the progress bar
    def change_directory(self):
        self.folderPath = QFileDialog.getExistingDirectory(self, "Select Directory", expanduser(self.folderPath.rsplit('/', 1)[0]))
        if self.folderPath:
            self.current_dir_label.setText(f"Current Directory: {self.folderPath}")
            focalLengthsByLens.clear()
            focalLengths.clear()
            lensByFocalLength.clear()
            lensCount.clear()
            self.progress_bar.show()
            # Start the image processing in a separate thread
            self.thread = ImageProcessingThread(self.folderPath)
            self.thread.finished.connect(self.on_processing_finished)
            self.thread.start()

    def on_processing_finished(self):
        self.progress_bar.hide()

        # Reset focal length distribution category dropdown
        self.fl_distribution_category_dropdown.blockSignals(True)
        self.fl_distribution_category_dropdown.clear()
        self.fl_distribution_category_dropdown.addItem(defaultSelectionDropdownSelection)
        self.fl_distribution_category_dropdown.setCurrentText(defaultSelectionDropdownSelection)
        self.fl_distribution_category_dropdown.addItems(sorted(list(lensCount.keys())))
        self.fl_distribution_category_dropdown.blockSignals(False)
        self.sortedFocalLengthDict = sorted(self.focalLengths.items())
        self.fl_distribution_total_image_count = sum(self.focalLengths.values())
        self.fl_distribution_categories, self.fl_distribution_values = zip(*self.sortedFocalLengthDict)
        self.change_fl_distribution_category_dropdown()

        # Reset lens dropdown category dropdown
        self.lens_distribution_category_dropdown.blockSignals(True)
        self.lens_distribution_category_dropdown.clear()
        self.lens_distribution_category_dropdown.addItem(defaultSelectionDropdownSelection)
        self.lens_distribution_category_dropdown.setCurrentText(defaultSelectionDropdownSelection)
        self.lens_distribution_category_dropdown.addItems(list(map(str, sorted(lensByFocalLength.keys()))))
        self.lens_distribution_category_dropdown.blockSignals(False)
        self.sortedLensImageCountDict = sorted(self.lensImageCountDict.items())
        self.lens_distribution_total_image_count = sum(self.lensImageCountDict.values())
        self.lens_distribution_total_image_count, self.fl_distribution_values = zip(*self.sortedLensImageCountDict)
        self.change_lens_distribution_category_dropdown()

class ImageProcessingThread(QThread):
    progress_updated = pyqtSignal(int)

    def __init__(self, folderPath):
        super().__init__()
        self.folderPath = folderPath

    def run(self):
        # Your image processing logic
        searchImages(self.folderPath)
        self.progress_updated.emit(100)  # Assuming 100% progress at the end