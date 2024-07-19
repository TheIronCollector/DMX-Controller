from threading import Thread
import sys
import os
import requests
import zipfile
import shutil

import Features.DMX.toDMX as toDMX
import Program

def get_latest_release(repo_owner, repo_name):
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def download_and_extract_release(repo_owner, repo_name, download_path):
    latest_release = get_latest_release(repo_owner, repo_name)
    zip_url = latest_release['zipball_url']
    release_tag = latest_release['tag_name']
    
    local_zip_path = os.path.join(download_path, f"{repo_name}-{release_tag}.zip")

    with requests.get(zip_url, stream=True) as r:
        r.raise_for_status()
        with open(local_zip_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    
    extract_path = os.path.join(download_path, f"{repo_name}-{release_tag}")
    with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    
    return extract_path, local_zip_path, release_tag

def update_project(repo_owner, repo_name, current_path, download_path):
    new_version_path, local_zip_path, release_tag = download_and_extract_release(repo_owner, repo_name, download_path)
    update_occurred = False

    # Remove old files
    for item in os.listdir(current_path):
        item_path = os.path.join(current_path, item)
        if item_path != download_path:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
                update_occurred = True
            else:
                os.remove(item_path)
                update_occurred = True
    
    # Move new files to the current path
    for item in os.listdir(new_version_path):
        s = os.path.join(new_version_path, item)
        d = os.path.join(current_path, item)
        if os.path.isdir(s):
            shutil.move(s, d)
            update_occurred = True
        else:
            shutil.move(s, current_path)
            update_occurred = True
    
    # Clean up
    shutil.rmtree(new_version_path)
    os.remove(local_zip_path)

    return update_occurred

def DMX_Thread():
    toDMX.run()

if __name__ == "__main__":
    repo_owner = "TheIronCollector"
    repo_name = "DMX-Controller"
    
    current_project_path = os.path.abspath(".")
    download_path = os.path.join(current_project_path, "downloads")
    
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    
    update_occurred = update_project(repo_owner, repo_name, current_project_path, download_path)
    if update_occurred:
        print("Project has been updated.")
    else:
        print("No updates were found.")

    thread = Thread(target=DMX_Thread)
    thread.start()
    Program.run()
    thread.join()
    sys.exit()
