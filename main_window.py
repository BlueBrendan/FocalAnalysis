from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea, QPushButton, QFileDialog, QLabel, QApplication, QComboBox, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from constants import (
    focalLengthsByLens, focalLengths, lensByFocalLength, lensCount,
    defaultSelectionDropdownSelection,
    defaultFocalLengthOrderingDropdownSelection,
    imageCountDropdownSelection,
    defaultLensOrderingDropdownSelection,
    lensOrderingDropdownSortByLens,
    lensOrderingDropdownSortByImageCount,
    focalLengthChartTitle,
    focalLengthChartXLabel,
    focalLengthChartYLabel,
    lensChartTitle,
    lensChartXLabel,
    lensChartYLabel,
    focalLengthCategory,
    lensCategory,
    barWidthByCategory,
    screen_height_percentage,
    scrollbar_thresholds,
    plot_margins
)
from BarGraphWidget import BarGraphWidget
from create_plot import CreatePlot
from util import searchImages, format_focal_length
from PyQt5.QtCore import Qt
from os.path import expanduser

class MainWindow(QMainWindow):
    def __init__(self, focalLengthCountDict, lensFocalLengthCountDict, lensImageCountDict, focalLengthLensDict, folder_path):
        # focalLengthCountDict: {focal length: number of images at focal length}
        # lensFocalLengthCountDict: {lens: {focal_length: number of images at focal length from lens}}
        # lensImageCountDict: {lens: number of images from lens}
        # focalLengthLensDict: {focal length: {lens: number of images at focal length from lens}}
        super().__init__()
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.folderPath = folder_path

        # Create a horizontal layout for the dropdowns and current directory
        self.fl_distribution_top_controls = QHBoxLayout()
        self.fl_distribution_top_controls.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(self.fl_distribution_top_controls)

        self.fl_distribution_category_dropdown = QComboBox()
        self.fl_distribution_ordering_dropdown = QComboBox()
        self.create_top_controls(self.fl_distribution_category_dropdown, self.fl_distribution_ordering_dropdown, defaultFocalLengthOrderingDropdownSelection, 'Lens', lensFocalLengthCountDict.keys(), self.fl_distribution_top_controls)

        # Add directory controls
        self.current_dir_label = QLabel(f"Current Directory: {folder_path}")
        change_dir_button = QPushButton("Change Directory")
        change_dir_button.clicked.connect(self.change_directory)
        self.fl_distribution_top_controls.addWidget(self.current_dir_label)
        self.fl_distribution_top_controls.addWidget(change_dir_button)
        self.fl_distribution_top_controls.addItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.focalLengths = focalLengthCountDict
        self.focalLengthsByLens = lensFocalLengthCountDict
        self.lensFocalLengthCountDict = lensFocalLengthCountDict
        self.lensImageCountDict = lensImageCountDict
        self.focalLengthLensDict = focalLengthLensDict
        self.sortedFocalLengthDict = sorted(self.focalLengths.items())
        self.fl_distribution_total_image_count = sum(self.focalLengths.values())
        self.fl_distribution_categories, self.fl_distribution_values = zip(*self.sortedFocalLengthDict)
        self.lens_distribution_total_image_count = sum(lensImageCountDict.values())
        self.lens_distribution_categories = tuple(lensImageCountDict.keys())
        self.lens_distribution_values = tuple(lensImageCountDict.values())

        title_font = QFont("Arial", 16)
        title_font.setBold(True)
        subtitle_font = QFont("Arial", 13)

        # Focal Length Distribution
        self.fl_distribution_title_label = QLabel("Focal Length Distribution")
        self.fl_distribution_title_label.setAlignment(Qt.AlignCenter)
        self.fl_distribution_title_label.setFont(title_font)
        main_layout.addWidget(self.fl_distribution_title_label)

        self.fl_distribution_subtitle_label = QLabel(f"Images Selected: 0/{self.fl_distribution_total_image_count} (0%)")
        self.fl_distribution_subtitle_label.setAlignment(Qt.AlignCenter)
        self.fl_distribution_subtitle_label.setFont(subtitle_font)
        main_layout.addWidget(self.fl_distribution_subtitle_label)

        self.fl_distribution_scroll_area = QScrollArea()
        self.fl_distribution_scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.fl_distribution_scroll_area)

        self.fl_distribution_graph = BarGraphWidget(self.fl_distribution_categories, self.fl_distribution_values, self.fl_distribution_subtitle_label, self.fl_distribution_total_image_count, focalLengthCategory)
        self.fl_distribution_scroll_area.setWidget(self.fl_distribution_graph)

        # Connect top control dropdowns to lambda functions
        self.fl_distribution_category_dropdown.currentIndexChanged.connect(lambda: self.change_fl_distribution_category_dropdown(self.fl_distribution_category_dropdown.currentText()))
        self.fl_distribution_ordering_dropdown.currentIndexChanged.connect(lambda: self.change_fl_distribution_ordering_dropdown(self.fl_distribution_ordering_dropdown.currentText()))

        # Create a horizontal layout for the dropdowns and current directory
        self.lens_distribution_top_controls = QHBoxLayout()
        self.lens_distribution_top_controls.setContentsMargins(0, 0, 0, 0)
        main_layout.addLayout(self.lens_distribution_top_controls)

        self.lens_distribution_category_dropdown = QComboBox()
        self.lens_distribution_ordering_dropdown = QComboBox()
        self.create_lens_distribution_top_controls(focalLengthLensDict.keys())
        self.lens_distribution_top_controls.addItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Lens Distribution
        self.lens_distribution_title_label = QLabel("Lens Distribution")
        self.lens_distribution_title_label.setAlignment(Qt.AlignCenter)
        self.lens_distribution_title_label.setFont(title_font)
        main_layout.addWidget(self.lens_distribution_title_label)

        self.lens_distribution_subtitle_label = QLabel(f"Images Selected: 0/{self.fl_distribution_total_image_count} (0%)")
        self.lens_distribution_subtitle_label.setAlignment(Qt.AlignCenter)
        self.lens_distribution_subtitle_label.setFont(subtitle_font)
        main_layout.addWidget(self.lens_distribution_subtitle_label)

        self.lens_distribution_scroll_area = QScrollArea()
        self.lens_distribution_scroll_area.setWidgetResizable(True)
        main_layout.addWidget(self.lens_distribution_scroll_area)

        self.lens_distribution_graph = BarGraphWidget(self.lens_distribution_categories, self.lens_distribution_values, self.lens_distribution_subtitle_label, self.fl_distribution_total_image_count, lensCategory)
        self.lens_distribution_scroll_area.setWidget(self.lens_distribution_graph)

        # Connect top control dropdowns to lambda functions
        self.lens_distribution_category_dropdown.currentIndexChanged.connect(lambda: self.change_lens_distribution_category_dropdown(self.lens_distribution_category_dropdown.currentText()))
        self.lens_distribution_ordering_dropdown.currentIndexChanged.connect(lambda: self.change_lens_distribution_ordering_dropdown(self.lens_distribution_ordering_dropdown.currentText()))

    def create_top_controls(self, category_dropdown, ordering_dropdown, default_ordering, key, keys, layout):
        category_dropdown.addItem(defaultSelectionDropdownSelection)
        category_dropdown.setCurrentText(defaultSelectionDropdownSelection)
        category_dropdown.addItems(list(map(str, sorted(keys))))

        ordering_dropdown.addItem(default_ordering)
        ordering_dropdown.addItem(imageCountDropdownSelection)
        ordering_dropdown.setCurrentText(default_ordering)
        self.create_dropdown_row(layout, {f'{key}: ': category_dropdown, 'Ordering: ': ordering_dropdown})

    def create_lens_distribution_top_controls(self, keys):
        self.lens_distribution_category_dropdown.addItem(defaultSelectionDropdownSelection)
        self.lens_distribution_category_dropdown.setCurrentText(defaultSelectionDropdownSelection)
        self.lens_distribution_category_dropdown.addItems([format_focal_length(key) for key in sorted(list(keys))])

        self.lens_distribution_ordering_dropdown.addItem(defaultLensOrderingDropdownSelection)
        self.lens_distribution_ordering_dropdown.addItem(imageCountDropdownSelection)
        self.lens_distribution_ordering_dropdown.setCurrentText(defaultLensOrderingDropdownSelection)
        self.create_dropdown_row(self.lens_distribution_top_controls, {defaultLensOrderingDropdownSelection: self.lens_distribution_category_dropdown, 'Ordering: ': self.lens_distribution_ordering_dropdown})

    def create_dropdown_row(self, layout, dropdowns):
        for label, dropdown in dropdowns.items():
            layout.addWidget(QLabel(label))
            layout.addWidget(dropdown)
            layout.addItem(QSpacerItem(20, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))

    def change_fl_distribution_category_dropdown(self, dropdown_selection):
        if dropdown_selection == defaultSelectionDropdownSelection:
            self.fl_distribution_categories, self.fl_distribution_values = zip(*self.sortedFocalLengthDict)
        else:
            self.fl_distribution_categories = tuple(sorted(self.focalLengthsByLens[dropdown_selection].keys()))
            self.fl_distribution_values = tuple(self.focalLengthsByLens[dropdown_selection][key] for key in self.fl_distribution_categories)
        self.fl_distribution_total_image_count = sum(self.fl_distribution_values)
        self.change_fl_distribution_ordering_dropdown(self.fl_distribution_ordering_dropdown.currentText())

    def change_fl_distribution_ordering_dropdown(self, dropdown_selection):
        if dropdown_selection == defaultFocalLengthOrderingDropdownSelection:
            sorted_pairs = sorted(zip(self.fl_distribution_categories, self.fl_distribution_values))
            self.fl_distribution_categories, self.fl_distribution_values = zip(*sorted_pairs)
        elif dropdown_selection == lensOrderingDropdownSortByImageCount:
            sorted_pairs = sorted(zip(self.fl_distribution_values, self.fl_distribution_categories), reverse=True)
            self.fl_distribution_values, self.fl_distribution_categories = zip(*sorted_pairs)
        self.fl_distribution_graph.setData(self.fl_distribution_categories, self.fl_distribution_values, self.fl_distribution_total_image_count)
        
    def change_lens_distribution_category_dropdown(self, dropdown_selection):
        if dropdown_selection == defaultSelectionDropdownSelection:
            self.lens_distribution_categories = tuple(self.lensImageCountDict.keys())
            self.lens_distribution_values = tuple(self.lensImageCountDict.values())
        else:
            self.lens_distribution_categories = tuple(sorted(self.focalLengthLensDict[float(dropdown_selection)].keys()))
            self.lens_distribution_values = tuple(self.focalLengthLensDict[float(dropdown_selection)][key] for key in self.lens_distribution_categories)
        self.lens_distribution_total_image_count = sum(self.lens_distribution_values)
        self.change_lens_distribution_ordering_dropdown(self.lens_distribution_ordering_dropdown.currentText())

    def change_lens_distribution_ordering_dropdown(self, dropdown_selection):
        if dropdown_selection == defaultLensOrderingDropdownSelection:
            sorted_pairs = sorted(zip(self.lens_distribution_categories, self.lens_distribution_values))
            self.lens_distribution_categories, self.lens_distribution_values = zip(*sorted_pairs)
        elif dropdown_selection == lensOrderingDropdownSortByImageCount:
            sorted_pairs = sorted(zip(self.lens_distribution_values, self.lens_distribution_categories), reverse=True)
            self.lens_distribution_values, self.lens_distribution_categories = zip(*sorted_pairs)
        self.lens_distribution_graph.setData(self.lens_distribution_categories, self.lens_distribution_values, self.lens_distribution_total_image_count)

    def change_directory(self):
        self.folderPath = QFileDialog.getExistingDirectory(self, "Select Directory", expanduser(self.folderPath.rsplit('/', 1)[0]))
        if self.folderPath:
            self.current_dir_label.setText(f"Current Directory: {self.folderPath}")
            focalLengthsByLens.clear()
            focalLengths.clear()
            lensByFocalLength.clear()
            lensCount.clear()
            searchImages(self.folderPath)

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
            self.change_fl_distribution_category_dropdown(self.fl_distribution_category_dropdown.currentText())

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
            self.change_lens_distribution_category_dropdown(self.lens_distribution_category_dropdown.currentText())