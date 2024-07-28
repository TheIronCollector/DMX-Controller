import serial
import time
import serial.tools.list_ports
import array
import logging
import sys

running: bool = True

# DMX data
dmx_data = array.array('B', [0] * 512)

# Vendor and Product ID's used to identity DMX interfaces
DSD_TECH_VID = 1027
DSD_TECH_PID = 24577

# Timing constants
FRAME_TIME = 1 / 120  # Approx. 8.3 ms between frames (120 Hz)
BREAK_TIME = 0.005    # 5 ms break time
MAB_TIME = 0.000012   # 12 microseconds for Mark After Break

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_dmx_interface() -> str | None:
    for port in serial.tools.list_ports.comports():
        if port.vid == DSD_TECH_VID and port.pid == DSD_TECH_PID:
            return port.device
    return None

def send_dmx_signal(ser: serial.Serial, dmx_data: array.array) -> None:
    try:
        ser.break_condition = True
        time.sleep(BREAK_TIME)
        ser.break_condition = False
        time.sleep(MAB_TIME)
        ser.write(b'\x00')  # DMX start code (0)
        ser.write(dmx_data)
    except serial.SerialException as e:
        logging.error(f"Serial error occurred: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in send_dmx_signal: {e}")

def run() -> None:
    global dmx_data

    looking = False

    while running:
        dmx_interface_port = find_dmx_interface()
        
        if not dmx_interface_port:
            if not looking: logging.info("DMX Interface not found. Waiting for connection...")
            time.sleep(1)
            looking = True
            continue

        logging.info(f'DMX Interface found at {dmx_interface_port}.')

        try:
            with serial.Serial(dmx_interface_port, baudrate=250000, stopbits=2) as ser:
                next_frame_time = time.monotonic()
                while running:
                    current_time = time.monotonic()
                    if current_time >= next_frame_time:
                        send_dmx_signal(ser, dmx_data)
                        next_frame_time += FRAME_TIME
                        if next_frame_time <= current_time:
                            next_frame_time = current_time + FRAME_TIME
                    time.sleep(0.001)
        except KeyboardInterrupt:
            logging.info("Program interrupted by user")
        except serial.SerialException as e:
            logging.error(f"Serial port error: {e}")
            time.sleep(1)  # Wait before trying to reconnect
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            time.sleep(1)  # Wait before trying to reconnect

    logging.info("Closing DMX program")
    sys.exit()