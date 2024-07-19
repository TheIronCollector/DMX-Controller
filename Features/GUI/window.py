from typing import Union
import pygame

import Features.GUI as GUI

class Window:
    def __init__(self, xPos: int, yPos: int, width: int, height: int, color: tuple, name: str, border: int = 15, isBG: bool = False, isFixture: bool = False, followScroll: bool = False) -> None:        
        self.x: int = xPos
        self.y: int = yPos
        self.width: int = width
        self.height: int = height
        self.color: tuple = color
        self.name: str = name
        self.border: int = border
        self.followScroll: bool = followScroll

        self.bools: dict[bool] = {
            'isBG': isBG,
            'enabled': False,
            'onScreen': False,
            'isFixture': isFixture,
        }
        
        self.z = len(winList)

        self.attachments: list[Union['Window', 'GUI.Button', 'GUI.Slider', 'GUI.Scroll', 'GUI.Text']] = []

        self.parent: GUI.Window | None = None

        if isBG:
            bgList.append(self)
        else:
            winList.append(self)

    def draw(self, surface: pygame.Surface, events: list[pygame.event.Event], scroll: Union['GUI.Scroll', 'None'] = None) -> None:
        if not self.bools['enabled'] and not self.bools['isBG']:
            return

        if not self.parent:
            winRect = pygame.Rect(self.x, self.y - (0 if self.bools['isBG'] else scroll.verticalOffset), self.width, self.height)
        else:
            parent = self.parent
            parentX = parent.x
            parentY = parent.y - (0 if parent.bools['isBG'] else scroll.verticalOffset)
            
            while parent.parent is not None:
                parent = parent.parent
                parentX += parent.x
                parentY += parent.y - (0 if parent.bools['isBG'] else scroll.verticalOffset)
            
            winRect = pygame.Rect(self.x + parentX, self.y + parentY - scroll.verticalOffset, self.width, self.height)

        self.bools['onScreen'] = self.isOnSurface(surface, winRect)
        if not self.bools['onScreen']:
            return

        if self.bools['isBG']:
            bg_surface = pygame.Surface((winRect.width, winRect.height))
            bg_surface.fill(self.color)
            surface.blit(bg_surface, (winRect.x, winRect.y))
            
            for attachment in self.attachments:
                if not attachment.bools['enabled']:
                    attachment.bools['enabled'] = True
                attachment.draw(surface, events, scroll)
            
            return

        rect_surface = pygame.Surface((winRect.width, winRect.height), pygame.SRCALPHA)
        pygame.draw.rect(rect_surface, self.color, rect_surface.get_rect(), border_radius=self.border)
        surface.blit(rect_surface, (winRect.x, winRect.y))

        for attachment in self.attachments:
            if not attachment.bools['enabled']:
                attachment.bools['enabled'] = True
            attachment.draw(surface, events, scroll)
        
    def attach(self, element: Union['Window', 'GUI.Button', 'GUI.Slider', 'GUI.Scroll', 'GUI.Text']) -> None:
        element.parent = self
        self.attachments.append(element)

    def isOnSurface(self, surface: pygame.Surface, winRect: pygame.Rect):
        surfaceRect = surface.get_rect()
        return winRect.colliderect(surfaceRect)

bgList: list[Window] = []
winList: list[Window] = []