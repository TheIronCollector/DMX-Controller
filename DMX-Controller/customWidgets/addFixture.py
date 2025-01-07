from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QIntValidator
from PyQt6.QtCore import Qt, QRect, QTimer
import customWidgets.textbox as textbox
import customWidgets.button as button

class AddFixture(QWidget):
    def __init__(self, x, y) -> None:
        super().__init__()

        # Set widget size and position (adjust based on your preferences)
        self.setGeometry(x, y, 300, 300)  # Example: 300x250 pixels
        self.setStyleSheet("background-color: transparent;")  # Ensure transparency around the rounded rect

        # Add three textboxes
        self.textbox1 = textbox.Textbox(20, 40, 260, 30, "Fixture Name:")
        self.textbox2 = textbox.Textbox(20, 100, 260, 30, "Fixture Starting Channel:")
        self.textbox3 = textbox.Textbox(20, 160, 260, 30, "Fixture Channel Mode:")
        
        # Set the parent of the textboxes to this widget
        self.textbox1.setParent(self)
        self.textbox2.setParent(self)
        self.textbox3.setParent(self)

        # Restrict textbox2 (Fixture Type) and textbox3 (Fixture Address) to only accept numbers
        int_validator = QIntValidator(1, 512, self)  # Allow numbers in the range 1-512
        self.textbox2.textbox.setValidator(int_validator)  # Apply validator to the QLineEdit in the textbox
        self.textbox3.textbox.setValidator(int_validator)  # Apply validator to the QLineEdit in the textbox

    def paintEvent(self, event):
        """ Paint a rounded rectangle background """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Set the background color (you can change the color as needed)
        painter.setBrush(QColor(0x121212))
        painter.setPen(Qt.PenStyle.NoPen)  # No border around the rect

        # Draw a rounded rectangle as the background for the window
        painter.drawRoundedRect(QRect(0, 0, self.width(), self.height()), 20, 20)
