import pygame
import Features.GUI as GUI
import Features.DMX.toDMX as toDMX

images = {}

class Slider:
    def __init__(self, rect: pygame.Rect, minVal: int, maxVal: int, step: int, channel: int):
        self.x = rect.x
        self.y = rect.y
        self.width = rect.w
        self.height = rect.h
        self.minVal = minVal
        self.maxVal = maxVal
        self.step = step
        self.channel = channel

        self.curVal = toDMX.dmx_data[channel - 1]

        self.bools: dict[bool] = {
            'enabled': True,
            'isBG': False,
            'dragging': False,
        }

        self.parent: GUI.Window | None = None

    def draw(self, surface: pygame.Surface, events: list[pygame.event.Event], scroll):
        self.curVal = toDMX.dmx_data[self.channel - 1]

        if not self.bools['enabled']:
            return

        if self.parent is not None:
            parent = self.parent
            parentX = parent.x
            parentY = parent.y
            
            while parent.parent is not None:
                parent = parent.parent
                parentX += parent.x
                parentY += parent.y

            sliderRect: pygame.Rect = pygame.Rect(self.x + parentX, self.y + parentY - scroll.verticalOffset, self.width, self.height)
        
        else:
            sliderRect: pygame.Rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        pygame.draw.rect(surface, (18, 18, 18), sliderRect)
        slider_pos = sliderRect.x + (sliderRect.width // 2)
        slider_y_pos = sliderRect.y + self.height - (self.curVal - self.minVal) * (self.height / (self.maxVal - self.minVal))
        self.sliderIcon(surface, slider_pos, slider_y_pos, 25)

        if self.bools['dragging']:
            self.draw_value_display(surface, slider_pos, slider_y_pos - 20)

        self.handle_events(events, sliderRect, slider_pos, slider_y_pos)

        toDMX.dmx_data[self.channel - 1] = self.curVal

    @staticmethod
    def sliderIcon(surface: pygame.Surface, xPos: int, yPos: int, width: int, color: tuple = (0, 0, 0)):
        pygame.draw.circle(surface, color, (xPos, yPos), width // 2)

    def handle_events(self, events: list[pygame.event.Event], sliderRect: pygame.Rect, slider_pos: int, slider_y_pos: int):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_x, mouse_y = event.pos
                    if pygame.Rect(slider_pos - 15 // 2, slider_y_pos - 15 // 2, 15, 15).collidepoint(mouse_x, mouse_y):
                        self.bools['dragging'] = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    self.bools['dragging'] = False

            elif event.type == pygame.MOUSEMOTION:
                if self.bools['dragging']:
                    mouse_x, mouse_y = event.pos
                    relative_y = mouse_y - sliderRect.y
                    value_range = self.maxVal - self.minVal
                    self.curVal = self.maxVal - (relative_y / sliderRect.height) * value_range
                    self.curVal = max(self.minVal, min(self.curVal, self.maxVal))
                    self.curVal = round(self.curVal / self.step) * self.step

    def draw_value_display(self, surface: pygame.Surface, x: int, y: int):
        # Draw the value display above the slider
        font = pygame.font.SysFont(None, 24)
        value_text = font.render(f'{self.curVal}', True, (255, 255, 255))
        text_rect = value_text.get_rect(center=(x, y - 10))

        # Draw black rectangle behind the text
        pygame.draw.rect(surface, (0, 0, 0), (text_rect.x - 5, text_rect.y - 5, text_rect.width + 10, text_rect.height + 10))
        surface.blit(value_text, text_rect)
