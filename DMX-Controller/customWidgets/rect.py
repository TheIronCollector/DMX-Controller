from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import QRect, Qt

class Rect(QWidget):
    def __init__(self, x, y, width, height, color, parent=None):
        super().__init__(parent)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = QColor(color)

        # Set the widget's size to ensure the rectangle fits within it
        self.setMinimumSize(x + width, y + height)

        rectList.append(self)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(self.color)
        painter.setPen(Qt.PenStyle.NoPen)  # Remove the pen outline
        painter.drawRect(QRect(self.x, self.y, self.width, self.height))

rectList = []