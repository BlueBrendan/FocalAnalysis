from PyQt5.QtWidgets import QScrollArea

class CustomScrollArea(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)

    def scrollHorizontally(self, delta):
        self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + delta)