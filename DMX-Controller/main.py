import os
import sys
import subprocess
import threading
import platform
import shutil

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

def update_from_github():
    repo_url = "https://github.com/TheIronCollector/DMX-Controller.git"
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    grandparent_dir = os.path.dirname(parent_dir)
    temp_dir = os.path.join(grandparent_dir, 'temp_update')
    script_name = os.path.basename(__file__)
    
    print(f"Updating from GitHub: {repo_url}")
    print(f"Current directory: {current_dir}")
    print(f"Parent directory to be updated: {parent_dir}")
    
    try:
        # Clone the repository to a temporary directory
        print("Cloning the latest version to a temporary directory...")
        subprocess.run(["git", "clone", repo_url, temp_dir], check=True)
        
        # Copy the update script to the temp directory
        shutil.copy2(__file__, os.path.join(temp_dir, script_name))
        
        # Remove the parent directory
        shutil.rmtree(parent_dir)
        
        # Rename the temp directory to the original parent directory name
        os.rename(temp_dir, parent_dir)
        
        print("Update completed successfully.")
        
        # Restart the script
        print("Restarting the script with the updated version...")
        new_script_path = os.path.join(parent_dir, script_name)
        os.execv(sys.executable, ['python'] + [new_script_path] + sys.argv[1:])
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during the update process: {e}")
        print("Continuing with the existing version of the program.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print("Continuing with the existing version of the program.")
    finally:
        # Clean up: remove the temporary directory if it still exists
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

def DMX_Thread():
    toDMX.run()

if __name__ == "__main__":
    if check_internet():
        update_from_github()
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