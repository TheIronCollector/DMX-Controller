# List of colors
Colors = {
    'Blue': (0, 0, 255),
    'Brown': (165, 42, 42),
    'Cyan': (0, 255, 255),
    'DarkGray1': (18, 18, 18),
    'DarkGray2': (24, 24, 24),
    'DarkGray3': (30, 30, 30),
    'DarkGray4': (36, 36, 36),
    'DarkGray5': (42, 42, 42),
    'DarkGray6': (48, 48, 48),
    'DarkGray7': (54, 54, 54),
    'DarkGray8': (60, 60, 60),
    'DarkGray9': (66, 66, 66),
    'DarkGray10': (72, 72, 72),
    'Green': (0, 255, 0),
    'LightGray': (200, 200, 200),
    'LightRed': (255, 102, 102),
    'Magenta': (255, 0, 255),
    'Orange': (255, 165, 0),
    'Pink': (255, 192, 203),
    'Purple': (128, 0, 128),
    'Red': (255, 0, 0),
    'White': (255, 255, 255),
    'Yellow': (255, 255, 0)
}

# List of bools
bools: dict = {
    'elementDebouncer': False,
    'newWindowOrder': False,
    'n': False,
    's': False,
    'e': False,
    'w': False
}

pageNum: int = 1
pageLim: int = 125

# Flips a bool from True to False or from False to True
def flipBool(bool: str):
    global bools
    bools[bool] = not bools[bool]