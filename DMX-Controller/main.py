import os
import sys
import subprocess
import threading

import Features.DMX.toDMX as toDMX
import Program

def check_internet():
    try:
        subprocess.check_call(["ping", "-c", "1", "google.com"], 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.DEVNULL)
        print("Internet connection is available.")
        return True
    except subprocess.CalledProcessError:
        print("No internet connection detected.")
        return False

def update_from_github():
    repo_url = "https://github.com/TheIronCollector/DMX_Controller.git"
    local_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Updating from GitHub: {repo_url}")
    print(f"Local directory: {local_dir}")
    
    if not os.path.exists(os.path.join(local_dir, '.git')):
        print("Git repository not found. Cloning...")
        subprocess.run(["git", "clone", repo_url, local_dir], check=True)
    else:
        print("Git repository found. Checking for updates...")
        os.chdir(local_dir)
        subprocess.run(["git", "fetch", "origin"], check=True)
        
        local_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()
        remote_hash = subprocess.check_output(["git", "rev-parse", "@{u}"]).strip()
        
        if local_hash != remote_hash:
            print("Updates available. Pulling changes...")
            subprocess.run(["git", "pull", "origin", "main"], check=True)
            print("Update completed successfully.")
        else:
            print("Local repository is up to date. No changes to pull.")

def DMX_Thread():
    toDMX.run()

if __name__ == "__main__":
    if check_internet():
        try:
            update_from_github()
        except subprocess.CalledProcessError as e:
            print(f"An error occurred during the update process: {e}")
            print("Continuing with the existing version of the program.")
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