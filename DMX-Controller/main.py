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

            # Locate the extracted folder
            extracted_dir = os.path.join(temp_extract_dir, os.listdir(temp_extract_dir)[0])
            print(f"Extracted to {extracted_dir}")

            # Check for the updated exe inside the zip
            updated_exe_name = "DMX Controller.exe"  # Update with your exe's name if necessary
            updated_exe_path = os.path.join(extracted_dir, updated_exe_name)

            if os.path.exists(updated_exe_path):
                print(f"Found updated executable: {updated_exe_path}")
                # Move the updated exe to the dist folder (without replacing the original)
                dist_folder = os.path.join(target_dir, "dist")
                os.makedirs(dist_folder, exist_ok=True)
                shutil.move(updated_exe_path, os.path.join(dist_folder, updated_exe_name))
                print(f"Updated executable moved to: {os.path.join(dist_folder, updated_exe_name)}")

            # Move the rest of the contents (non-exe files) to the target directory
            print(f"Moving other files to {target_dir}...")
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
        # Wait for the current program to close (use a simple timeout here or other methods)
        print("Waiting for the current program to close before replacing the exe...")
        time.sleep(5)  # Adjust this to an appropriate wait time if needed
        
        # Rename and replace the original exe with the updated exe
        print(f"Renaming and replacing the executable: {updated_exe_path} -> {exe_path}")
        if os.path.exists(exe_path):
            os.remove(exe_path)  # Remove the original exe
        os.rename(updated_exe_path, exe_path)  # Rename the updated exe to the original exe name

        print(f"Restarting the program with the updated executable...")
        subprocess.Popen([exe_path])  # Restart the program with the new exe
        sys.exit()  # Exit the current process

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
            dist_folder = os.path.join(target_dir, "dist")
            updated_exe_path = os.path.join(dist_folder, "DMX Controller.exe")

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
