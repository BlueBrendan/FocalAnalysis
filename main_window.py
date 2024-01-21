from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QApplication, QComboBox, QSpacerItem, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from constants import defaultSelectionDropdownSelection, defaultOrderingDropdownSelection, imageCountDropdownSelection, lensOrderingDropdownSortByLens, lensOrderingDropdownSortByImageCount, focalLengthChartTitle, focalLengthChartXLabel, focalLengthChartYLabel, lensChartTitle, lensChartXLabel, lensChartYLabel
from create_plot import CreatePlot

class MainWindow(QMainWindow):
    def __init__(self, focalLengths, focalLengthsByLens, lensCount, lensByFocalLength):
        super().__init__()
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # widget for dropdowns
        dropdowns_layout = QHBoxLayout()
        dropdowns_layout.setContentsMargins(10, 0, 10, 10)
        main_layout.addLayout(dropdowns_layout)

        self.focalLengths = focalLengths
        self.focalLengthsByLens = focalLengthsByLens
        self.sortedFocalLengthDict = sorted(self.focalLengths.items())
        categories, values = zip(*self.sortedFocalLengthDict)
        self.create_lens_selection_dropdown(focalLengthsByLens)
        self.create_ordering_dropdown()
        self.create_dropdown_row(dropdowns_layout, {'Lens: ': self.lens_selection_dropdown, 'Ordering: ': self.ordering_dropdown})

        # Create the figure and axis objects
        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(left=0.05, right=0.975, top=0.83, bottom=0.125)
        plt.margins(x=0.02)
        
        # Create a canvas to display the plot
        self.canvas = FigureCanvas(self.fig)
        main_layout.addWidget(self.canvas, 25)
        self.focal_length_plot = CreatePlot(self.ax, self.canvas, categories, values, focalLengths, focalLengthsByLens, self.lens_selection_dropdown.currentText(), self.ordering_dropdown.currentText(), focalLengthChartTitle, focalLengthChartXLabel, focalLengthChartYLabel)
        
        # widget for dropdowns
        dropdowns_2_layout = QHBoxLayout()
        dropdowns_2_layout.setContentsMargins(10, 0, 10, 10)
        main_layout.addLayout(dropdowns_2_layout)
        self.create_focal_length_selection_dropdown()
        self.create_lens_ordering_dropdown()
        self.create_dropdown_row(dropdowns_2_layout, {'Focal Length': self.focal_length_selection_dropdown, 'Ordering: ': self.lens_ordering_dropdown})

        # Create the figure and axis objects
        self.fig_2, self.ax_2 = plt.subplots()
        plt.subplots_adjust(left=0.05, right=0.975, top=0.83, bottom=0.125)
        plt.margins(x=0.02)
        
        # Create a canvas to display the plot
        self.canvas_2 = FigureCanvas(self.fig_2)
        main_layout.addWidget(self.canvas_2, 25)
        self.lens_plot = CreatePlot(self.ax_2, self.canvas_2, tuple(lensCount.keys()), tuple(lensCount.values()), lensCount, lensByFocalLength, self.lens_selection_dropdown.currentText(), self.ordering_dropdown.currentText(), lensChartTitle, lensChartXLabel, lensChartYLabel)
        screen_width, screen_height, window_width, window_height = self.determine_screen()
        # Set window size based on the user's monitor
        self.setGeometry((screen_width - window_width) // 2, (screen_height - window_height) // 2, window_width, window_height)

    def create_dropdown_row(self, layout, dropdowns):
        for label, dropdown in dropdowns.items():
            layout.addWidget(QLabel(label))
            layout.addWidget(dropdown)
            if label == 'Ordering: ':
                layout.addItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
            else:
                layout.addItem(QSpacerItem(20, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))

    def create_lens_selection_dropdown(self, lensDict):
        self.lens_selection_dropdown = QComboBox()
        self.lens_selection_dropdown.addItem(defaultSelectionDropdownSelection)
        self.lens_selection_dropdown.setCurrentText(defaultSelectionDropdownSelection)
        self.lens_selection_dropdown.addItems(sorted(list(lensDict.keys())))
        self.lens_selection_dropdown.currentIndexChanged.connect(lambda: self.focal_length_plot.update_plot(self.lens_selection_dropdown.currentText(), self.ordering_dropdown.currentText()))

    def create_ordering_dropdown(self):
        self.ordering_dropdown = QComboBox()
        self.ordering_dropdown.addItem(defaultOrderingDropdownSelection)
        self.ordering_dropdown.addItem(imageCountDropdownSelection)
        self.ordering_dropdown.setCurrentText(defaultOrderingDropdownSelection)
        self.ordering_dropdown.currentIndexChanged.connect(lambda: self.focal_length_plot.update_plot(self.lens_selection_dropdown.currentText(), self.ordering_dropdown.currentText()))

    def create_focal_length_selection_dropdown(self):
        self.focal_length_selection_dropdown = QComboBox()
        self.focal_length_selection_dropdown.addItem(defaultSelectionDropdownSelection)
        self.focal_length_selection_dropdown.setCurrentText(defaultOrderingDropdownSelection)
        focalLengths = tuple(sorted(self.focalLengths.keys()))
        for focalLength in focalLengths: 
            self.focal_length_selection_dropdown.addItem(str(focalLength)) 
        self.focal_length_selection_dropdown.currentIndexChanged.connect(lambda: self.lens_plot.update_plot(self.focal_length_selection_dropdown.currentText(), self.lens_ordering_dropdown.currentText()))

    def create_lens_ordering_dropdown(self):
        self.lens_ordering_dropdown = QComboBox()
        self.lens_ordering_dropdown.addItem(lensOrderingDropdownSortByLens)
        self.lens_ordering_dropdown.addItem(lensOrderingDropdownSortByImageCount)
        self.lens_ordering_dropdown.setCurrentText(lensOrderingDropdownSortByLens)
        self.lens_ordering_dropdown.currentIndexChanged.connect(lambda: self.lens_plot.update_plot(self.lens_selection_dropdown.currentText(), self.lens_ordering_dropdown.currentText()))

    def determine_screen(self):
        screen_resolution = QApplication.desktop().screenGeometry()
        screen_width = screen_resolution.width()
        screen_height = screen_resolution.height()

        window_width = int(screen_width * 0.85)
        window_height = int(screen_height * 0.8)
        return screen_width, screen_height, window_width, window_height