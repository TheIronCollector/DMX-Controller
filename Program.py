import pygame
import sys
import math

import save_load
from Features import GUI, DMX
import pygame_textinput as text

saving: bool = False
addingFixture: bool = False

# Function that shows the FPS
def showFPS(surface: pygame.Surface, clock: pygame.time.Clock, font: pygame.font.Font):
    # Get the FPS
    fps = clock.get_fps()
    
    # Render the FPS on the screen
    fps_text = font.render(f"FPS: {fps:.2f}", True, pygame.Color('white'))
    surface.blit(fps_text, (5, surface.get_height() - 15))

# Function that creates all elements on screen
def createElements(width: int, height: int):
    global scroll, modelInput, modelInputRect, channelInput, channelRect, channelModeInput, channelModeRect, EnterButton

    scroll = GUI.Scroll(width - 160, 100, 10, height - 100, 0, 4700)

    modelInput = text.TextInputVisualizer(font_color = (255, 255, 255), cursor_color = (255, 255, 255))
    modelInputRect = pygame.Rect(width // 2 - 200, height // 2 - 120, 305, 15)
    channelInput = text.TextInputVisualizer(font_color = (255, 255, 255), cursor_color = (255, 255, 255))
    channelRect = pygame.Rect(width // 2 - 200, height // 2 - 70, 305, 15)
    channelModeInput = text.TextInputVisualizer(font_color = (255, 255, 255), cursor_color = (255, 255, 255))
    channelModeRect = pygame.Rect(width // 2 - 200, height // 2 - 20, 305, 15)

    fixtureButton: GUI.Button = GUI.Button(width - 145, height // 2 + 55, 140, 50, GUI._G.Colors['DarkGray4'], text = "Add Fixture", onClick = lambda: onButtonClick('addFixture'))
    saveButton: GUI.Button = GUI.Button(width - 145, height // 2 - 5, 140, 50, GUI._G.Colors['DarkGray4'], text = "Save", onClick = lambda: onButtonClick('saveButton'))
    sceneButton1: GUI.Button = GUI.Button((width - 150) // 8 - 150, 20, 50, 50, GUI._G.Colors['DarkGray4'], text = "1", onClick = lambda: onButtonClick('sceneButton1'))
    sceneButton2: GUI.Button = GUI.Button(2 * (width - 150) // 8 - 150, 20, 50, 50, GUI._G.Colors['DarkGray4'], text = "2", onClick = lambda: onButtonClick('sceneButton2'))
    sceneButton3: GUI.Button = GUI.Button(3 * (width - 150) // 8 - 150, 20, 50, 50, GUI._G.Colors['DarkGray4'], text = "3", onClick = lambda: onButtonClick('sceneButton3'))
    sceneButton4: GUI.Button = GUI.Button(4 * (width - 150) // 8 - 150, 20, 50, 50, GUI._G.Colors['DarkGray4'], text = "4", onClick = lambda: onButtonClick('sceneButton4'))
    sceneButton5: GUI.Button = GUI.Button(5 * (width - 150) // 8 - 150, 20, 50, 50, GUI._G.Colors['DarkGray4'], text = "5", onClick = lambda: onButtonClick('sceneButton5'))
    sceneButton6: GUI.Button = GUI.Button(6 * (width - 150) // 8 - 150, 20, 50, 50, GUI._G.Colors['DarkGray4'], text = "6", onClick = lambda: onButtonClick('sceneButton6'))
    sceneButton7: GUI.Button = GUI.Button(7 * (width - 150) // 8 - 150, 20, 50, 50, GUI._G.Colors['DarkGray4'], text = "7", onClick = lambda: onButtonClick('sceneButton7'))
    sceneButton8: GUI.Button = GUI.Button(8 * (width - 150) // 8 - 150, 20, 50, 50, GUI._G.Colors['DarkGray4'], text = "8", onClick = lambda: onButtonClick('sceneButton8'))
    pageUpButton: GUI.Button = GUI.Button(8 * (width - 200) // 8, 20, 100, 25, GUI._G.Colors['DarkGray4'], text = "Page Up", onClick = lambda: onButtonClick('pageUp'))
    pageDownButton: GUI.Button = GUI.Button(8 * (width - 200) // 8, 50, 100, 25, GUI._G.Colors['DarkGray4'], text = "Page Down", onClick = lambda: onButtonClick('pageDown'))
    EnterButton = GUI.Button(width // 2 - 150, height // 2 + 100, 200, 25, GUI._G.Colors['DarkGray5'], text = "Enter", onClick = lambda: onButtonClick('enterButton'))

    for button in GUI.buttonList:
        button.bools['enabled'] = True

    selectScene: GUI.Button = GUI.Button(width // 2 - 60, height // 2 - 20, 100, 25, GUI._G.Colors['DarkGray4'], text = "Select A Scene", onClick = lambda: onButtonClick(''))

    saveWin: GUI.Window = GUI.Window(width // 2 - 200, height // 2 - 200, 400, 200, GUI._G.Colors['DarkGray3'], 'saveWin', followScroll = False)
    saveWin.bools['enabled'] = True

    mainBG: GUI.Window = GUI.Window(0, 100, width, height - 100, GUI._G.Colors['DarkGray1'], 'mainBG', isBG = True)
    saveBG: GUI.Window = GUI.Window(0, 100, width, height - 100, GUI._G.Colors['DarkGray1'], 'saveBG', isBG = True)
    sceneList: GUI.Window = GUI.Window(0, 0, width, 100, GUI._G.Colors['DarkGray2'], 'sceneList', isBG = True)
    mainBG.attach(scroll)
    saveBG.attach(saveWin)

    mainBG.bools['enabled'] = True
    sceneList.bools['enabled'] = True

# Function that's ran when a button is clicked
def onButtonClick(buttonName: str):
    global saving, addingFixture

    if buttonName == 'addFixture':
        if addingFixture:
            addingFixture = False
            return
        
        print("Adding Fixture")
        addingFixture = True
        # DMX.fixture.Fixture("Totally legit brand", 1, 4)
    
    elif buttonName == 'saveButton':
        if saving:
            saving = False
            GUI.bgList[0].bools['enabled'] = True
            GUI.bgList[1].bools['enabled'] = False
            return
        
        print("Saving")
        saving = True
        GUI.bgList[0].bools['enabled'] = False
        GUI.bgList[1].bools['enabled'] = True
        
    elif buttonName == 'pageUp' and GUI._G.pageNum != GUI._G.pageLim:
        GUI._G.pageNum += 1
    
    elif buttonName == 'pageDown' and GUI._G.pageNum != 1:    
        GUI._G.pageNum -= 1
    
    elif buttonName == 'enterButton':
        try:
            model = modelInput.value
            channel = int(channelInput.value)
            channelMode = int(channelModeInput.value)

            DMX.fixture.Fixture(model, channel, channelMode)
            addingFixture = False
            modelInput.value = ''
            channelInput.value = ''
            channelModeInput.value = ''
        except:
            print("Please try again")

    elif buttonName == 'sceneButton1':
        if saving:
            save_load.save(1)
            GUI.bgList[0].bools['enabled'] = True
            GUI.bgList[1].bools['enabled'] = False
            saving = False
            return
        
        save_load.load(1 + 8 * (GUI._G.pageNum - 1))
    
    elif buttonName == 'sceneButton2':
        if saving:
            save_load.save(2)
            GUI.bgList[0].bools['enabled'] = True
            GUI.bgList[1].bools['enabled'] = False
            saving = False
            return
        
        save_load.load(2 + 8 * (GUI._G.pageNum - 1))
    
    elif buttonName == 'sceneButton3':
        if saving:
            save_load.save(3)
            GUI.bgList[0].bools['enabled'] = True
            GUI.bgList[1].bools['enabled'] = False
            saving = False
            return
        
        save_load.load(3 + 8 * (GUI._G.pageNum - 1))
    
    elif buttonName == 'sceneButton4':
        if saving:
            save_load.save(4)
            GUI.bgList[0].bools['enabled'] = True
            GUI.bgList[1].bools['enabled'] = False
            saving = False
            return
        
        save_load.load(4 + 8 * (GUI._G.pageNum - 1))
    
    elif buttonName == 'sceneButton5':
        if saving:
            save_load.save(5)
            GUI.bgList[0].bools['enabled'] = True
            GUI.bgList[1].bools['enabled'] = False
            saving = False
            return
        
        save_load.load(5 + 8 * (GUI._G.pageNum - 1))
    
    elif buttonName == 'sceneButton6':
        if saving:
            save_load.save(6)
            GUI.bgList[0].bools['enabled'] = True
            GUI.bgList[1].bools['enabled'] = False
            saving = False
            return
        
        save_load.load(6 + 8 * (GUI._G.pageNum - 1))
    
    elif buttonName == 'sceneButton7':
        if saving:
            save_load.save(7)
            GUI.bgList[0].bools['enabled'] = True
            GUI.bgList[1].bools['enabled'] = False
            saving = False
            return
        
        save_load.load(7 + 8 * (GUI._G.pageNum - 1))
    
    elif buttonName == 'sceneButton8':
        if saving:
            save_load.save(8)
            GUI.bgList[0].bools['enabled'] = True
            GUI.bgList[1].bools['enabled'] = False
            saving = False
            return
        
        save_load.load(8 + 8 * (GUI._G.pageNum - 1))

# Displays everything to the screen
def display(surface: pygame.Surface, events: list[pygame.event.Event], clock: pygame.time.Clock, font: pygame.font.Font) -> None:
    modelInput.update(events)
    channelInput.update(events)
    channelModeInput.update(events)
    
    width = surface.get_width()
    height = surface.get_height()

    # Fill the screen with a color
    surface.fill((255, 255, 255))

    for win in GUI.window.bgList:
        if win.bools['enabled']:
            win.draw(surface, events, scroll)

    for button in GUI.button.buttonList:
        if button.text == 'Select A Scene' and saving:
            button.draw(surface, events, scroll)
        if button.bools['enabled']:
            button.draw(surface, events, scroll)

    for fix in DMX.fixture.fixList:
        model = fix.model
        text = font.render(model, True, pygame.Color('white'))
        surface.blit(text, (fix.x + 15, fix.y + 110 - scroll.verticalOffset))

    if addingFixture:
        pygame.draw.rect(surface, (30, 30, 30), pygame.Rect(width // 2 - 300, height // 2 - 200, 500, 400), border_radius = 15)
        pygame.draw.rect(surface, (42, 42, 42), pygame.Rect(width // 2 - 200, height // 2 - 120, 300, 25))
        pygame.draw.rect(surface, (42, 42, 42), pygame.Rect(width // 2 - 200, height // 2 - 70, 300, 25))
        pygame.draw.rect(surface, (42, 42, 42), pygame.Rect(width // 2 - 200, height // 2 - 20, 300, 25))
        EnterButton.draw(surface, events, scroll)

        surface.blit(modelInput.surface, (width // 2 - 200, height // 2  - 120))
        surface.blit(channelInput.surface, (width // 2 - 200, height // 2  - 70))
        surface.blit(channelModeInput.surface, (width // 2 - 200, height // 2 - 20))

        text = font.render('Enter model name:', True, pygame.Color('white'))
        surface.blit(text, (width // 2 - 200, height // 2 - 140))
        text = font.render('Enter starting channel:', True, pygame.Color('white'))
        surface.blit(text, (width // 2 - 200, height // 2 - 90))
        text = font.render('Enter channel mode:', True, pygame.Color('white'))
        surface.blit(text, (width // 2 - 200, height // 2 - 40))

    if not addingFixture:
        EnterButton.bools['enabled'] = False

    # Shows the FPS to screen (for testing purposes)
    showFPS(surface, clock, font)

    # Update the display
    pygame.display.flip()

# Handles the pygame loop
def pygamewindow(surface: pygame.Surface) -> None:
    # Main loop
    running: bool = True

    # Set up clock
    clock = pygame.time.Clock()

    # Set up font
    font = pygame.font.Font(None, 18)

    while running:
        # Kinda explanatory. It's the width and height of the window in pixels.
        width: int = surface.get_width()
        height: int = surface.get_height()

        # Creates buttons once (don't need hundreds of buttons appearing each second)
        if not GUI._G.bools['elementDebouncer']:
            createElements(width, height)
            GUI._G.flipBool('elementDebouncer')

        if not addingFixture:
            modelInput.focused = False
            channelInput.focused = False
            channelModeInput.focused = False

        # Handles events
        events: list[pygame.event.Event] = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEWHEEL:
                scroll.set_vertical_offset(scroll.verticalOffset - 75 * event.y)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if addingFixture and modelInputRect.collidepoint(pygame.mouse.get_pos()):
                    modelInput.focused = True
                else:
                    modelInput.focused = False
                
                if addingFixture and channelRect.collidepoint(pygame.mouse.get_pos()):
                    channelInput.focused = True
                else:
                    channelInput.focused = False
                
                if addingFixture and channelModeRect.collidepoint(pygame.mouse.get_pos()):
                    channelModeInput.focused = True
                else:
                    channelModeInput.focused = False

        # Handles events where a key is pressed on a keyboard
        keys_pressed: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
        if keys_pressed[pygame.K_ESCAPE]:
            running = False

        # Makes everything seen
        display(surface, events, clock, font)

        dt = clock.tick(60)/1000

    pygame.quit()
    DMX.toDMX.running = False
    sys.exit()

# This is ran to start everything. (called from main.py)
def run() -> None:
    # Initialize Pygame
    pygame.init()

    # Set up the display
    screen: pygame.Surface = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
    pygame.display.set_caption("DMX Controller")

    icon: pygame.Surface = pygame.image.load('DMX-Controller/PlaceHolder.png')
    pygame.display.set_icon(icon)

    pygamewindow(screen)

# For testing purposes
if __name__ == "__main__":
    run()
