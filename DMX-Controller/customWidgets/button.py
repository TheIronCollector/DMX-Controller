from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QMouseEvent, QColor, QPainter, QFont, QPen

class Button(QWidget):
    def __init__(self, x, y, width, height, text, function, color=0x808080, hover_color="darkGray", press_color=0x202020) -> None:
        super().__init__()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.function = function
        self.color = QColor(color)  # Default color
        self.hover_color = QColor(hover_color)  # Color when hovered
        self.press_color = QColor(press_color)  # Color when pressed

        # Current color starts with the default color
        self.current_color = self.color

        # Define the button's geometry based on pixel coordinates
        self.setGeometry(x, y, width, height)

        self.is_pressed = False  # To track the button press state

    def paintEvent(self, event):
        """ Repaint the button with a rounded rectangle and centered text """
        # Create a painter object for drawing the rounded rect and the text
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # Enable anti-aliasing for smooth shapes
        
        # Draw the rounded rectangle
        painter.setBrush(self.current_color)  # Set the current color as the brush color
        painter.setPen(Qt.PenStyle.NoPen)  # Remove the pen outline
        painter.drawRoundedRect(QRect(0, 0, self.width, self.height), 15, 15)  # Draw the rounded rect

        # Set font properties
        font = QFont("Arial", 14)
        painter.setFont(font)

        # Set text color to bright red for visibility
        painter.setPen(QPen(QColor("white")))

        # Calculate the rectangle where the text will be drawn
        text_rect = QRect(0, 0, self.width, self.height)

        # Draw the text in the center of the button
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, self.text)

    def setText(self, text: str):
        """Set the text and trigger a repaint."""
        self.text = text
        self.update()  # Trigger a repaint of the widget

    def enterEvent(self, event):
        """ Change to hover color when the mouse enters """
        self.current_color = self.hover_color
        self.update()  # Trigger a repaint

    def leaveEvent(self, event):
        """ Revert to normal color when the mouse leaves """
        self.current_color = self.color
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        """ Change to pressed color when the mouse button is pressed """
        if event.button() == Qt.MouseButton.LeftButton:
            self.current_color = self.press_color
            self.is_pressed = True
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """ Trigger the function on mouse release if the button was pressed """
        if event.button() == Qt.MouseButton.LeftButton and self.is_pressed:
            self.current_color = self.hover_color  # Return to hover state
            self.is_pressed = False
            self.update()
            self.function()  # Run the assigned function when clicked
