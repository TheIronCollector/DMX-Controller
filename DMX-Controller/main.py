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
        
        # Copy the update script to the temp directory
        shutil.copy2(__file__, os.path.join(temp_update_dir, script_name))
        
        # Optionally, perform any additional steps needed to update your project files
        
        print("Update completed successfully.")
        
        # Restart the script
        print("Restarting the script with the updated version...")
        new_script_path = os.path.join(temp_update_dir, script_name)
        os.execv(sys.executable, ['python'] + [new_script_path] + sys.argv[1:])
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
        Program.run()
    except Exception as e:
        print(f"An error occurred in the main program: {e}")
    finally:
        print("Waiting for DMX thread to finish...")
        thread.join()
        print("Exiting the program.")
        sys.exit()
