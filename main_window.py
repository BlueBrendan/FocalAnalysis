from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QProgressBar, QPushButton, QFileDialog, QLabel, QComboBox, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from constants import (
    focal_lengths_by_lens_dict,
    lens_by_focal_length_dict,
    default_category_dropdown_selection,
    default_focal_length_ordering_dropdown_selection,
    image_count_dropdown_selection,
    default_lens_ordering_dropdown_selection,
    focal_length_category,
    lens_category,
    graph_font,
    progress_bar_style_sheet
)
from BarGraphWidget import BarGraphWidget
from util import ImageProcessingThread, CustomScrollArea
from PyQt6.QtCore import Qt
from os.path import expanduser
from collections import Counter

class MainWindow(QMainWindow):
    def __init__(self, folder_path):
        super().__init__()
        self.setWindowTitle("FocalAnalysis")
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        self.main_layout = QVBoxLayout()
        main_widget.setLayout(self.main_layout)
        self.folderPath = folder_path

        title_font = QFont(graph_font, 16)
        title_font.setBold(True)
        subtitle_font = QFont(graph_font, 12)
        self.normal_font = QFont(graph_font, 12)

        # Create focal length distribution dropdowns
        self.fl_distribution_top_controls = QHBoxLayout()
        self.fl_distribution_top_controls.setContentsMargins(15, 15, 15, 0)
        self.main_layout.addLayout(self.fl_distribution_top_controls)
        self.fl_distribution_category_dropdown = QComboBox()
        self.fl_distribution_category_dropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.fl_distribution_category_dropdown.setFont(self.normal_font)
        self.fl_distribution_ordering_dropdown = QComboBox()
        self.fl_distribution_ordering_dropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.fl_distribution_ordering_dropdown.setFont(self.normal_font)
        self.fl_distribution_categroy_dropdown_label = QLabel(f"{default_lens_ordering_dropdown_selection}:")
        self.fl_distribution_categroy_dropdown_label.setFont(self.normal_font)
        self.fl_distribution_ordering_dropdown_label = QLabel('Ordering:')
        self.fl_distribution_ordering_dropdown_label.setFont(self.normal_font)
        
        # Create directory controls
        self.current_dir_label = QLabel(f"Current Directory: {folder_path}")
        self.current_dir_label.setFont(self.normal_font)
        self.current_dir_label.setContentsMargins(0, 0, 10, 0)
        self.change_dir_button = QPushButton("Change Directory")
        self.change_dir_button.setFont(self.normal_font)
        self.change_dir_button.clicked.connect(self.change_directory)
        self.create_dropdown_rows(self.fl_distribution_top_controls, {self.fl_distribution_categroy_dropdown_label: self.fl_distribution_category_dropdown, self.fl_distribution_ordering_dropdown_label: self.fl_distribution_ordering_dropdown})
        self.fl_distribution_top_controls.addItem(QSpacerItem(20, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.fl_distribution_top_controls.addWidget(self.current_dir_label)
        self.fl_distribution_top_controls.addWidget(self.change_dir_button)

        # Create lens distribution dropdowns
        self.lens_distribution_top_controls = QHBoxLayout()
        self.lens_distribution_top_controls.setContentsMargins(15, 15, 0, 0)
        
        self.lens_distribution_category_dropdown = QComboBox()
        self.lens_distribution_category_dropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.lens_distribution_category_dropdown.setFont(self.normal_font)
        self.lens_distribution_ordering_dropdown = QComboBox()
        self.lens_distribution_ordering_dropdown.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        self.lens_distribution_ordering_dropdown.setFont(self.normal_font)
        self.lens_distribution_categroy_dropdown_label = QLabel(f"{default_focal_length_ordering_dropdown_selection}:")
        self.lens_distribution_categroy_dropdown_label.setFont(self.normal_font)
        self.lens_distribution_ordering_dropdown_label = QLabel('Ordering:')
        self.lens_distribution_ordering_dropdown_label.setFont(self.normal_font)

        # Create focal length distribution graph
        fl_distribution_title_label = QLabel("Focal Length Distribution")
        fl_distribution_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fl_distribution_title_label.setFont(title_font)
        self.main_layout.addWidget(fl_distribution_title_label)
        fl_distribution_subtitle_label = QLabel("Images Selected: 0/0 (0%)")
        fl_distribution_subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        fl_distribution_subtitle_label.setFont(subtitle_font)
        self.main_layout.addWidget(fl_distribution_subtitle_label)
        self.fl_distribution_selected_label = QLabel('Lens: <b>All</b>')
        self.fl_distribution_selected_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.fl_distribution_selected_label.setFont(subtitle_font)
        self.main_layout.addWidget(self.fl_distribution_selected_label)
        self.fl_distribution_scroll_area = CustomScrollArea()
        self.fl_distribution_scroll_area.setWidgetResizable(True)
        self.fl_distribution_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.main_layout.addWidget(self.fl_distribution_scroll_area)
        self.fl_distribution_graph = BarGraphWidget([], [], fl_distribution_subtitle_label, 0, focal_length_category, self.fl_distribution_category_dropdown, self.lens_distribution_category_dropdown, self.fl_distribution_selected_label, parent=self.fl_distribution_scroll_area)
        self.fl_distribution_scroll_area.setWidget(self.fl_distribution_graph)
        self.fl_distribution_category_dropdown.currentIndexChanged.connect(lambda: self.change_fl_distribution_category_dropdown())
        self.fl_distribution_ordering_dropdown.currentIndexChanged.connect(lambda: self.change_fl_distribution_ordering_dropdown())
        self.main_layout.addLayout(self.lens_distribution_top_controls)

        # Create lens distribution graph
        lens_distribution_title_label = QLabel("Lens Distribution")
        lens_distribution_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lens_distribution_title_label.setFont(title_font)
        self.main_layout.addWidget(lens_distribution_title_label)
        lens_distribution_subtitle_label = QLabel("Images Selected: 0/0 (0%)")
        lens_distribution_subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lens_distribution_subtitle_label.setFont(subtitle_font)
        self.main_layout.addWidget(lens_distribution_subtitle_label)
        self.lens_distribution_selected_label = QLabel('Focal Length: <b>All</b>')
        self.lens_distribution_selected_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lens_distribution_selected_label.setFont(subtitle_font)
        self.main_layout.addWidget(self.lens_distribution_selected_label)
        self.lens_distribution_scroll_area = CustomScrollArea()
        self.lens_distribution_scroll_area.setWidgetResizable(True)
        self.lens_distribution_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.main_layout.addWidget(self.lens_distribution_scroll_area)
        self.lens_distribution_graph = BarGraphWidget([], [], lens_distribution_subtitle_label, 0, lens_category, self.fl_distribution_category_dropdown, self.lens_distribution_category_dropdown, self.lens_distribution_selected_label)
        self.lens_distribution_scroll_area.setWidget(self.lens_distribution_graph)
        self.create_dropdown_rows(self.lens_distribution_top_controls, {self.lens_distribution_categroy_dropdown_label: self.lens_distribution_category_dropdown, self.lens_distribution_ordering_dropdown_label: self.lens_distribution_ordering_dropdown})
        self.lens_distribution_top_controls.addItem(QSpacerItem(20, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.progress_container = QWidget(self)
        self.progress_layout = QVBoxLayout(self.progress_container)
        self.progress_layout.setContentsMargins(0, 0, 0, 0)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(30)
        self.progress_bar.setStyleSheet(progress_bar_style_sheet)
        self.progress_bar.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.main_layout.addWidget(self.progress_bar)
        size_policy = self.progress_bar.sizePolicy()
        size_policy.setRetainSizeWhenHidden(True)
        self.progress_bar.setSizePolicy(size_policy)

        self.lens_distribution_category_dropdown.currentIndexChanged.connect(lambda: self.change_lens_distribution_category_dropdown())
        self.lens_distribution_ordering_dropdown.currentIndexChanged.connect(lambda: self.change_lens_distribution_ordering_dropdown())

    def create_graph(self, focal_lengths_by_lens_dict, lens_by_focal_length_dict):
        self.progress_bar.setVisible(False)
        self.focal_lengths_by_lens = focal_lengths_by_lens_dict
        self.focalLengthLensDict = lens_by_focal_length_dict
        self.create_fl_distribution_top_controls(sorted(focal_lengths_by_lens_dict.keys()))
        self.create_lens_distribution_top_controls(sorted(lens_by_focal_length_dict.keys()))
        self.change_fl_distribution_category_dropdown()
        self.change_lens_distribution_category_dropdown()

        self.fl_distribution_graph.set_data(self.fl_distribution_categories, self.fl_distribution_values, self.fl_distribution_total_image_count)
        self.lens_distribution_graph.set_data(self.lens_distribution_categories, self.lens_distribution_values, self.lens_distribution_total_image_count)

    def create_fl_distribution_top_controls(self, keys):
        self.fl_distribution_category_dropdown.addItem(default_category_dropdown_selection)
        self.fl_distribution_category_dropdown.addItems(list(keys))
        self.fl_distribution_category_dropdown.setCurrentText(default_category_dropdown_selection)

        self.fl_distribution_ordering_dropdown.addItem(image_count_dropdown_selection)
        self.fl_distribution_ordering_dropdown.addItem(default_focal_length_ordering_dropdown_selection)
        self.fl_distribution_ordering_dropdown.setCurrentText(image_count_dropdown_selection)

    def create_lens_distribution_top_controls(self, keys):
        self.lens_distribution_category_dropdown.addItem(default_category_dropdown_selection)
        self.lens_distribution_category_dropdown.addItems(map(str,keys))
        self.lens_distribution_category_dropdown.setCurrentText(default_category_dropdown_selection)

        self.lens_distribution_ordering_dropdown.addItem(image_count_dropdown_selection)
        self.lens_distribution_ordering_dropdown.addItem(default_lens_ordering_dropdown_selection)
        self.lens_distribution_ordering_dropdown.setCurrentText(image_count_dropdown_selection)

    def create_dropdown_rows(self, layout, dropdowns):
        for dropdown_label, dropdown in dropdowns.items():
            layout.addWidget(dropdown_label)
            layout.addWidget(dropdown)
            layout.addItem(QSpacerItem(20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum))

    def change_fl_distribution_category_dropdown(self):
        dropdown_selection = self.fl_distribution_category_dropdown.currentText()
        self.fl_distribution_selected_label.setText((f"Lens: <b>{dropdown_selection}</b>"))
        if dropdown_selection == default_category_dropdown_selection:
            focal_length_dict = dict(sum((Counter(values) for values in self.focal_lengths_by_lens.values()), Counter()))
            self.fl_distribution_categories = tuple(focal_length_dict.keys())
            self.fl_distribution_values = tuple(focal_length_dict.values())
        else:
            self.fl_distribution_categories = tuple(sorted(self.focal_lengths_by_lens[dropdown_selection].keys()))
            self.fl_distribution_values = tuple(self.focal_lengths_by_lens[dropdown_selection][key] for key in self.fl_distribution_categories)
        self.fl_distribution_total_image_count = sum(self.fl_distribution_values)
        self.change_fl_distribution_ordering_dropdown()

    def change_fl_distribution_ordering_dropdown(self):
        dropdown_selection = self.fl_distribution_ordering_dropdown.currentText()
        if dropdown_selection == default_focal_length_ordering_dropdown_selection:
            sorted_pairs = sorted(zip(self.fl_distribution_categories, self.fl_distribution_values))
            self.fl_distribution_categories, self.fl_distribution_values = zip(*sorted_pairs)
        elif dropdown_selection == image_count_dropdown_selection:
            if self.fl_distribution_values and self.fl_distribution_categories:
                sorted_pairs = sorted(zip(self.fl_distribution_values, self.fl_distribution_categories), reverse=True)
                self.fl_distribution_values, self.fl_distribution_categories = zip(*sorted_pairs)
            else:
                self.fl_distribution_values, self.fl_distribution_categories = zip(*sorted(zip(self.fl_distribution_values, self.fl_distribution_categories), reverse=True)) if self.fl_distribution_values and self.fl_distribution_categories else [], []
        self.fl_distribution_graph.set_data(self.fl_distribution_categories, self.fl_distribution_values, self.fl_distribution_total_image_count)
        
    def change_lens_distribution_category_dropdown(self):
        dropdown_selection = self.lens_distribution_category_dropdown.currentText()
        new_label_text = f"Focal Length: <b>{dropdown_selection}</b>"
        self.lens_distribution_selected_label.setText(new_label_text)
        if dropdown_selection != default_category_dropdown_selection:
            self.lens_distribution_selected_label.setText(new_label_text + '<b>mm</b>')
        if dropdown_selection == default_category_dropdown_selection:
            lens_dict = dict(sum((Counter(values) for values in self.focalLengthLensDict.values()), Counter()))
            self.lens_distribution_categories = tuple(lens_dict.keys())
            self.lens_distribution_values = tuple(lens_dict.values())
        else:
            self.lens_distribution_categories = tuple(sorted(self.focalLengthLensDict[float(dropdown_selection)].keys()))
            self.lens_distribution_values = tuple(self.focalLengthLensDict[float(dropdown_selection)][key] for key in self.lens_distribution_categories)
        self.lens_distribution_total_image_count = sum(self.lens_distribution_values)
        self.change_lens_distribution_ordering_dropdown()

    def change_lens_distribution_ordering_dropdown(self):
        dropdown_selection = self.lens_distribution_ordering_dropdown.currentText()
        if dropdown_selection == default_lens_ordering_dropdown_selection:
            sorted_pairs = sorted(zip(self.lens_distribution_categories, self.lens_distribution_values))
            self.lens_distribution_categories, self.lens_distribution_values = zip(*sorted_pairs)
        elif dropdown_selection == image_count_dropdown_selection:
            if self.lens_distribution_categories and self.lens_distribution_values:
                sorted_pairs = sorted(zip(self.lens_distribution_values, self.lens_distribution_categories), reverse=True)
                self.lens_distribution_values, self.lens_distribution_categories = zip(*sorted_pairs)
            else:
                self.lens_distribution_values, self.lens_distribution_categories = [], []
        self.lens_distribution_graph.set_data(self.lens_distribution_categories, self.lens_distribution_values, self.lens_distribution_total_image_count)

    # Modify the change_directory function to include the progress bar
    def change_directory(self):
        self.folderPath = QFileDialog.getExistingDirectory(self, "Select Directory", expanduser(self.folderPath.rsplit('/', 1)[0]))
        if self.folderPath:
            self.current_dir_label.setText(f"Current Directory: {self.folderPath}")
            focal_lengths_by_lens_dict.clear()
            lens_by_focal_length_dict.clear()
            # Start the image processing in a separate thread
            self.thread = ImageProcessingThread(self.folderPath)
            self.thread.progress_updated.connect(self.update_progress)
            self.thread.finished.connect(self.on_processing_finished)
            self.thread.start()
            self.progress_bar.setVisible(True)

    def on_processing_finished(self):
        self.progress_bar.setVisible(False)
        # Reset focal length distribution category dropdown
        self.fl_distribution_category_dropdown.blockSignals(True)
        self.fl_distribution_category_dropdown.clear()
        self.fl_distribution_category_dropdown.addItem(default_category_dropdown_selection)
        self.fl_distribution_category_dropdown.setCurrentText(default_category_dropdown_selection)
        self.fl_distribution_category_dropdown.addItems(sorted(list(focal_lengths_by_lens_dict.keys())))
        self.fl_distribution_category_dropdown.blockSignals(False)
        self.fl_distribution_total_image_count = sum(sum(focal_length.values()) for focal_length in self.focal_lengths_by_lens.values())
        self.change_fl_distribution_category_dropdown()

        # Reset lens dropdown category dropdown
        self.lens_distribution_category_dropdown.blockSignals(True)
        self.lens_distribution_category_dropdown.clear()
        self.lens_distribution_category_dropdown.addItem(default_category_dropdown_selection)
        self.lens_distribution_category_dropdown.setCurrentText(default_category_dropdown_selection)
        self.lens_distribution_category_dropdown.addItems(list(map(str, sorted(lens_by_focal_length_dict.keys()))))
        self.lens_distribution_category_dropdown.blockSignals(False)
        self.lens_distribution_total_image_count = sum(sum(lens.values()) for lens in self.focalLengthLensDict.values())
        self.change_lens_distribution_category_dropdown()

    def update_progress(self, value):
        self.progress_bar.setValue(value)