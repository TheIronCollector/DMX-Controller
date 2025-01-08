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

def download_github_repo_as_zip(github_url, target_dir):
    try:
        # Construct the URL for the ZIP file
        repo_name = github_url.rstrip('/').split('/')[-1]
        zip_url = f"{github_url}/archive/refs/heads/main.zip"
        
        # Download the ZIP file
        print(f"Downloading repository from {zip_url}...")
        response = requests.get(zip_url, stream=True)
        response.raise_for_status()  # Raise an error for bad HTTP responses

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

                # Always replace files, including the running executable
                if os.path.exists(d):
                    if os.path.isdir(d):
                        shutil.rmtree(d)
                    else:
                        os.remove(d)
                shutil.move(s, d)

        # Clean up the temporary ZIP file
        os.remove(temp_zip_path)
        print("Update completed successfully.")
    except Exception as e:
        print(f"An error occurred while downloading or extracting the repository: {e}")

def create_updater_script(exe_path, temp_dir):
    updater_script = os.path.join(temp_dir, "updater.bat")
    with open(updater_script, "w") as script:
        script.write(f"""@echo off
timeout /t 2 > nul
move /y "{exe_path}.new" "{exe_path}" > nul
start "" "{exe_path}"
del "%~f0" > nul
""")
    return updater_script

def restart_with_update(exe_path):
    # Rename the current executable to allow replacement
    new_exe_path = f"{exe_path}.new"
    os.rename(exe_path, new_exe_path)

    # Create an updater script
    temp_dir = tempfile.gettempdir()
    updater_script = create_updater_script(exe_path, temp_dir)

    # Start the updater script and exit the current program
    os.system(f'start /b cmd /c "{updater_script}"')
    sys.exit()

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
        download_github_repo_as_zip("https://github.com/TheIronCollector/DMX-Controller", target_dir)

        # Restart if the executable was updated
        restart_with_update(exe_path)

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
