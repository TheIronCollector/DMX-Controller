import os
import sys
import subprocess
import threading
import platform
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

def ensure_git_installed():
    try:
        # Check if Git is already installed
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("Git is already installed.")
    except FileNotFoundError:
        print("Git is not installed. Attempting to install...")
        if sys.platform.startswith('win'):
            try:
                # Attempt to install Git using winget
                subprocess.run(["winget", "install", "--id", "Git.Git", "-e", "--source", "winget"], check=True)
                print("Git has been successfully installed.")
            except subprocess.CalledProcessError as e:
                print(f"Failed to install Git: {e}")
                print("Please install Git manually from https://git-scm.com/downloads")
        else:
            print("Automatic Git installation is only supported on Windows.")
            print("Please install Git manually from https://git-scm.com/downloads")

def force_remove_readonly(func, path, exc_info):
    # Change the file from read-only and try removing it again
    os.chmod(path, stat.S_IWRITE)
    func(path)

def is_update_available():
    try:
        repo_url = "https://github.com/TheIronCollector/DMX-Controller.git"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        
        # Fetch the latest changes from the remote repository
        subprocess.run(["git", "fetch", repo_url], cwd=parent_dir, check=True)
        
        # Check if the local repository is behind the remote repository
        local_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=parent_dir).strip()
        remote_commit = subprocess.check_output(["git", "rev-parse", "origin/main"], cwd=parent_dir).strip()
        
        return local_commit != remote_commit
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while checking for updates: {e}")
        return False

def update_from_github():
    if not shutil.which('git') or not os.path.isdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.git')):
        print("Git repository not available. Please download the latest version manually.")
        print("Visit: https://github.com/TheIronCollector/DMX-Controller/releases")
        return False
    
    repo_url = "https://github.com/TheIronCollector/DMX-Controller.git"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    grandparent_dir = os.path.dirname(parent_dir)
    temp_update_dir = os.path.join(grandparent_dir, 'temp_update')
    script_name = os.path.basename(__file__)
    
    print(f"Updating from GitHub: {repo_url}")
    print(f"Current directory: {current_dir}")
    print(f"Parent directory to be updated: {parent_dir}")

    try:
        # Ensure any previous temp update directory is removed
        if os.path.exists(temp_update_dir):
            print("Removing existing temporary update directory...")
            shutil.rmtree(temp_update_dir, onerror=force_remove_readonly)
        
        # Clone the repository to the temporary update directory
        print("Cloning the latest version to a temporary update directory...")
        subprocess.run(["git", "clone", repo_url, temp_update_dir], check=True)
        
        # Copy the entire contents of temp_update_dir to parent_dir
        print("Copying updated files to the main directory...")
        for item in os.listdir(temp_update_dir):
            s = os.path.join(temp_update_dir, item)
            d = os.path.join(parent_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        
        print("Update completed successfully.")
        
        # Restart the script from the original location
        print("Restarting the script with the updated version...")
        os.execv(sys.executable, ['python'] + [os.path.join(parent_dir, script_name)] + sys.argv[1:])
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during the update process: {e}")
        print("Continuing with the existing version of the program.")
    except PermissionError as e:
        print(f"A permission error occurred: {e}")
        print("Ensure the script is run with the necessary permissions.")
        print("Continuing with the existing version of the program.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print("Continuing with the existing version of the program.")
    finally:
        # Clean up: remove the temporary update directory if it still exists
        if os.path.exists(temp_update_dir):
            try:
                shutil.rmtree(temp_update_dir, onerror=force_remove_readonly)
            except PermissionError as e:
                print(f"Failed to remove temporary update directory: {e}")

def DMX_Thread():
    toDMX.run()

if __name__ == "__main__":
    if check_internet():
        ensure_git_installed()
        if is_update_available():
            update_from_github()
        else:
            print("No updates available. Continuing with the existing version.")
    else:
        print("Skipping update check due to no internet connection.")
    
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
