import os
import sys
import time
import requests
import shutil
import tempfile
import zipfile
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

def replace_exe(exe_path, updated_exe_path):
    """Replace the original exe with the updated one."""
    try:
        # Wait for the original exe to close
        print("Waiting for the current program to close...")
        time.sleep(5)  # Adjust sleep time as needed

        # Replace the original exe with the updated exe
        print(f"Renaming {updated_exe_path} to {exe_path}")
        if os.path.exists(exe_path):
            os.remove(exe_path)  # Remove the original exe
        os.rename(updated_exe_path, exe_path)  # Rename the updated exe

        print(f"Executable replaced. Restarting the program...")
        subprocess.Popen([exe_path])  # Restart the program with the new exe
        sys.exit()  # Exit the current process

    except Exception as e:
        print(f"Failed to replace executable: {e}")
        sys.exit(1)

if __name__ == "__main__":
    target_dir = sys.argv[1]  # Directory to update
    exe_path = os.path.join(target_dir, "DMX Controller.exe")  # The current exe path
    dist_folder = os.path.join(target_dir, "dist")
    updated_exe_path = os.path.join(dist_folder, "DMX Controller.exe")

    print("Starting update process...")
    update_applied = download_github_repo_as_zip("https://github.com/TheIronCollector/DMX-Controller", target_dir)

    if update_applied:
        print("Update applied. Replacing executable...")
        replace_exe(exe_path, updated_exe_path)
    else:
        print("No update was needed.")
