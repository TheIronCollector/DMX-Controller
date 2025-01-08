import os
import sys
import time
import requests
import shutil
import tempfile
import zipfile
import threading
import toDMX
import Program
import subprocess

def download_github_repo_as_zip(github_url, target_dir):
    try:
        # Construct the URL for the ZIP file
        repo_name = github_url.rstrip('/').split('/')[-1]
        zip_url = f"{github_url}/archive/refs/heads/main.zip"
        
        # Download the ZIP file
        print(f"Downloading repository from {zip_url}...")
        response = requests.get(zip_url, stream=True)
        response.raise_for_status()

        # Create a temporary file for the ZIP
        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_zip:
            temp_zip.write(response.content)
            temp_zip_path = temp_zip.name

        # Extract the ZIP file
        with tempfile.TemporaryDirectory() as temp_extract_dir:
            print(f"Extracting {temp_zip_path} to {temp_extract_dir}...")
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_extract_dir)

            # Move the contents of the extracted folder to the target directory
            extracted_dir = os.path.join(temp_extract_dir, os.listdir(temp_extract_dir)[0])
            print(f"Moving contents from {extracted_dir} to {target_dir}...")
            for item in os.listdir(extracted_dir):
                s = os.path.join(extracted_dir, item)
                d = os.path.join(target_dir, item)
                if os.path.exists(d):
                    if os.path.isdir(d):
                        shutil.rmtree(d)
                    else:
                        os.remove(d)
                shutil.move(s, d)

        # Clean up the temporary ZIP file
        os.remove(temp_zip_path)
        print("Update completed successfully.")
        return True
    except Exception as e:
        print(f"An error occurred while downloading or extracting the repository: {e}")
        return False

def restart_with_update(exe_path, updated_exe_path):
    """Handle renaming and restarting the program after the update."""
    try:
        # Create a temporary name for the updated executable
        temp_exe_path = exe_path + ".tmp"

        # Rename the updated executable to the temporary name
        print(f"Renaming updated executable: {updated_exe_path} -> {temp_exe_path}")
        os.rename(updated_exe_path, temp_exe_path)

        # Restart the program with the new executable
        print(f"Restarting program with the updated executable: {temp_exe_path}")
        subprocess.Popen([temp_exe_path])

        # Wait a bit to ensure the original program exits
        time.sleep(2)

        # Now that the original program has closed, delete the original executable
        print(f"Removing original executable: {exe_path}")
        os.remove(exe_path)

        # Rename the temporary executable to the original executable name
        print(f"Renaming temporary executable: {temp_exe_path} -> {exe_path}")
        os.rename(temp_exe_path, exe_path)

        # Exit the current process to complete the update
        sys.exit()
    except Exception as e:
        print(f"Failed to restart with update: {e}")
        sys.exit(1)

def DMX_Thread():
    try:
        toDMX.run()
    except Exception as e:
        print(f"Error in DMX thread: {e}")

if __name__ == "__main__":
    is_exe = False
    cur_dir = os.getcwd()
    exe_path = sys.argv[0]  # Path to the running executable

    # Determine if running from an EXE
    for item in os.listdir(cur_dir):
        if item.endswith('.exe'):
            target_dir = os.path.dirname(cur_dir)
            is_exe = True
            print("Program was run with an exe")
            break
    else:
        target_dir = cur_dir

    print(f"Current directory: {cur_dir}")

    try:
        if not is_exe:
            raise ValueError("Not an exe. Won't update.")

        print("Checking for updates...")
        update_applied = download_github_repo_as_zip("https://github.com/TheIronCollector/DMX-Controller", target_dir)

        # If the update was applied, handle the executable replacement
        if update_applied:
            print("Update applied. Preparing to restart with the updated executable...")
            updated_exe_path = exe_path.replace(".exe", " Updated.exe")

            # Check for the updated executable
            if os.path.exists(updated_exe_path):
                restart_with_update(exe_path, updated_exe_path)
            else:
                print(f"Updated executable not found: {updated_exe_path}")
        else:
            print("No update was needed.")

    except Exception as e:
        print(f"Error during update process: {e}")

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
