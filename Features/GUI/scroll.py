import pygame
import sys

import Features.GUI as GUI

class Scroll:
    def __init__(self, xPos: int, yPos: int, width: int, height: int, minScroll: int, maxScroll: int) -> None:
        self.x = xPos
        self.y = yPos
        self.width = width
        self.height = height
        self.minScroll = minScroll
        self.maxScroll = maxScroll
        self.scrollPos = minScroll
        self.scrollBarHeight = height * 0.1  # height of the scrollbar relative to the container height
        self.dragging = False
        self.scrollBarRect = pygame.Rect(self.x, self.y, self.width, self.scrollBarHeight)
        self.scrollBarColor = (100, 100, 100)
        self.backgroundColor = (200, 200, 200)
        self.verticalOffset = 0
        self.font = pygame.font.SysFont('Arial', 18)
        self.textColor = (0, 0, 0)

        self.bools: dict[bool] = {
            'isBG': False,
            'enabled': False,
        }

        self.parent: GUI.Window | None = None

    def draw(self, surface: pygame.Surface, events: list[pygame.event.Event], scroll) -> None:
        # Draw background
        pygame.draw.rect(surface, self.backgroundColor, (self.x, self.y, self.width, self.height), border_radius=10)

        # Update scrollbar position
        self.scrollBarRect.y = self.y + (self.scrollPos - self.minScroll) / (self.maxScroll - self.minScroll) * (self.height - self.scrollBarHeight)
        self.verticalOffset = (int)(self.scrollPos)
        
        # Draw scrollbar
        pygame.draw.rect(surface, self.scrollBarColor, self.scrollBarRect, border_radius=10)

        # Handle events
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.scrollBarRect.collidepoint(event.pos):
                    self.dragging = True
                    self.mouseYOffset = event.pos[1] - self.scrollBarRect.y

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if self.dragging:
                    self.scrollBarRect.y = event.pos[1] - self.mouseYOffset
                    self.scrollBarRect.y = max(self.y, min(self.scrollBarRect.y, self.y + self.height - self.scrollBarHeight))
                    self.scrollPos = self.minScroll + (self.scrollBarRect.y - self.y) / (self.height - self.scrollBarHeight) * (self.maxScroll - self.minScroll)
                    self.verticalOffset = self.scrollPos
        
        # Blit the current verticalOffset
        # offset_text = self.font.render(f'Offset: {self.verticalOffset:.2f}', True, self.textColor)
        # surface.blit(offset_text, (self.x + self.width + 10, self.y))

    def get_scroll_position(self) -> int:
        return int(self.scrollPos)

    def get_vertical_offset(self) -> int:
        return int(self.verticalOffset)

    def set_vertical_offset(self, val: int) -> None:
        self.scrollPos = max(self.minScroll, min(val, self.maxScroll))
        self.scrollBarRect.y = self.y + (self.scrollPos - self.minScroll) / (self.maxScroll - self.minScroll) * (self.height - self.scrollBarHeight)
        self.verticalOffset = int(self.scrollPos)

def main():
    # Example usage
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    scroll = Scroll(50, 50, 20, 300, 0, 100)

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill((255, 255, 255))
        scroll.draw(screen, events)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()