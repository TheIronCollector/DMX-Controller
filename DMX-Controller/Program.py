from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QScrollArea
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from customWidgets import fixture, button, rect, addFixture
import sys
import save_load
import toDMX
import win32api

# Constant for padding, FPS cap, etc.
FPS_CAP = 300  # Default FPS cap, you can retrieve dynamically from monitor
FIXTURE_PADDING_X = 300
FPS_LABEL_GEOMETRY = (10, -30, 70, 20)  # Relative geometry for FPS label in bottom left corner of screen
MAX_PAGE_NUM = 125  # With 8 scenes per page, 1000 total scenes are possible. (Value may change)

try:
    DEVICE = win32api.EnumDisplayDevices()
except:
    print("System is either not Windows or came across an error.")

# Variables
isSaving = False
atChases = False
cur_page = 1
scrollVal = 0
maxScrollVal = 0
maxHScrollVal = 0

# Get display refresh rate
def get_refresh_rate(device):
    settings = win32api.EnumDisplaySettings(device.DeviceName, -1)
    return getattr(settings, 'DisplayFrequency', 60)  # Fallback to 60Hz if unavailable

# FPS label creation with combined FPS and frame logic
def create_fps_label(parent, fps_cap=FPS_CAP):
    fps_label = QLabel(parent)
    fps_label.frames = 0

    try:
        fps_label.fps_cap = get_refresh_rate(DEVICE)
    except:
        fps_label.fps_cap = fps_cap

    fps_label.setFont(QFont('Arial', 12))
    fps_label.setStyleSheet("color: black; background-color: black;")
    fps_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)

    def update_fps():
        fps_label.setText(f"FPS: {fps_label.frames}")
        fps_label.frames = 0

    return fps_label, update_fps

# Tile fixtures based on available space
def tile_fixtures(fixture_list, max_x: int, min_y: int, height: int, width: int):
    global maxScrollVal, maxHScrollVal

    current_x = 0
    current_y = min_y
    max_y = min_y  # Initialize max_y to the starting position
    highest_x = 0

    for fix in fixture_list:
        # If the fixture doesn't fit horizontally, move to the next line
        if current_x + fix.width > max_x:
            current_x = 0
            current_y += fix.height

        # Place the fixture at the current position
        fix.setGeometry(current_x, current_y, fix.width, fix.height)

        # Update max_y to be the maximum y position reached by any fixture
        max_y = max(max_y, current_y + fix.height)

        # Update highest_x to the farthest right point reached
        highest_x = max(highest_x, current_x + fix.width)

        # Move the current_x position for the next fixture
        current_x += fix.width

    maxScrollVal = max_y - height
    maxHScrollVal = max(0, highest_x - width)

# Custom widget container class
class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

    def add_widget(self, widget):
        """ Add a widget to the main widget and show it """
        widget.setParent(self)
        widget.setEnabled(True)
        widget.setMouseTracking(True)
        widget.show()

    def remove_widget(self, widget):
        """ Remove a widget from the main widget by hiding and deleting it """
        widget.hide()
        widget.setParent(None)
        widget.deleteLater()

    def toggle_widget(self, widget):
        """ Toggle the visibility of a widget. Show if hidden, hide if shown. """
        if widget.isVisible():
            widget.hide()  # If the widget is currently visible, hide it
        else:
            widget.show()  # If the widget is currently hidden, show it

# Main window class
class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DMX Controller")
        self.showFullScreen()

        self.MainWidget = MainWidget()
        self.setCentralWidget(self.MainWidget)
        self.MainWidget.lower()

        # Creating the background
        self.add_BG()

        # Add other stuff layered on top of fixtures
        self.add_windows()

        # Tile fixtures dynamically
        self.tile_fixtures_in_window()

        # # Add FPS label
        # self.fps_label, self.update_fps = create_fps_label(self, fps_cap=FPS_CAP)
        # self.position_fps_label()
        # self.fps_label.show()

        # # Timer to control FPS and frame updates
        # self.setup_fps_timer()

    def add_windows(self):
        width = self.width()
        height = self.height()

        self.addFixtureWin = addFixture.AddFixture(width//2 - 150, height//2 - 125)
        self.Enter_button = button.Button(100, 250, 100, 25, "Add", lambda: 0 if self.addFixtureWin.textbox1.textbox.text() == "" 
                                          or self.addFixtureWin.textbox2.textbox.text() == "" 
                                          or self.addFixtureWin.textbox1.textbox.text() == "" 
                                          else self.add_fixture(self.addFixtureWin.textbox1.textbox.text(), 
                                             int(self.addFixtureWin.textbox2.textbox.text()), 
                                             int(self.addFixtureWin.textbox3.textbox.text())))
        self.Enter_button.setParent(self.addFixtureWin)
        
        self.MainWidget.add_widget(self.addFixtureWin)
        self.addFixtureWin.hide()

    def button_clicked(self, buttonName: str):
        global cur_page, isSaving, atChases

        if buttonName == 'Chases':
            if not atChases:
                atChases = True
                self.FixScrollWidget.hide()
                self.ChaseScrollWidget.show()
            else:
                atChases = False
                self.FixScrollWidget.show()
                self.ChaseScrollWidget.hide()

        if buttonName == 'AddFixture':
            self.MainWidget.toggle_widget(self.addFixtureWin)

        if buttonName == 'Save':
            isSaving = not isSaving

        if buttonName == '1':
            if isSaving:
                save_load.save(1 + 8 * (cur_page - 1), self)
                isSaving = False
            else:
                save_load.load(1 + 8 * (cur_page - 1), self)

        if buttonName == '2':
            if isSaving:
                save_load.save(2 + 8 * (cur_page - 1), self)
                isSaving = False
            else:
                save_load.load(2 + 8 * (cur_page - 1), self)

        if buttonName == '3':
            if isSaving:
                save_load.save(3 + 8 * (cur_page - 1), self)
                isSaving = False
            else:
                save_load.load(3 + 8 * (cur_page - 1), self)

        if buttonName == '4':
            if isSaving:
                save_load.save(4 + 8 * (cur_page - 1), self)
                isSaving = False
            else:
                save_load.load(4 + 8 * (cur_page - 1), self)

        if buttonName == '5':
            if isSaving:
                save_load.save(5 + 8 * (cur_page - 1), self)
                isSaving = False
            else:
                save_load.load(5 + 8 * (cur_page - 1), self)

        if buttonName == '6':
            if isSaving:
                save_load.save(6 + 8 * (cur_page - 1), self)
                isSaving = False
            else:
                save_load.load(6 + 8 * (cur_page - 1), self)

        if buttonName == '7':
            if isSaving:
                save_load.save(7 + 8 * (cur_page - 1), self)
                isSaving = False
            else:
                save_load.load(7 + 8 * (cur_page - 1), self)

        if buttonName == '8':
            if isSaving:
                save_load.save(8 + 8 * (cur_page - 1), self)
                isSaving = False
            else:
                save_load.load(8 + 8 * (cur_page - 1), self)

        if buttonName == 'Page Up':
            if cur_page < MAX_PAGE_NUM:
                cur_page += 1
                for button in self.sceneButtonList:
                    button.setText(f"{int(button.text) + 8}")

        if buttonName == 'Page Down':
            if cur_page > 1:
                cur_page -= 1
                for button in self.sceneButtonList:
                    button.setText(f"{int(button.text) - 8}")

    def add_BG(self):
        width = self.width()
        height = self.height()

        # BG
        self.MainWidget.add_widget(rect.Rect(0, 0, width, 150, 0x121212, self))
        self.MainWidget.add_widget(rect.Rect(width - 300, 150, 300, height - 150, 0x151515, self))

        # Buttons
        B1 = button.Button(width//12 + 100, 50, 50, 50, "1", lambda: self.button_clicked('1'))
        self.MainWidget.add_widget(B1)
        B2 = button.Button(2*width//12 + 100, 50, 50, 50, "2", lambda: self.button_clicked('2'))
        self.MainWidget.add_widget(B2)
        B3 = button.Button(3*width//12 + 100, 50, 50, 50, "3", lambda: self.button_clicked('3'))
        self.MainWidget.add_widget(B3)
        B4 = button.Button(4*width//12 + 100, 50, 50, 50, "4", lambda: self.button_clicked('4'))
        self.MainWidget.add_widget(B4)
        B5 = button.Button(5*width//12 + 100, 50, 50, 50, "5", lambda: self.button_clicked('5'))
        self.MainWidget.add_widget(B5)
        B6 = button.Button(6*width//12 + 100, 50, 50, 50, "6", lambda: self.button_clicked('6'))
        self.MainWidget.add_widget(B6)
        B7 = button.Button(7*width//12 + 100, 50, 50, 50, "7", lambda: self.button_clicked('7'))
        self.MainWidget.add_widget(B7)
        B8 = button.Button(8*width//12 + 100, 50, 50, 50, "8", lambda: self.button_clicked('8'))
        self.MainWidget.add_widget(B8)
        
        self.MainWidget.add_widget(button.Button(width - 200, 25, 120, 40, "Page Up", lambda: self.button_clicked("Page Up")))
        self.MainWidget.add_widget(button.Button(width - 200, 75, 120, 40, "Page Down", lambda: self.button_clicked("Page Down")))
        self.MainWidget.add_widget(button.Button(width - 135, 175, 120, 40, "Save", lambda: self.button_clicked('Save')))
        self.MainWidget.add_widget(button.Button(width - 265, 175, 120, 40, "Add Fixture", lambda: self.button_clicked('AddFixture')))
        # self.MainWidget.add_widget(button.Button(width - 200, 235, 120, 40, "Chases", lambda: self.button_clicked('Chases'))) Next update

        self.FixScrollWidget = QScrollArea()
        self.FixScrollContent = QWidget()
        self.FixScrollWidget.setGeometry(0, 150, width - 300, height - 150)
        self.FixScrollContent.setGeometry(0, 150, self.width() - 302, self.height() - 200)
        self.FixScrollWidget.setWidget(self.FixScrollContent)
        self.MainWidget.add_widget(self.FixScrollWidget)
        
        self.ChaseScrollWidget = QScrollArea()
        self.ChaseScrollContent = QWidget()
        self.ChaseScrollWidget.setGeometry(0, 150, width - 300, height - 150)
        self.ChaseScrollContent.setGeometry(0, 150, self.width() - 302, self.height() - 200)
        self.ChaseScrollWidget.setWidget(self.ChaseScrollContent)
        self.MainWidget.add_widget(self.ChaseScrollWidget)
        self.ChaseScrollWidget.hide()

        self.sceneButtonList = [B1, B2, B3, B4, B5, B6, B7, B8]

    # Dynamically add fixtures
    def add_fixture(self, name, start_channel, channel_mode, loading = False):
        new_fixture = fixture.Fixture(name, start_channel, channel_mode)
        new_fixture.setParent(self.FixScrollContent)
        new_fixture.show()
        self.tile_fixtures_in_window()

        # Update scroll content size based on fixtures
        self.FixScrollContent.setGeometry(0, 0, self.width() + maxHScrollVal, self.height() + maxScrollVal)

        if loading:
            return
        
        self.MainWidget.toggle_widget(self.addFixtureWin)
        self.addFixtureWin.textbox1.textbox.setText("")
        self.addFixtureWin.textbox2.textbox.setText("")
        self.addFixtureWin.textbox3.textbox.setText("")

    # Re-tile the fixtures when window size changes
    def tile_fixtures_in_window(self):
        width = self.width()
        tile_fixtures(fixture.fixtureList, width - FIXTURE_PADDING_X, 0, self.height(), self.width()) 

    # Position FPS label
    def position_fps_label(self):
        height = self.height()
        self.fps_label.setGeometry(
            FPS_LABEL_GEOMETRY[0],
            height + FPS_LABEL_GEOMETRY[1],  # Adjust Y-position based on window height
            FPS_LABEL_GEOMETRY[2],
            FPS_LABEL_GEOMETRY[3]
        )

    # Setup FPS timer
    def setup_fps_timer(self):
        self.render_timer = QTimer(self)
        self.render_timer.timeout.connect(self.update)
        self.render_timer.start(1000 // self.fps_label.fps_cap)

    # Update window content and FPS
    def update(self):
        super().update()
        self.fps_label.frames += 1
        if self.fps_label.frames >= self.fps_label.fps_cap:
            self.update_fps()

    # Key press event to close the window
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def closeEvent(self, event):
        toDMX.running = False
        if True:
            event.accept() # let the window close

    def __str__(self) -> str:
        return super().__str__()

# Run application
def run():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    run()