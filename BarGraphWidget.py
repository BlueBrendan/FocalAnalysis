from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont, QFontMetrics, QPen, QMouseEvent
from PyQt6.QtCore import Qt, QRect, QPoint
from constants import (
    focal_length_category, 
    lens_category, 
    graph_padding_constant, 
    graph_font, 
    default_category_dropdown_selection,
    focal_length_category_thresehold, 
    lens_category_thresehold,
    focal_length_bar_width,
    focal_length_bar_spacing,
    lens_bar_width,
    lens_bar_spacing
)
from util import CustomScrollArea, format_focal_length 

class BarGraphWidget(QWidget):
    def __init__(self, categories, values, images_selection_text, total_image_count, category, fl_distribution_dropdown, lens_distribution_dropdown, selected_label, parent=None):
        super().__init__(parent)
        self.categories = categories
        self.values = values
        self.images_selection_text = images_selection_text
        self.total_image_count = total_image_count
        self.fl_distribution_dropdown = fl_distribution_dropdown
        self.lens_distribution_dropdown = lens_distribution_dropdown
        self.category = category
        self.setMinimumHeight(400)
        self.selected_bars = set()
        self.bar_positions = []
        self.selection_rect = QRect()
        self.drag_start = QPoint()
        self.dragging = False
        self.total_selected_percentage = 0

    def set_data(self, categories, values, total_image_count):
        self.categories = categories
        self.values = values
        self.total_image_count = total_image_count
        self.total_selected_percentage = 0
        self.selected_bars = set()
        self.images_selection_text.setText(f"Images Selected: 0/{self.total_image_count} (0%)")
        self.updateGeometry()
        self.update()

    def draw_gridlines(self, painter):
        # Draw vertical grid lines
        grid_pen = QPen(QColor(200, 200, 200), 0.5, Qt.PenStyle.SolidLine)
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
        painter.setPen(QPen(QColor(0, 0, 0), 1))
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
            painter.setPen(QColor(Qt.GlobalColor.black))
            if i in self.selected_bars:
                painter.setBrush(QColor(250, 100, 100))
            else:
                painter.setBrush(QColor(100, 150, 250))
            painter.drawRect(int(x), y, int(self.bar_width), height)

            # Annotation at the top of each bar
            painter.setFont(self.bar_label_font)
            painter.setPen(QColor(Qt.GlobalColor.white))
            value_text = str(value)
            font_metrics = QFontMetrics(self.bar_label_font)
            value_text_width = font_metrics.horizontalAdvance(value_text)
            value_text_x = int(x + (self.bar_width - value_text_width) / 2)
            value_text_y = int(y - 10)
            painter.drawText(value_text_x, value_text_y, value_text)

            # Label category at x-axis
            category_text = format_focal_length(self.categories[i]) if isinstance(self.categories[i], int) or isinstance(self.categories[i], float) else self.categories[i]
            category_text_rect = QRect(int(x-graph_padding_constant), self.height() - 50, int(self.bar_width + (graph_padding_constant * 2)), 40)
            painter.setFont(self.x_axis_font)
            wrapped_text = QFontMetrics(self.x_axis_font).elidedText(category_text, Qt.TextElideMode.ElideNone, category_text_rect.width())
            painter.drawText(category_text_rect, Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, wrapped_text )
        if (self.category == focal_length_category and self.num_categories > focal_length_category_thresehold) or (self.category == lens_category and self.num_categories > lens_category_thresehold):
            self.setMinimumWidth(self.total_width + (graph_padding_constant * 2))
        else:
            self.setMinimumWidth(0)

    # PyQt methods
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QColor(Qt.GlobalColor.white))
        max_height = max(self.values) if len(self.values) > 0 else 0
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
        if self.category == focal_length_category:
            if self.num_categories == 0:
                self.bar_width, self.bar_spacing = 0, 0
            elif self.num_categories <= focal_length_category_thresehold:
                self.bar_width = total_bar_width / self.num_categories
                self.bar_spacing = total_bar_space / self.num_categories
            else:
                self.bar_width = focal_length_bar_width
                self.bar_spacing = focal_length_bar_spacing
        elif self.category == lens_category:
            if self.num_categories == 0:
                self.bar_width, self.bar_spacing = 0, 0
            elif self.num_categories < lens_category_thresehold:
                self.bar_width = int(total_bar_width / self.num_categories)
                self.bar_spacing = int(total_bar_space / self.num_categories)
            else:
                self.bar_width = lens_bar_width
                self.bar_spacing = lens_bar_spacing
        self.draw_gridlines(painter)
        self.draw_bars(painter)
        if self.dragging:
            painter.setBrush(QColor(200, 200, 200, 100))
            painter.drawRect(self.selection_rect)

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

    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.dragging:
            selected_indices = set()
            selection_area = self.selection_rect.normalized()
            total_selected_value = 0
            for i, rect in enumerate(self.bar_positions):
                if selection_area.intersects(rect):
                    selected_indices.add(i)
                    total_selected_value += self.values[i]
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                self.selected_bars.update(selected_indices)
            elif event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                for bar in selected_indices:
                    if bar in self.selected_bars:
                        self.selected_bars.remove(bar)
                    else:
                        self.selected_bars.add(bar)
            else:
                self.selected_bars = selected_indices
            total_selected_value = sum(self.values[i] for i in self.selected_bars)
            self.total_selected_percentage = round((total_selected_value / self.total_image_count) * 100, 2) if total_selected_value > 0 else 0
            self.images_selection_text.setText(f"Images Selected: {total_selected_value}/{self.total_image_count} ({self.total_selected_percentage}%)")
            self.dragging = False
            self.update()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if len(self.selected_bars) == 1:
            selected_category = self.categories[self.selected_bars.pop()]
            if self.category == focal_length_category:
                self.lens_distribution_dropdown.setCurrentText(str(selected_category))
            elif self.category == lens_category:
                self.fl_distribution_dropdown.setCurrentText(selected_category)
        else:
            if self.category == focal_length_category:
                self.fl_distribution_dropdown.setCurrentText(default_category_dropdown_selection)
            elif self.category == lens_category:
                self.lens_distribution_dropdown.setCurrentText(default_category_dropdown_selection)

    def wheelEvent(self, event):
        sensitivity_factor = 2
        delta = event.angleDelta().y() * sensitivity_factor
        parent = self.parentWidget().parentWidget()
        if parent and isinstance(parent, CustomScrollArea):
            parent.scrollHorizontally(-delta)