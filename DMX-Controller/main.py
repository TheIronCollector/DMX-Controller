import os
import sys
import time
import subprocess
import threading
import toDMX
import Program
import update_script  # Import the update script

def DMX_Thread():
    try:
        toDMX.run()
    except Exception as e:
        print(f"Error in DMX thread: {e}")

if __name__ == "__main__":
    is_exe = False
    cur_dir = os.getcwd()
    exe_path = sys.argv[0]  # Path to the running executable

    # Path to the update flag file
    update_flag_path = os.path.join(cur_dir, "update_flag.txt")

    # Check if the update flag exists
    if os.path.exists(update_flag_path):
        print("Update already applied. Skipping update process.")
    else:
        # If flag doesn't exist, proceed with the update
        with open(update_flag_path, "w") as f:
            f.write("update_triggered")  # Mark the update as triggered

        print("Checking for updates...")

        # Run the update script in a separate process
        update_process = subprocess.Popen([sys.executable, "update_script.py", cur_dir])

        # Continue running the DMX thread and main program
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
