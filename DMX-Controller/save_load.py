import Features
import logging
import ast
import os
import platform
from pathlib import Path

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

def save(sceneNum: int, filename: str = "saves.txt") -> None:
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

    Features.fixture.save()
    data = Features.fixture.data.copy()
    Features.fixture.data = []
    
    data.insert(0, sceneNum)

    with open(file_path, 'a') as file:
        file.write(str(data) + "\n")

    data.clear()
    Features.fixture.data.clear()
    Features.fixture.fixList.clear()

def load(sceneNum: int, filename: str = "saves.txt") -> None:
    file_path = get_save_file_path(filename)

    # Clear existing fixtures
    attachments = Features.GUI.window.bgList[0].attachments
    for attachment in attachments[:]:
        if type(attachment) == Features.GUI.Window and attachment.bools['isFixture']:
            attachments.remove(attachment)
            del attachment

    Features.fixture.fixList.clear()
    Features.DMX.fixture.data.clear()
    Features.DMX.fixture.channelsList = [False] * 512
    Features.DMX.toDMX.dmx_data = [0] * 512

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
                brand, channel, channel_mode, channel_values = fixture_data
                new_fixture = Features.DMX.fixture.Fixture(brand, channel, channel_mode)
                for i in range(channel_mode):
                    Features.DMX.toDMX.dmx_data[channel - 1 + i] = channel_values[i]

    Features.fixture.data = []

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
