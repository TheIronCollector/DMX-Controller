import os
import sys
import subprocess
import threading
import time
import platform
import errno
import shutil
import stat

import Features.DMX.toDMX as toDMX
import Program

def check_internet():
    try:
        subprocess.check_call(["ping", "-c" if platform.system().lower() != "windows" else "-n", "1", "google.com"], 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.DEVNULL)
        print("Internet connection is available.")
        return True
    except subprocess.CalledProcessError:
        print("No internet connection detected.")
        return False

def handle_remove_readonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0777
        func(path)
    else:
        raise

def remove_directory(dir_path):
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            shutil.rmtree(dir_path, onerror=handle_remove_readonly)
            break
        except PermissionError:
            if attempt < max_attempts - 1:
                print(f"Permission error, retrying in 2 seconds... (Attempt {attempt + 1}/{max_attempts})")
                time.sleep(2)
            else:
                raise

def replace_with_github_clone(target_dir, github_url):
    if not os.path.exists(target_dir):
        raise ValueError(f"The target directory {target_dir} does not exist.")

    temp_dir = target_dir + "_temp"
    
    try:
        # Remove the temporary directory if it already exists
        if os.path.exists(temp_dir):
            remove_directory(temp_dir)

        # Clone the repository to the temporary directory
        subprocess.run(["git", "clone", github_url, temp_dir], check=True)

        # Remove the original directory
        print("Removing original directory")
        remove_directory(target_dir)

        # Rename the cloned directory to the target directory name
        print("Renaming temp directory to original's name")
        os.rename(temp_dir, target_dir)

        print(f"Successfully replaced {target_dir} with the cloned repository.")
    except subprocess.CalledProcessError as e:
        print(f"Error cloning repository: {e}")
        if os.path.exists(temp_dir):
            remove_directory(temp_dir)
    except Exception as e:
        print(f"An error occurred: {e}")
        if os.path.exists(temp_dir):
            remove_directory(temp_dir)

def DMX_Thread():
    toDMX.run()

if __name__ == "__main__":
    cur_dir = os.getcwd()
    parent_dir = os.path.dirname(cur_dir)

    print(f'Current directory: {cur_dir}')
    print(f'Parent directory: {parent_dir}')

    try:
        if check_internet():
            replace_with_github_clone(cur_dir, "https://github.com/TheIronCollector/DMX-Controller.git")
        else:
            print("Skipping update check due to no internet connection.")
    except Exception as e:
        print(e)

    print("Starting DMX thread and main program...")
    thread = threading.Thread(target=DMX_Thread)
    thread.start()
    
    try:
        print("Running program")
        Program.run()
    except Exception as e:
        print(f"An error occurred in the main program: {e}")
    finally:
        print("Waiting for DMX thread to finish...")
        thread.join()
        print("Exiting the program.")
        sys.exit()
