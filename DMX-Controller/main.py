import os
import sys
import subprocess
import threading
import platform
import requests
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
    current_version = "v1.0.0"  # Replace this with your actual current version
    repo_owner = "TheIronCollector"
    repo_name = "DMX-Controller"
    
    print(f"Current version: {current_version}")
    print("Checking for updates...")

    # First, try to check for updates using the GitHub API
    try:
        api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        response = requests.get(api_url)
        response.raise_for_status()
        latest_version = response.json()['tag_name']
        
        print(f"Latest version on GitHub: {latest_version}")
        return latest_version != current_version

    except requests.RequestException as e:
        print(f"Failed to check for updates via GitHub API: {e}")
    
    # If API check fails, fall back to Git method (mainly for development environments)
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        git_dir = os.path.join(current_dir, '.git')
        
        if not os.path.isdir(git_dir):
            print(f"Not a git repository. Git directory not found at {git_dir}")
            return False
        
        print("Checking for updates using Git...")
        
        # Fetch the latest changes from the remote repository
        fetch_result = subprocess.run(
            ["git", "fetch", "origin", "main"], 
            cwd=current_dir, 
            capture_output=True, 
            text=True
        )
        if fetch_result.returncode != 0:
            print(f"Git fetch failed: {fetch_result.stderr}")
            return False
        
        # Get the latest commit hash from the remote main branch
        remote_commit = subprocess.check_output(
            ["git", "rev-parse", "origin/main"], 
            cwd=current_dir
        ).strip().decode()
        
        # Get the current commit hash
        local_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], 
            cwd=current_dir
        ).strip().decode()
        
        print(f"Local commit: {local_commit}")
        print(f"Remote commit: {remote_commit}")
        
        return local_commit != remote_commit

    except subprocess.CalledProcessError as e:
        print(f"Git operation failed: {e}")
    except FileNotFoundError:
        print("Git command not found. Make sure Git is installed and in your PATH.")
    
    # If both methods fail, assume no update is available
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
