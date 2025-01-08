import os
import sys
import time
import subprocess
import threading
import toDMX
import Program

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

        # Run the update script in a separate process
        update_process = subprocess.Popen([sys.executable, "update_script.py", target_dir])

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

    except Exception as e:
        print(f"Error during update process: {e}")
