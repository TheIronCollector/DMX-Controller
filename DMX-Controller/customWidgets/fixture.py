from PyQt6.QtWidgets import QWidget, QSlider, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QFont
from PyQt6.QtCore import Qt, QRectF, QSize, QEvent
import toDMX
import customWidgets.nowheelslider as nws

class Fixture(QWidget):
    def __init__(self, name: str, start_channel: int, channel_mode: int, x: int = 0, y: int = 0):
        super().__init__()
        self.name = name
        self.start_channel = start_channel
        self.channel_mode = channel_mode
        self.sliders = []
        self.dropdown = None
        self.value_labels = []
        self.channel_labels = []
        self._x = x
        self._y = y
        self._width = 0
        self._height = 0
        self.min_y = 150
        
        print(self.find_available_space())
        if self.start_channel == -1:
            del self
            return

        # Add these to ensure maximum interactivity
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # Install an event filter to catch all events
        self.installEventFilter(self)

        self.initUI()
        fixtureList.append(self)
    
    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 30, 10, 10)  # Top margin for the name label
        sliders_layout = QHBoxLayout()
        
        for i in range(self.channel_mode):
            slider = nws.NoWheelSlider(Qt.Orientation.Vertical, self)
            slider.setRange(0, 255)

            value_label = QLabel("0")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value_label.setStyleSheet("color: rgba(255, 255, 255, 200);")
            
            channel_label = QLabel(str(self.start_channel + i))
            channel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            channel_label.setStyleSheet("color: rgba(255, 255, 255, 200);")
            
            slider_layout = QVBoxLayout()
            slider_layout.addWidget(value_label)
            slider_layout.addWidget(slider, alignment=Qt.AlignmentFlag.AlignHCenter)
            slider_layout.addWidget(channel_label)
            
            sliders_layout.addLayout(slider_layout)
            
            self.sliders.append(slider)
            self.value_labels.append(value_label)
            self.channel_labels.append(channel_label)
            
            slider.valueChanged.connect(lambda value, label=channel_label: self.updateValue(value, int(label.text())))
        
        main_layout.addLayout(sliders_layout)
        self.setLayout(main_layout)
        
        # Set a fixed size for the widget
        self.setFixedWidth(100 + 50 * self.channel_mode)
        self.setFixedHeight(300)
        self.width = 100 + 50 * self.channel_mode
        self.height = 300

        # Set initial position
        self.move(self._x, self._y)

    def find_available_space(self) -> str:
        if len(channelList) != 512:
            return "Channel states list must be exactly 512 elements long."

        start_index = self.start_channel - 1  # Adjust for 0-based index

        # Check if the initial channel and subsequent channels are all False
        if all(channelList[start_index + i] == False for i in range(self.channel_mode)):
            # Mark the channels as occupied
            for i in range(start_index, start_index + self.channel_mode):
                channelList[i] = True
            return f"Channel {self.start_channel} to {self.start_channel + self.channel_mode - 1} are now occupied."

        # Search for the next available space
        for i in range(512 - self.channel_mode + 1):
            if all(channelList[i + j] == False for j in range(self.channel_mode)):
                # Mark the channels as occupied
                for j in range(i, i + self.channel_mode):
                    channelList[j] = True
                self.start_channel = i + 1
                return f"Available space found and occupied from channel {i + 1} to {i + self.channel_mode}"

        self.channel = -1
        return "No available space found."

    def updateValueLabel(self):
        for i, slider in enumerate(self.sliders):
            self.value_labels[i].setText(str(slider.value()))
    
    def updateValue(self, value, channelValue):
        # print(f'{self.name}: Channel {channelValue} is now {value}')
        toDMX.dmx_data[channelValue - 1] = value
        self.updateValueLabel()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw rounded rectangle for the main widget
        rect = self.rect().adjusted(5, 5, -5, -5)
        path = QPainterPath()
        path.addRoundedRect(QRectF(rect), 15, 15)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(24, 24, 24))
        painter.drawPath(path)
        
        # Draw name label
        painter.setPen(QColor(255, 255, 255, 200))  # Semi-white color
        painter.setFont(QFont("Arial", 10))
        painter.drawText(rect.adjusted(10, 5, -10, 0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, self.name)

    def sizeHint(self):
        return QSize(100 + 50 * self.channel_mode, 300)

    # def eventFilter(self, obj, event):
    #     if obj is self:
    #         event_type = event.type()
    #         event_names = {
    #             QEvent.Type.MouseButtonPress: "MouseButtonPress",
    #             QEvent.Type.MouseButtonRelease: "MouseButtonRelease",
    #             QEvent.Type.MouseMove: "MouseMove",
    #             QEvent.Type.Enter: "Enter",
    #             QEvent.Type.Leave: "Leave",
    #             QEvent.Type.FocusIn: "FocusIn",
    #             QEvent.Type.FocusOut: "FocusOut"
    #         }
            
    #         if event_type in event_names:
    #             print(f"Fixture {self.name} - {event_names[event_type]} Event")
        
    #     return super().eventFilter(obj, event)

    # def event(self, event):
    #     print(f"Fixture {self.name} - General Event: {event.type()}")
    #     return super().event(event)

    # def mousePressEvent(self, event):
    #     print(f"Fixture {self.name} - Specific Mouse Press Event")
    #     super().mousePressEvent(event)

    # def mouseReleaseEvent(self, event):
    #     print(f"Fixture {self.name} - Specific Mouse Release Event")
    #     super().mouseReleaseEvent(event)

    # def enterEvent(self, event):
    #     print(f"Fixture {self.name} - Specific Enter Event")
    #     super().enterEvent(event)

    # def leaveEvent(self, event):
    #     print(f"Fixture {self.name} - Specific Leave Event")
    #     super().leaveEvent(event)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self.move(self._x, self._y)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self.move(self._x, self._y)

    @property
    def width(self):
        return self.size().width()
    
    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        return self.size().height()
    
    @height.setter
    def height(self, value):
        self._height = value

channelList: list[bool] = 512 * [False]
fixtureList = []
data = []

def save():
    for fixture in fixtureList:
        sliderVals = []

        for slider in fixture.sliders:
            sliderVals.append(slider.value())

        data.append([fixture.name, fixture.start_channel, fixture.channel_mode, sliderVals])

    print(data)