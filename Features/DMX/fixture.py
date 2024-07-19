import pygame
from Features import GUI

class Fixture:
    def __init__(self, model: str = "Something", channel: int = 1, channelMode: int = 1) -> None:
        self.model: str = model
        self.channel: int = channel
        self.channelMode: int = channelMode

        # Debug
        # print(type(self.brand), self.brand)
        # print(type(self.channel), self.channel)
        # print(type(self.channelMode), self.channelMode)

        print(self.find_available_space())
        if self.channel == -1:
            del self
            return

        # Padding values
        side_padding = 20
        top_padding = 45
        bottom_padding = 40
        window_margin = 10

        # Calculate total width needed for sliders
        slider_width = 10
        spacing = 40
        total_width = self.channelMode * (slider_width + spacing) - spacing + 2 * side_padding
        
        # Calculate total height needed for sliders
        total_height = 255 + top_padding + bottom_padding

        # Find the current position for the new window
        self.x, self.y = self.calculate_position(total_width + window_margin, total_height + window_margin)

        # Create the window
        fixtureWin = GUI.window.Window(self.x, self.y, total_width, total_height, GUI._G.Colors['DarkGray3'], model, isFixture = True)
        GUI.window.bgList[0].attach(fixtureWin)

        start_x = (fixtureWin.width - total_width + side_padding) // 2
        start_y = top_padding

        self.sliders: list[GUI.Slider] = []

        for i in range(self.channelMode):
            sliderRect: pygame.Rect = pygame.Rect(side_padding // 2 + start_x + (slider_width + spacing) * i, start_y, slider_width, 255)
            slider = GUI.slider.Slider(sliderRect, 0, 255, 1, self.channel + i)
            fixtureWin.attach(slider)
            self.sliders.append(slider)

        fixList.append(self)

    def __str__(self) -> str:
        return f"Brand: {self.model}, Channels: {self.channel}"
    
    def find_available_space(self) -> str:
        if len(channelsList) != 512:
            return "Channel states list must be exactly 512 elements long."

        start_index = self.channel - 1  # Adjust for 0-based index

        # Check if the initial channel and subsequent channels are all False
        if all(channelsList[start_index + i] == False for i in range(self.channelMode)):
            # Mark the channels as occupied
            for i in range(start_index, start_index + self.channelMode):
                channelsList[i] = True
            return f"Channel {self.channel} to {self.channel + self.channelMode - 1} are now occupied."

        # Search for the next available space
        for i in range(512 - self.channelMode + 1):
            if all(channelsList[i + j] == False for j in range(self.channelMode)):
                # Mark the channels as occupied
                for j in range(i, i + self.channelMode):
                    channelsList[j] = True
                self.channel = i + 1
                return f"Available space found and occupied from channel {i + 1} to {i + self.channelMode}"

        self.channel = -1
        return "No available space found."
    
    def calculate_position(self, required_width: int, required_height: int):
        # Starting position
        x, y = 30, 50
        max_width = pygame.display.get_surface().get_width()

        for window in GUI.window.bgList[0].attachments:
            if type(window) == GUI.Window:
                if x + required_width + 300 > max_width:
                    x = 30
                    y += window.height + 10
                else:
                    x += window.width + 10

        return x, y

channelsList: list[int] = [False] * 512
fixList: list[Fixture] = []
data = []

def save():
    for fixture in fixList:
        sliderVals = []

        for slider in fixture.sliders:
            sliderVals.append(slider.curVal)

        data.append([fixture.model, fixture.channel, fixture.channelMode, sliderVals])