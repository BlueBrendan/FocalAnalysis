import numpy as np
from PyQt5.QtWidgets import QScrollBar, QSizePolicy
from constants import defaultSelectionDropdownSelection, imageCountDropdownSelection, defaultBarGraphColor
from matplotlib.widgets import SpanSelector, Slider
from matplotlib.patches import Rectangle

class CreatePlot():
    def __init__(self, ax, canvas, categories, values, focalLengths, focalLengthsByLens, lensDropdownValue, orderingDropdownValue, title, xlabel, ylabel):
        self.ax = ax
        self.canvas = canvas
        self.categories = categories
        self.values = values
        self.focalLengths = focalLengths
        self.focalLengthsByLens = focalLengthsByLens
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.total_bar_width, self.initial_x = self.set_spacing(categories)

        # Create a bar chart
        x = np.arange(len(categories))  # x-axis locations for the bars
        self.bars, self.annotations = [], []
        self.selection_sum_text = self.ax.text(0.05, 0.95, "", transform=self.ax.transAxes,
                                               fontsize=12, ha='center', va='top')
        
        self.create_annotations(values, self.total_bar_width, self.initial_x)
        self.set_axis(self.total_bar_width, self.initial_x, categories, x)
        self.update_plot(lensDropdownValue, orderingDropdownValue)
        
        # Add span selector for bar selection
        self.span_selector = SpanSelector(ax, self.on_span_select, 'horizontal', useblit=True)
        self.selection_rectangle, self.selection_start = None, None

    def set_spacing(self, categories):
        self.bar_width = max(45/len(categories), 0.50)
        self.bar_spacing = max(30/len(categories), 0.35)
        num_categories = len(categories)
        total_bar_width = self.bar_width + self.bar_spacing
        total_width = num_categories * total_bar_width
        excess_space = (1 - total_width) / 2
        initial_x = excess_space + 0.5 * total_bar_width
        return total_bar_width, initial_x

    def set_axis(self, total_bar_width, initial_x, categories, x):
        self.ax.set_xticks([i * total_bar_width + initial_x for i in x])
        self.ax.set_xticklabels(categories)

        self.ax.xaxis.grid(True, linestyle='-', color='gray', alpha=0.5, zorder=0)
        self.ax.yaxis.grid(True, linestyle='-', color='gray', alpha=0.5, zorder=0)

        self.ax.set_title(self.title, pad=35, fontweight='bold')
        self.ax.set_xlabel(self.xlabel, labelpad=10)
        self.ax.set_ylabel(self.ylabel)

        self.image_count = self.ax.text(0.5, 1.05, f"Total Images: {self.sum}", transform=self.ax.transAxes,
                     fontsize=12, ha='center', va='center')

    def create_annotations(self, values, total_bar_width, initial_x):
        self.text_annotations = []
        self.sum = 0

        # Populate the text_annotations list with initial annotations
        for i, v in enumerate(values):
            self.sum += v
            annotation = self.ax.text(i * total_bar_width + initial_x, v, str(v), ha='center', va='bottom')
            self.text_annotations.append(annotation)

    def update_plot(self, lensDropdownText, orderingDropdownText):
        for bar in self.bars:
            bar.remove()
        for annotation in self.text_annotations:
            annotation.remove()
        if lensDropdownText == defaultSelectionDropdownSelection:
            lens_data = self.focalLengths
        else:
            lens_data = self.focalLengthsByLens[lensDropdownText]

        self.sortedFocalLengthDict = sorted(lens_data.items())
        categories, values = zip(*self.sortedFocalLengthDict)
        if orderingDropdownText == imageCountDropdownSelection:
            combined_tuples = zip(categories, values)
            sorted_combined_tuples = sorted(combined_tuples, key=lambda x: x[1], reverse=True)
            categories, values = zip(*sorted_combined_tuples)
        total_bar_width, initial_x = self.set_spacing(categories)
        self.categories, self.values, self.total_bar_width, self.initial_x = categories, values, total_bar_width, initial_x

        # Create a bar chart
        x = np.arange(len(categories))  # x-axis locations for the bars
        self.bars = self.ax.bar([i * total_bar_width + initial_x for i in x], values, width=self.bar_width, label='Values', facecolor=defaultBarGraphColor, zorder=2)

        # Set x-axis tick positions and labels
        self.ax.set_xticks([i * total_bar_width + initial_x for i in x])
        self.ax.set_xticklabels(categories)
        self.create_annotations(values, total_bar_width, initial_x)
        self.image_count.set_text(f"Total Images: {self.sum}")
        self.canvas.draw()

    def on_span_select(self, xmin, xmax):
        if xmin == xmax:
            for bar in self.bars:
                bar.set_facecolor(defaultBarGraphColor)
            self.image_count.set_text(f"Total Images: {self.sum}")
            self.canvas.draw()
            return
        
        if self.selection_rectangle:
            self.selection_rectangle.remove()

        x1, x2 = min(xmin, xmax), max(xmin, xmax)
        y1, y2 = min(self.ax.get_ylim()), max(self.ax.get_ylim())

        self.selection_rectangle = Rectangle((x1, y1), x2 - x1, y2 - y1,
                                             alpha=0.5, facecolor='red', edgecolor='black')
        self.ax.add_patch(self.selection_rectangle)

        # Determine which bars are inside the selected rectangle
        selected_indices = np.nonzero(
            np.array([x1 <= i * self.total_bar_width + self.initial_x <= x2
                      for i in range(len(self.categories))])
        )[0]

        # Calculate and display the sum of values inside the selection
        selected_values = [self.values[i] for i in selected_indices]
        self.image_count.set_text(f"Selected Images: {sum(selected_values)}")

        # Update the color of the selected bars
        for i, bar in enumerate(self.bars):
            if i in selected_indices:
                bar.set_facecolor('orange')  # Change color for selected bars
            else:
                bar.set_facecolor(defaultBarGraphColor)  # Reset color for unselected bars
        self.selection_rectangle.remove()
        self.selection_rectangle = None
        self.canvas.draw()
        