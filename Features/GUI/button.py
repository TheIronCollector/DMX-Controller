import pygame
from typing import Callable, Optional

import Features.GUI as GUI

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, color: tuple, text: str | None = None, border: int = 10, onClick: Optional[Callable[..., None]] = None) -> None:
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height
        self.color: tuple = color
        self.border: int = border
        self.clickFunction: Optional[Callable[..., None]] = onClick
        self.text: str = text
        
        self.isHovering: bool = False
        self.isPressed: bool = False
        self.parent: GUI.Window | None = None

        self.bools: dict[bool] = {
            'enabled': False
        }

        buttonList.append(self)

    def draw(self, surface: pygame.Surface, events: list[pygame.event.Event], scroll) -> None:
        if self.parent is not None:
            parent = self.parent
            parentX = parent.x
            parentY = parent.y
            
            while parent.parent is not None:
                parent = parent.parent
                parentX += parent.x
                parentY += parent.y

            buttonRect: pygame.Rect = pygame.Rect(self.x + parentX, self.y + parentY, self.width, self.height)

        else:
            buttonRect: pygame.Rect = pygame.Rect(self.x, self.y, self.width, self.height)

        mousePos: tuple = pygame.mouse.get_pos()
        mousePressed: tuple = pygame.mouse.get_pressed()

        self.isHovering = buttonRect.collidepoint(mousePos)
        self.isPressed = mousePressed[0] and self.isHovering

        if self.isPressed:
            button_color = GUI._G.Colors['DarkGray3']
        elif self.isHovering:
            button_color = GUI._G.Colors['DarkGray5']
        else:
            button_color = self.color

        text = self.text
        try:
            text = str(int(self.text) + 8 * (GUI._G.pageNum - 1))
        except:
            pass

        self.draw_rounded_rect(surface, buttonRect, button_color, self.border)
        self.draw_centered_text(surface, text, buttonRect, (255, 255, 255))

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.isHovering:
                    if self.clickFunction:
                        self.clickFunction()
                    else:
                        print("No function attached")

    def draw_centered_text(self, surface: pygame.Surface, text: str, rect: pygame.Rect, color: tuple):
        font = pygame.font.SysFont(None, 24)
        
        # Render the text
        text_surface = font.render(text, True, color)
        # Get the rectangle of the text surface
        text_rect = text_surface.get_rect()
        # Center the text rectangle inside the given rectangle
        text_rect.center = rect.center
        # Draw the text onto the given surface
        surface.blit(text_surface, text_rect)

    @staticmethod
    def draw_rounded_rect(surface: pygame.Surface, rect: pygame.Rect, color: tuple, borderRadius: int) -> None:
        pygame.draw.rect(surface, color, rect, border_radius=borderRadius)

# Buttons
buttonList: list[Button] = []