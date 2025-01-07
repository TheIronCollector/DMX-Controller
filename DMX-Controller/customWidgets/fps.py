from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QFont

class FPSLabel(QLabel):
    def __init__(self, fps_cap: int = 60, parent=None):
        super().__init__(parent)
        self.frames = 0
        self.fps_cap = fps_cap
        self.setFont(QFont('Arial', 12))
        self.setStyleSheet("color: white; background-color: black;")
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        
        # Timer for updating FPS label
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_fps)
        self.update_timer.start(1000)  # Update every second

        # Timer to control frame rate
        self.frame_timer = QTimer(self)
        self.frame_timer.timeout.connect(self.increment_frame)
        self.frame_timer.start(1000 // self.fps_cap)  # Cap the FPS
    
    def increment_frame(self):
        self.frames += 1
    
    def update_fps(self):
        self.setText(f"FPS: {self.frames}")
        self.frames = 0

    def set_fps_cap(self, new_fps_cap: int):
        self.fps_cap = new_fps_cap
        self.frame_timer.start(1000 // self.fps_cap)