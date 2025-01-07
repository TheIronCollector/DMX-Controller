import customWidgets.fixture
import toDMX
import logging
import ast
import os
import platform
from pathlib import Path
import customWidgets

def get_user_data_dir(app_name: str) -> Path:
    if platform.system() == "Windows":
        base_dir = Path(os.getenv('LOCALAPPDATA'))
    else:
        base_dir = Path.home() / ".local" / "share"
    
    user_data_dir = base_dir / app_name
    user_data_dir.mkdir(parents=True, exist_ok=True)
    
    return user_data_dir

def get_save_file_path(filename: str) -> Path:
    user_data_dir = get_user_data_dir("DMX Controller")
    return user_data_dir / filename

def save(sceneNum: int, window, filename: str = "saves.txt") -> None:
    file_path = get_save_file_path(filename)
    data_index = -1
    
    if file_path.exists():
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for i in range(len(lines)):
                line = ast.literal_eval(lines[i].strip())
                if line[0] == sceneNum:
                    data_index = i
                    logging.info(f'{sceneNum} already has data. Overwriting data!')
                    break
    
    if data_index != -1:
        delete_line(data_index, file_path)

    customWidgets.fixture.save()
    data = customWidgets.fixture.data.copy()
    customWidgets.fixture.data.clear()
    
    data.insert(0, sceneNum)

    with open(file_path, 'a') as file:
        file.write(str(data) + "\n")

    data.clear()

def load(sceneNum: int, window, filename: str = "saves.txt") -> None:
    file_path = get_save_file_path(filename)

    for fixture in customWidgets.fixture.fixtureList:
        window.MainWidget.remove_widget(fixture)

    customWidgets.fixture.fixtureList.clear()
    customWidgets.fixture.data.clear()
    customWidgets.fixture.channelList = [False] * 512
    toDMX.dmx_data = [0] * 512

    if file_path.exists():
        with open(file_path, 'r') as file:
            lines = file.readlines()
            data = -1
            for i in range(len(lines)):
                line = ast.literal_eval(lines[i].strip())
                if line[0] == sceneNum:
                    data = line
                    break
        
            if data == -1:
                logging.info(f"Scene {sceneNum} is empty. Defaulting all channels to 0.")
                return
            
            for fixture_data in data[1:]:
                name, channel, channel_mode, channel_values = fixture_data
                window.add_fixture(name, channel, channel_mode, True)
                for i in range(channel_mode):
                    toDMX.dmx_data[channel - 1 + i] = channel_values[i]
            
            for fixture in customWidgets.fixture.fixtureList:
                for i in range(len(fixture.sliders)):
                    channel = int(fixture.channel_labels[i].text())
                    fixture.sliders[i].setValue(toDMX.dmx_data[channel - 1])

def delete_line(line_index: int, file_path: Path):
    print(f"Deleting line {line_index + 1}")

    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    # Check if the line index is within the valid range
    if 0 <= line_index < len(lines):
        del lines[line_index]  # Remove the specified line

        # Write the updated lines back to the file
        with open(file_path, 'w') as file:
            file.writelines(lines)
    else:
        print(f"Line index {line_index} is out of range. No line deleted.")
    
def main():
    print('ok')

if __name__ == '__main__':
    main()
