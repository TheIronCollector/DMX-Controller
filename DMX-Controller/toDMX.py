import serial
import time
import serial.tools.list_ports
import array
import logging
import sys

running: bool = True

# DMX data
dmx_data = array.array('B', [0] * 512)

# Timing constants
FRAME_TIME = 1 / 120  # Approx. 8.3 ms between frames (120 Hz)
BREAK_TIME = 0.005    # 5 ms break time
MAB_TIME = 0.000012   # 12 microseconds for Mark After Break

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_dmx_dongle():
    """
    Finds a USB to DMX dongle by checking VID/PID or description.

    Returns:
        str: The COM port of the DMX dongle, or None if not found.
    """
    # Known VID/PID for USB to DMX devices (add more as needed)
    known_dongles = [
        (0x0403, 0x6001),  # Example: FTDI-based devices (like Enttec Open DMX)
        (0x1A86, 0x7523),  # Example: CH340-based devices
        (0x067B, 0x2303),  # Example: PL2303-based devices
    ]

    ports = serial.tools.list_ports.comports()
    for port in ports:
        # Check for VID/PID match
        if port.vid and port.pid:
            for vid, pid in known_dongles:
                if port.vid == vid and port.pid == pid:
                    print(f"Found DMX dongle on {port.device} (VID: {vid}, PID: {pid})")
                    return port.device

        # Optionally, check for description if VID/PID is unavailable
        if "DMX" in (port.description or "").upper() or "DMX" in (port.manufacturer or "").upper():
            print(f"Found DMX dongle on {port.device} (Description: {port.description})")
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
        dmx_interface_port = find_dmx_dongle()
        
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
                    # print(dmx_data[0:16])
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