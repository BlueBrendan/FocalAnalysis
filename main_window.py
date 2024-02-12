from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QApplication, QComboBox, QSpacerItem, QSizePolicy, QScrollBar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from constants import defaultSelectionDropdownSelection, defaultOrderingDropdownSelection, imageCountDropdownSelection, lensOrderingDropdownSortByLens, lensOrderingDropdownSortByImageCount, focalLengthChartTitle, focalLengthChartXLabel, focalLengthChartYLabel, lensChartTitle, lensChartXLabel, lensChartYLabel, focalLengthScrollbarThreshold, focalLengthCategory, lensCategory, barWidthByCategory, screen_height_percentage, scrollbar_thresholds
from create_plot import CreatePlot

class MainWindow(QMainWindow):
    def __init__(self, focalLengths, focalLengthsByLens, lensCount, lensByFocalLength):
        super().__init__()
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        # widget for dropdowns
        dropdowns_focal_length_layout = QHBoxLayout()
        dropdowns_focal_length_layout.setContentsMargins(10, 0, 10, 10)
        main_layout.addLayout(dropdowns_focal_length_layout)

        self.focalLengths = focalLengths
        self.focalLengthsByLens = focalLengthsByLens
        self.sortedFocalLengthDict = sorted(self.focalLengths.items())
        categories, values = zip(*self.sortedFocalLengthDict)

        self.fig_focal_length, self.ax_focal_length = plt.subplots()
        plt.subplots_adjust(left=0.05, right=0.975, top=0.83, bottom=0.125)
        plt.margins(x=0.005,y=0.1)
        self.canvas_focal_length = FigureCanvas(self.fig_focal_length)
        main_layout.addWidget(self.canvas_focal_length, 20)

        self.create_lens_selection_dropdown(focalLengthsByLens, self.canvas_focal_length, self.ax_focal_length, focalLengthCategory)
        self.create_ordering_dropdown(self.canvas_focal_length, self.ax_focal_length, focalLengthCategory)
        self.create_dropdown_row(dropdowns_focal_length_layout, {'Lens: ': self.lens_selection_dropdown, 'Ordering: ': self.ordering_dropdown})

        # Create scrollbar for first plot
        self.focalLengthScrollbar = QScrollBar(self)
        self.focalLengthScrollbar.hide()

        self.focal_length_plot = CreatePlot(self.ax_focal_length, self.canvas_focal_length, categories, values, focalLengths, focalLengthsByLens, self.lens_selection_dropdown.currentText(), self.ordering_dropdown.currentText(), focalLengthChartTitle, focalLengthChartXLabel, focalLengthChartYLabel)
        self.create_scroll_bar(self.canvas_focal_length, categories, self.ax_focal_length, main_layout, focalLengthCategory)

        # widget for dropdowns
        dropdowns_lens_layout = QHBoxLayout()
        dropdowns_lens_layout.setContentsMargins(10, 0, 10, 10)
        main_layout.addLayout(dropdowns_lens_layout)

        self.lensCount = lensCount
        self.lensByFocalLength = lensByFocalLength
        self.lenses = sorted(lensCount.items())
        # Create the figure and axis objects
        self.fig_lens, self.axis_lens = plt.subplots()
        plt.subplots_adjust(left=0.05, right=0.975, top=0.83, bottom=0.125)
        plt.margins(x=0.02,y=0.1)
        
        # Create a canvas to display the plot
        self.canvas_lens = FigureCanvas(self.fig_lens)
        main_layout.addWidget(self.canvas_lens, 20)

        self.create_focal_length_selection_dropdown(self.canvas_lens, self.axis_lens, lensCategory)
        self.create_lens_ordering_dropdown( self.canvas_lens, self.axis_lens, lensCategory)
        self.create_dropdown_row(dropdowns_lens_layout, {'Focal Length': self.focal_length_selection_dropdown, 'Ordering: ': self.lens_ordering_dropdown})

        # Create scrollbar for second plot
        self.lensScrollbar = QScrollBar(self)
        self.lensScrollbar.hide()
        self.lens_plot = CreatePlot(self.axis_lens, self.canvas_lens, tuple(lensCount.keys()), tuple(lensCount.values()), lensCount, lensByFocalLength, self.lens_selection_dropdown.currentText(), self.ordering_dropdown.currentText(), lensChartTitle, lensChartXLabel, lensChartYLabel)
        
        # Create second scroll bar for lens plot
        self.create_scroll_bar(self.canvas_lens, lensCount, self.axis_lens, main_layout, lensCategory)
        
        screen_width, screen_height, window_width, window_height = self.determine_screen()
        # Set window size based on the user's monitor
        self.setGeometry((screen_width - window_width) // 2, (screen_height - window_height) // 2, window_width, window_height)

    def calculate_scrollbar_dimensions(self, axis):
        xmin = axis.get_xlim()[0]
        xmax = axis.get_xlim()[1]
        graph_gap = xmax - xmin
        return xmin, graph_gap

    def create_scroll_bar(self, canvas, categories, axis, main_layout, categoryType):
        xmin, graph_gap = self.calculate_scrollbar_dimensions(axis)
        if categoryType == focalLengthCategory and len(categories) >= scrollbar_thresholds[categoryType]:
            self.focalLengthScrollbar.show()
            self.focalLengthScrollbar.setOrientation(1)  # Horizontal orientation
            self.focalLengthScrollbar.setMaximum(int(len(categories)) * 2)  # Adjust this based on your content
            self.focalLengthScrollbar.valueChanged.connect(lambda value: self.update_scroll(canvas, self.focalLengthScrollbar, value, categories, axis, xmin, graph_gap, categoryType))
            self.update_scroll(canvas, self.focalLengthScrollbar, self.focalLengthScrollbar.value(), categories, axis, xmin, graph_gap, categoryType)
            main_layout.addWidget(self.focalLengthScrollbar)
        elif categoryType == lensCategory and len(categories) >= scrollbar_thresholds[categoryType]:
            self.lensScrollbar.show()
            self.lensScrollbar.setOrientation(1)  # Horizontal orientation
            self.lensScrollbar.setMaximum(int(len(categories)) * 2)  # Adjust this based on your content
            self.lensScrollbar.valueChanged.connect(lambda value: self.update_scroll(canvas, self.lensScrollbar, value, categories, axis, xmin, graph_gap, categoryType))
            self.update_scroll(canvas, self.lensScrollbar, self.lensScrollbar.value(), categories, axis, xmin, graph_gap, categoryType)
            main_layout.addWidget(self.lensScrollbar)
    
    def validate_scroll(self, canvas, axis, scrollbar, dictionaryOfItems, tupleOfItems, dropdownSelection, categoryType):
        self.calculate_scrollbar_dimensions(axis)
        if dropdownSelection != defaultSelectionDropdownSelection:
            categories = tuple(category for category in dictionaryOfItems[dropdownSelection])
        else:
            categories = tuple(value[0] for value in tupleOfItems)
        if len(categories) >= scrollbar_thresholds[categoryType]:
            scrollbar.show()
            xmin, graph_gap = self.calculate_scrollbar_dimensions(axis)
            self.update_scroll(canvas, scrollbar, scrollbar.value(), categories, axis, xmin, graph_gap, categoryType)
        else:
            scrollbar.hide()

    def update_scroll(self, canvas, scrollbar, scrollbar_value, categories, axis, xmin, graph_gap, categoryType):
        scrollbar.setMaximum(int(len(categories)) * 2)  # Adjust this based on your content
        max_scroll = scrollbar.maximum()
        total_width = graph_gap - barWidthByCategory[categoryType]/len(categories)

        # Calculate new x-axis limits for the focal length plot
        xlim_start = scrollbar_value / max_scroll * total_width + xmin
        # Problem is the way xlim_end is calculated - it should never be greater than ~38.3ish
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

    def create_lens_selection_dropdown(self, lensDict, canvas, axis, categoryType):
        self.lens_selection_dropdown = QComboBox()
        self.lens_selection_dropdown.addItem(defaultSelectionDropdownSelection)
        self.lens_selection_dropdown.setCurrentText(defaultSelectionDropdownSelection)
        self.lens_selection_dropdown.addItems(sorted(list(lensDict.keys())))
        self.lens_selection_dropdown.currentIndexChanged.connect(lambda: self.focal_length_plot.update_plot(self.focalLengthsByLens, self.focalLengths, self.lens_selection_dropdown.currentText(), self.ordering_dropdown.currentText()))
        self.lens_selection_dropdown.currentIndexChanged.connect(lambda: self.validate_scroll(canvas, axis, self.focalLengthScrollbar, self.focalLengthsByLens, self.sortedFocalLengthDict, self.lens_selection_dropdown.currentText(), categoryType))

    def create_ordering_dropdown(self,canvas, axis, categoryType):
        self.ordering_dropdown = QComboBox()
        self.ordering_dropdown.addItem(defaultOrderingDropdownSelection)
        self.ordering_dropdown.addItem(imageCountDropdownSelection)
        self.ordering_dropdown.setCurrentText(defaultOrderingDropdownSelection)
        self.ordering_dropdown.currentIndexChanged.connect(lambda: self.focal_length_plot.update_plot(self.focalLengthsByLens, self.focalLengths, self.lens_selection_dropdown.currentText(), self.ordering_dropdown.currentText()))
        self.ordering_dropdown.currentIndexChanged.connect(lambda: self.validate_scroll(canvas, axis, self.focalLengthScrollbar, self.focalLengthsByLens, self.sortedFocalLengthDict, self.lens_selection_dropdown.currentText(), categoryType))

    def create_focal_length_selection_dropdown(self, canvas, axis, categoryType):
        self.focal_length_selection_dropdown = QComboBox()
        self.focal_length_selection_dropdown.addItem(defaultSelectionDropdownSelection)
        self.focal_length_selection_dropdown.setCurrentText(defaultOrderingDropdownSelection)
        focalLengths = tuple(sorted(self.focalLengths.keys()))
        for focalLength in focalLengths: 
            self.focal_length_selection_dropdown.addItem(str(focalLength)) 
        self.focal_length_selection_dropdown.currentIndexChanged.connect(lambda: self.lens_plot.update_plot(self.lensByFocalLength, self.lensCount, self.focal_length_selection_dropdown.currentText(), self.lens_ordering_dropdown.currentText()))
        self.focal_length_selection_dropdown.currentIndexChanged.connect(lambda: self.validate_scroll(canvas, axis, self.lensScrollbar, self.lensByFocalLength, self.lenses, self.focal_length_selection_dropdown.currentText(), categoryType))

    def create_lens_ordering_dropdown(self, canvas, axis, categoryType):
        self.lens_ordering_dropdown = QComboBox()
        self.lens_ordering_dropdown.addItem(lensOrderingDropdownSortByLens)
        self.lens_ordering_dropdown.addItem(lensOrderingDropdownSortByImageCount)
        self.lens_ordering_dropdown.setCurrentText(lensOrderingDropdownSortByLens)
        self.lens_ordering_dropdown.currentIndexChanged.connect(lambda: self.lens_plot.update_plot(self.lensByFocalLength, self.lensCount, self.focal_length_selection_dropdown.currentText(), self.lens_ordering_dropdown.currentText()))
        self.lens_ordering_dropdown.currentIndexChanged.connect(lambda: self.validate_scroll(canvas, axis, self.lensScrollbar, self.lensByFocalLength, self.lenses, self.focal_length_selection_dropdown.currentText(), categoryType))

    def determine_screen(self):
        screen_resolution = QApplication.desktop().screenGeometry()
        screen_width = screen_resolution.width()
        screen_height = screen_resolution.height()

        window_width = int(screen_width * 0.85)
        window_height = int(screen_height * screen_height_percentage)
        return screen_width, screen_height, window_width, window_height