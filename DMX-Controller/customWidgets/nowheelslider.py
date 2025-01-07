from PyQt6.QtWidgets import QSlider
from PyQt6.QtCore import Qt

class NoWheelSlider(QSlider):
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(orientation, parent)

    def wheelEvent(self, event):
        # Override wheelEvent and do nothing to disable mouse wheel interaction
        event.ignore()

    # def mousePressEvent(self, event):
    #     print("NoWheelSlider - Mouse Press Event")
    #     super().mousePressEvent(event)
    
    # def mouseReleaseEvent(self, event):
    #     print("NoWheelSlider - Mouse Release Event")
    #     super().mouseReleaseEvent(event)