from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QFont, QFontMetrics, QPen
from PyQt5.QtCore import Qt, QRect, QPoint
from constants import focalLengthCategory, lensCategory, graph_padding_constant, graph_font
from util import format_focal_length
from CustomScrollArea import CustomScrollArea

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
        max_height = max(self.values)
        self.available_height = self.height() - 100  # Leave some margin
        self.height_scaling = self.available_height / max_height if max_height > 0 else 1
        self.bar_positions = []
        self.num_categories = len(self.categories)
        self.total_width = 0
        self.bar_label_font = QFont(graph_font, 14)
        self.bar_label_font.setBold(True)
        self.x_axis_font = QFont(graph_font, 13)
        self.x_axis_font.setBold(False)
        self.available_width = self.width() - (graph_padding_constant * 2)
        total_bar_width = self.available_width * 0.5
        total_bar_space = self.available_width - total_bar_width
        if self.category == focalLengthCategory:
            if self.num_categories < 30:
                self.bar_width = total_bar_width / self.num_categories
                self.bar_spacing = total_bar_space / self.num_categories
            else:
                self.bar_width = 40
                self.bar_spacing = 30
        elif self.category == lensCategory:
            if self.num_categories < 7:
                self.bar_width = int(total_bar_width / self.num_categories)
                self.bar_spacing = int(total_bar_space / self.num_categories)
            else:
                self.bar_width = 350
                self.bar_spacing = 200
        self.draw_gridlines(painter)
        self.draw_bars(painter)
        if self.dragging:
            painter.setBrush(QColor(200, 200, 200, 100))
            painter.drawRect(self.selection_rect)

    def draw_gridlines(self, painter):
        # Draw vertical grid lines
        grid_pen = QPen(QColor(200, 200, 200), 1.6, Qt.SolidLine)
        painter.setPen(grid_pen)
        for i in range(1, self.num_categories):
            x = i * (self.bar_width + self.bar_spacing) + graph_padding_constant
            painter.drawLine(int(x), 40, int(x), self.height() - 55)
        # Draw horizontal grid lines
        num_horizontal_lines = 8
        increment = self.available_height / (num_horizontal_lines - 1)
        for i in range(num_horizontal_lines):
            y = int(i * increment)  # Ensure y is an integer
            painter.drawLine(graph_padding_constant, y, self.available_width + graph_padding_constant, y)
        # Draw the horizontal axis line
        painter.setPen(QPen(Qt.black, 1))
        x_axis_y = self.height() - 55  # Same as y offset used for bars
        painter.drawLine(graph_padding_constant, x_axis_y, self.available_width + graph_padding_constant, x_axis_y)
        # Draw the vertical axis line
        painter.drawLine(graph_padding_constant, x_axis_y, graph_padding_constant, 40)

    def draw_bars(self, painter):
        for i, value in enumerate(self.values):
            x = i * (self.bar_width + self.bar_spacing) + graph_padding_constant + (self.bar_spacing/2)
            height = int(value * self.height_scaling)
            if height > self.available_height:
                height = self.available_height  # Cap the height at the available space
            y = self.height() - height - 55  # Offset bars upwards
            self.total_width += self.bar_width
            self.total_width += self.bar_spacing

            self.bar_positions.append(QRect(int(x), y, int(self.bar_width), height))
            if i in self.selected_bars:
                painter.setBrush(QColor(250, 100, 100))
            else:
                painter.setBrush(QColor(100, 150, 250))
            painter.drawRect(int(x), y, int(self.bar_width), height)

            # Annotation at the top of each bar
            painter.setFont(self.bar_label_font)
            value_text = str(value)
            font_metrics = QFontMetrics(self.bar_label_font)
            value_text_width = font_metrics.width(value_text)
            value_text_x = int(x + (self.bar_width - value_text_width) / 2)
            value_text_y = int(y - 10)
            painter.drawText(value_text_x, value_text_y, value_text)

            # Label category at x-axis
            category_text = format_focal_length(self.categories[i]) if type(self.categories[i]) == float else self.categories[i]
            category_text_rect = QRect(int(x-graph_padding_constant), self.height() - 50, int(self.bar_width + (graph_padding_constant * 2)), 40)
            painter.setFont(self.x_axis_font)
            wrapped_text = QFontMetrics(self.x_axis_font).elidedText(category_text, Qt.TextElideMode.ElideNone, category_text_rect.width())
            painter.drawText(category_text_rect, Qt.AlignCenter | Qt.TextWordWrap, wrapped_text )
        if (self.category == focalLengthCategory and self.num_categories >= 30) or (self.category == lensCategory and self.num_categories >= 7):
            self.setMinimumWidth(self.total_width + (graph_padding_constant * 2))
        else:
            self.setMinimumWidth(0)

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

    def wheelEvent(self, event):
        sensitivity_factor = 2
        delta = event.angleDelta().y() * sensitivity_factor
        parent = self.parentWidget().parentWidget()
        if parent and isinstance(parent, CustomScrollArea):
            parent.scrollHorizontally(-delta)