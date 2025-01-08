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
            updated = False
            for item in os.listdir(extracted_dir):
                s = os.path.join(extracted_dir, item)
                d = os.path.join(target_dir, item)

                # Replace only if there is a difference
                if os.path.exists(d):
                    if os.path.isdir(d):
                        if not are_directories_identical(s, d):
                            shutil.rmtree(d)
                            shutil.move(s, d)
                            updated = True
                    else:
                        if not file_is_identical(s, d):
                            os.remove(d)
                            shutil.move(s, d)
                            updated = True
                else:
                    shutil.move(s, d)
                    updated = True

        # Clean up the temporary ZIP file
        os.remove(temp_zip_path)
        print("Update completed successfully.")
        return updated
    except Exception as e:
        print(f"An error occurred while downloading or extracting the repository: {e}")
        return False

def file_is_identical(file1, file2):
    """Check if two files are identical."""
    return os.path.exists(file2) and os.path.getsize(file1) == os.path.getsize(file2)

def are_directories_identical(dir1, dir2):
    """Check if two directories are identical."""
    if not os.path.exists(dir2):
        return False
    for root, dirs, files in os.walk(dir1):
        for name in files:
            file1 = os.path.join(root, name)
            file2 = os.path.join(dir2, os.path.relpath(file1, dir1))
            if not file_is_identical(file1, file2):
                return False
    return True

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
        update_applied = download_github_repo_as_zip("https://github.com/TheIronCollector/DMX-Controller", target_dir)

        # Restart only if the update was applied
        if update_applied:
            print("Update applied. Restarting the program...")
            restart_with_update(exe_path)
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
