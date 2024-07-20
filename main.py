import os
import requests
from threading import Thread
import sys
import subprocess

import Features.DMX.toDMX as toDMX
import Program

def check_for_updates(repo_url):
    try:
        response = requests.get(f"{repo_url}/commits/main")
        if response.status_code == 200:
            latest_commit = response.json()['sha']
            with open('last_commit.txt', 'r') as f:
                current_commit = f.read().strip()
            if latest_commit != current_commit:
                return True
    except Exception as e:
        print(f"Error checking for updates: {e}")
    return False

def update_program(repo_url):
    try:
        subprocess.run(["git", "pull", repo_url], check=True)
        latest_commit = subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()
        with open('last_commit.txt', 'w') as f:
            f.write(latest_commit)
        print("Program updated successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error updating program: {e}")
        return False

def DMX_Thread():
    toDMX.run()

if __name__ == "__main__":
    repo_url = "https://github.com/TheIronCollector/DMX-Controller"
    
    if check_for_updates(repo_url):
        print("Update available. Updating program...")
        if update_program(repo_url):
            print("Restarting program with updates...")
            os.execv(sys.executable, ['python'] + sys.argv)
        else:
            print("Failed to update. Continuing with current version.")
    
    thread = Thread(target=DMX_Thread)
    thread.start()
    Program.run()
    thread.join()
    sys.exit()