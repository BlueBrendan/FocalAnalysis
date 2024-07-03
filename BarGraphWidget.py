from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QFontMetrics, QPen
from PyQt5.QtCore import Qt, QRect, QPoint
from constants import focalLengthCategory, focalLengthDistributionPaddingConstant, lensDistributionGraphPaddingConstant, graph_font
from util import format_focal_length
import math

class BarGraphWidget(QWidget):
    def __init__(self, categories, values, images_selection_text, total_image_count, category, parent=None):
        super().__init__(parent)
        self.categories = categories
        self.values = values
        self.images_selection_text = images_selection_text
        self.total_image_count = total_image_count
        self.category = category
        self.setMinimumHeight(400)
        self.selected_bars = set()  # Use a set to maintain unique selected bars
        self.bar_positions = []
        self.selection_rect = QRect()
        self.drag_start = QPoint()
        self.dragging = False
        self.total_selected_percentage = 0

    def setData(self, categories, values, total_image_count):
        self.categories = categories
        self.values = values
        self.total_image_count = total_image_count
        self.total_selected_percentage = 0
        self.selected_bars = set() 
        self.images_selection_text.setText(f"Images Selected: 0/{self.total_image_count} ({self.total_selected_percentage})%")
        self.updateGeometry()  # Update widget geometry to fit new data
        self.update()  # Trigger a repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        bar_width = 50 if self.category == focalLengthCategory else 200
        bar_spacing = 15 if self.category == focalLengthCategory else 200
        max_height = max(self.values)
        available_height = self.height() - 100  # Leave some margin
        if max_height > 0:
            height_scaling = available_height / max_height
        else:
            height_scaling = 1
        self.bar_positions = []

        total_width = 0
        bar_label_font = QFont(graph_font, 14)
        bar_label_font.setBold(True)
        x_axis_font = QFont(graph_font, 13)
        x_axis_font.setBold(False)
        paddingConstant = focalLengthDistributionPaddingConstant if self.category == focalLengthCategory else lensDistributionGraphPaddingConstant

        # Draw vertical grid lines
        grid_pen = QPen(QColor(200, 200, 200), 1.6, Qt.SolidLine)
        painter.setPen(grid_pen)
        num_vertical_lines = len(self.values)
        for i in range(1, num_vertical_lines):
            x = i * (bar_width + bar_spacing) + paddingConstant - bar_spacing // 2
            painter.drawLine(x, 40, x, self.height() - 55)
        # Draw horizontal grid lines
        num_horizontal_lines = 8
        increment = available_height / (num_horizontal_lines - 1)
        for i in range(num_horizontal_lines):
            y = int(i * increment)  # Ensure y is an integer
            painter.drawLine(20, y-10, self.width(), y)
        # Draw the horizontal axis line
        painter.setPen(QPen(Qt.black, 1))
        x_axis_y = self.height() - 55  # Same as y offset used for bars
        painter.drawLine(20, x_axis_y, self.width() - 20, x_axis_y)
        # Draw the vertical axis line
        painter.drawLine(20, x_axis_y, 20, 40)  # 40 is a top margin

        for i, value in enumerate(self.values):
            x = i * (bar_width + bar_spacing) + paddingConstant
            height = int(value * height_scaling)
            if height > available_height:
                height = available_height  # Cap the height at the available space
            y = self.height() - height - 55  # Offset bars upwards
            total_width += bar_width
            total_width += bar_spacing if i != len(self.values)-1 else paddingConstant * 2

            self.bar_positions.append(QRect(x, y, bar_width, height))
            if i in self.selected_bars:
                painter.setBrush(QColor(250, 100, 100))
            else:
                painter.setBrush(QColor(100, 150, 250))
            painter.drawRect(x, y, bar_width, height)

            # Annotation at the top of each bar
            painter.setFont(bar_label_font)
            value_text = str(value)
            font_metrics = QFontMetrics(bar_label_font)
            value_text_width = font_metrics.width(value_text)
            value_text_x = int(x + (bar_width - value_text_width) / 2)
            value_text_y = int(y - 10)
            painter.drawText(value_text_x, value_text_y, value_text)
            # Label category at x-axis
            category_text = format_focal_length(self.categories[i]) if type(self.categories[i]) == float else self.categories[i]
            category_text_rect = QRect(x-paddingConstant, self.height() - 50, bar_width + (paddingConstant * 2), 40)
            painter.setFont(x_axis_font)
            wrapped_text = QFontMetrics(x_axis_font).elidedText(category_text, Qt.TextElideMode.ElideNone, category_text_rect.width())
            painter.drawText(category_text_rect, Qt.AlignCenter | Qt.TextWordWrap, wrapped_text )

        if self.dragging:
            painter.setBrush(QColor(200, 200, 200, 100))
            painter.drawRect(self.selection_rect)
        self.setMinimumWidth(total_width)

    def mousePressEvent(self, event):
        self.drag_start = event.pos()
        self.selection_rect.setTopLeft(self.drag_start)
        self.selection_rect.setBottomRight(self.drag_start)
        self.dragging = True
        self.update()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.selection_rect.setBottomRight(event.pos())
            self.update()

    def mouseReleaseEvent(self, event):
        if self.dragging:
            selected_indices = set()
            selection_area = self.selection_rect.normalized()
            total_selected_value = 0
            for i, rect in enumerate(self.bar_positions):
                if selection_area.intersects(rect):
                    selected_indices.add(i)
                    total_selected_value += self.values[i]
            if not event.modifiers() & Qt.ShiftModifier:
                self.selected_bars = selected_indices
            else:
                self.selected_bars.update(selected_indices)
            total_selected_value = sum(self.values[i] for i in self.selected_bars)
            self.total_selected_percentage = round((total_selected_value / self.total_image_count) * 100, 2) if total_selected_value > 0 else 0
            self.images_selection_text.setText(f"Images Selected: {total_selected_value}/{self.total_image_count} ({self.total_selected_percentage}%)")
            self.dragging = False
            self.update()