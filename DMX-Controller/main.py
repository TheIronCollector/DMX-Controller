import os
import platform
import psutil
import shutil
import signal
import subprocess
import sys
import tempfile
import threading

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

def move_contents(src, dst):
    for item in os.listdir(src):
        if item == '.git':
            continue
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.exists(d):
            if os.path.isdir(d):
                shutil.rmtree(d)
            else:
                os.remove(d)
        shutil.move(s, d)

def is_update_available(repo_path: str) -> bool:
    """
    Check if an update is available for the Git repository at the given path.
    
    :param repo_path: The local path to the Git repository.
    :return: True if an update is available, False otherwise.
    """
    try:
        # Fetch the latest changes from the remote
        subprocess.run(['git', '-C', repo_path, 'fetch'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Get the latest commit hash on the remote repository
        remote_commit = subprocess.check_output(
            ['git', '-C', repo_path, 'rev-parse', 'origin/main']
        ).strip().decode('utf-8')
        
        # Get the current commit hash of the local repository
        local_commit = subprocess.check_output(
            ['git', '-C', repo_path, 'rev-parse', 'HEAD']
        ).strip().decode('utf-8')
        
        # Compare the commit hashes
        return remote_commit != local_commit
    
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while checking for updates: {e}")
        return False

def update_directory_with_github_clone(target_dir, github_url):
    if not os.path.exists(target_dir):
        raise ValueError(f"The target directory {target_dir} does not exist.")

    # Create a temporary directory for cloning
    with tempfile.TemporaryDirectory() as temp_parent_dir:
        try:
            # Clone the repository to a new directory inside the temp directory
            repo_name = os.path.splitext(os.path.basename(github_url))[0]
            clone_dir = os.path.join(temp_parent_dir, repo_name)

            print("Cloning GitHub directory")
            subprocess.run(["git", "clone", github_url, clone_dir], check=True)

            # Move contents from cloned directory to target directory
            print("Moving contents to main directory")
            move_contents(clone_dir, target_dir)

            print(f"Successfully updated {target_dir} with the contents of the cloned repository.")
        except subprocess.CalledProcessError as e:
            print(f"Error cloning repository: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

def DMX_Thread():
    toDMX.run()

if __name__ == "__main__":
    is_exe = False
    cur_dir = os.getcwd()

    # Making sure the directory is the right one and not the dist folder (contains an exe)
    for item in os.listdir(cur_dir):
        if item.endswith('.exe'):
            target_dir = os.path.dirname(cur_dir)
            is_exe = True
            print("Program was run with an exe")
            break
    else:
        target_dir = cur_dir

    print(f'Current directory: {cur_dir}')

    try:
        if not is_exe:
            raise ValueError("Not an exe. Won't update.")

        if check_internet():
            if is_update_available(target_dir):
                print("Update is available. Updating...")
                update_directory_with_github_clone(target_dir, "https://github.com/TheIronCollector/DMX-Controller.git")
            else:
                print("No updates available.")
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
