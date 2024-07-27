import os
import sys
import subprocess
import threading
import time
import platform
import errno
import shutil
import stat
import tempfile

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

def copy_contents(src, dst, exclude=None):
    if exclude is None:
        exclude = ['.git']
    for item in os.listdir(src):
        if item in exclude:
            continue
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            if os.path.exists(d):
                shutil.rmtree(d)
            shutil.copytree(s, d)
        else:
            if os.path.exists(d):
                os.remove(d)
            shutil.copy2(s, d)

def update_directory_with_github_clone(target_dir, github_url):
    if not os.path.exists(target_dir):
        raise ValueError(f"The target directory {target_dir} does not exist.")

    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Clone the repository to the temporary directory
            subprocess.run(["git", "clone", github_url, temp_dir], check=True)

            # Remove .git directory from target if it exists
            target_git_dir = os.path.join(target_dir, '.git')
            if os.path.exists(target_git_dir):
                shutil.rmtree(target_git_dir)

            # Copy contents from temp directory to target directory, excluding .git
            copy_contents(temp_dir, target_dir)

            print(f"Successfully updated {target_dir} with the contents of the cloned repository.")
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

def DMX_Thread():
    toDMX.run()

if __name__ == "__main__":
    cur_dir = os.getcwd()
    parent_dir = os.path.dirname(cur_dir)

    print(f'Current directory: {cur_dir}')
    print(f'Parent directory: {parent_dir}')

    try:
        if check_internet():
            update_directory_with_github_clone(cur_dir, "https://github.com/TheIronCollector/DMX-Controller.git")
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
