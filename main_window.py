from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QApplication, QComboBox, QSpacerItem, QSizePolicy, QScrollBar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from constants import defaultSelectionDropdownSelection, defaultOrderingDropdownSelection, imageCountDropdownSelection, lensOrderingDropdownSortByLens, lensOrderingDropdownSortByImageCount, focalLengthChartTitle, focalLengthChartXLabel, focalLengthChartYLabel, lensChartTitle, lensChartXLabel, lensChartYLabel, focalLengthScrollbarThreshold, lensScrollbarThreshold, focalLengthCategory, lensCategory, barWidthByCategory
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

        self.fig, self.ax = plt.subplots()
        plt.subplots_adjust(left=0.05, right=0.975, top=0.83, bottom=0.125)
        plt.margins(x=0.005)
        self.canvas = FigureCanvas(self.fig)
        main_layout.addWidget(self.canvas, 20)

        self.create_lens_selection_dropdown(main_layout, focalLengthsByLens, categories, self.canvas, self.ax, focalLengthCategory)
        self.create_ordering_dropdown()
        self.create_dropdown_row(dropdowns_layout, {'Lens: ': self.lens_selection_dropdown, 'Ordering: ': self.ordering_dropdown})

        self.focal_length_plot = CreatePlot(self.ax, self.canvas, categories, values, focalLengths, focalLengthsByLens, self.lens_selection_dropdown.currentText(), self.ordering_dropdown.currentText(), focalLengthChartTitle, focalLengthChartXLabel, focalLengthChartYLabel)
        self.create_scroll_bar(self.canvas, categories, self.ax, main_layout, focalLengthCategory)

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
        main_layout.addWidget(self.canvas_2, 20)
        self.lens_plot = CreatePlot(self.ax_2, self.canvas_2, tuple(lensCount.keys()), tuple(lensCount.values()), lensCount, lensByFocalLength, self.lens_selection_dropdown.currentText(), self.ordering_dropdown.currentText(), lensChartTitle, lensChartXLabel, lensChartYLabel)
        
        # Create scroll bar for focal length plot
        self.create_scroll_bar(self.canvas_2, lensCount, self.ax_2, main_layout, lensCategory)
        
        screen_width, screen_height, window_width, window_height = self.determine_screen()
        # Set window size based on the user's monitor
        self.setGeometry((screen_width - window_width) // 2, (screen_height - window_height) // 2, window_width, window_height)

    def calculate_scrollbar_dimensions(self, axis):
        xmin = axis.get_xlim()[0]
        xmax = axis.get_xlim()[1]
        graph_gap = xmax - xmin
        return xmin, graph_gap

    def create_scroll_bar(self, canvas, categories, axis, main_layout, categoryType, dropdownSelection=None):
        xmin, graph_gap = self.calculate_scrollbar_dimensions(axis)
        self.focalLengthScrollbar = QScrollBar(self)
        self.focalLengthScrollbar.hide()
        if categoryType == focalLengthCategory:
            if len(categories) >= focalLengthScrollbarThreshold:
                self.focalLengthScrollbar.show()
                # Add a horizontal scrollbar for the focal length plot
                self.focalLengthScrollbar.setOrientation(1)  # Horizontal orientation
                self.focalLengthScrollbar.setMaximum(int(len(categories)) * 2)  # Adjust this based on your content
                self.focalLengthScrollbar.valueChanged.connect(lambda value: self.update_scroll(canvas, self.focalLengthScrollbar, value, categories, axis, xmin, graph_gap, categoryType))
                self.update_scroll(canvas, self.focalLengthScrollbar, self.focalLengthScrollbar.value(), categories, axis, xmin, graph_gap, categoryType)
                main_layout.addWidget(self.focalLengthScrollbar)
        elif categoryType == lensCategory and len(categories) >= lensScrollbarThreshold:
            self.lensScrollbar = QScrollBar(self)
            self.lensScrollbar.setOrientation(1)  # Horizontal orientation
            self.lensScrollbar.setMaximum(int(len(categories)) * 2)  # Adjust this based on your content
            self.lensScrollbar.valueChanged.connect(lambda value: self.update_scroll(canvas, self.lensScrollbar, value, categories, axis, xmin, graph_gap, categoryType))
            self.update_scroll(canvas, self.lensScrollbar, self.lensScrollbar.value(), categories, axis, xmin, graph_gap, categoryType)
            main_layout.addWidget(self.lensScrollbar)

    def update_scroll(self, canvas, scrollbar, scrollbar_value, categories, axis, xmin, graph_gap, categoryType, lensDropdownSelection=None):
        
        if lensDropdownSelection:
            categories = tuple(category for category in self.focalLengthsByLens[lensDropdownSelection])
            
            if len(categories) >= focalLengthScrollbarThreshold:
                self.focalLengthScrollbar.show()
            else:
                self.focalLengthScrollbar.hide()
        self.focalLengthScrollbar.setMaximum(int(len(categories)) * 2)  # Adjust this based on your content
        max_scroll = scrollbar.maximum()
        total_width = graph_gap - barWidthByCategory[categoryType]/len(categories)

        # Calculate new x-axis limits for the focal length plot
        xlim_start = scrollbar_value / max_scroll * total_width + xmin
        xlim_end = xlim_start + barWidthByCategory[categoryType]/len(categories)
        axis.set_xlim(xlim_start, xlim_end)
        canvas.draw()

    def create_dropdown_row(self, layout, dropdowns):
        for label, dropdown in dropdowns.items():
            layout.addWidget(QLabel(label))
            layout.addWidget(dropdown)
            if label == 'Ordering: ':
                layout.addItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
            else:
                layout.addItem(QSpacerItem(20, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))

    def create_lens_selection_dropdown(self, main_layout, lensDict, categories, canvas, axis, categoryType):
        self.lens_selection_dropdown = QComboBox()
        self.lens_selection_dropdown.addItem(defaultSelectionDropdownSelection)
        self.lens_selection_dropdown.setCurrentText(defaultSelectionDropdownSelection)
        self.lens_selection_dropdown.addItems(sorted(list(lensDict.keys())))
        self.lens_selection_dropdown.currentIndexChanged.connect(lambda: self.focal_length_plot.update_plot(self.lens_selection_dropdown.currentText(), self.ordering_dropdown.currentText()))
        self.lens_selection_dropdown.currentIndexChanged.connect(lambda: self.update_scroll(canvas, scrollbar, scrollbar_value, categories, axis, xmin, graph_gap, categoryType, self.lens_selection_dropdown.currentText()))

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