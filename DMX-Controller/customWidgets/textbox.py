from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QColor

class Textbox(QWidget):
    def __init__(self, x, y, width, height, label, placeholder_text = "") -> None:
        super().__init__()

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label_text = label
        self.placeholder_text = placeholder_text

        # Set the geometry of the widget using pixel coordinates
        self.setGeometry(self.x, self.y, self.width, self.height + 30)  # Extra 30px for the label

        # Create a QLabel for the label text
        self.label = QLabel(self)
        self.label.setText(self.label_text)
        self.label.setGeometry(0, 0, self.width, 20)  # Label positioned above the textbox
        self.label.setStyleSheet("color: white; font-size: 12px;")  # White text for the label
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create a QLineEdit (textbox) for user input
        self.textbox = QLineEdit(self)
        self.textbox.setPlaceholderText(self.placeholder_text)
        self.textbox.setGeometry(0, 25, self.width, self.height)  # Position below the label
        self.textbox.setStyleSheet("background-color: 0x080808; color: black; border: none; padding: 5px;")

    def paintEvent(self, event):
        """ Optional: You can override the paint event if you want to add any custom painting logic """
        # Create a painter to fill the background (if needed)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set the background color to dark gray for the entire widget
        painter.setBrush(QColor(0x121212))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(QRect(0, 0, self.width, self.height + 30))  # Drawing the background
