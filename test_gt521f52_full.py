import serial
import time

def print_hex(data, label):
    print(f"[{label}] " + ' '.join(f'{b:02X}' for b in data))

# Basic commands (packet format is fixed 12 bytes — GT-521F52 datasheet)
CMD_OPEN      = b'\x55\xAA\x01\x00\x00\x00\x00\x00\x01\x00\x01\x01'
CMD_CMOS_LED_ON  = b'\x55\xAA\x01\x00\x00\x00\x00\x00\x12\x00\x01\x12'
CMD_CMOS_LED_OFF = b'\x55\xAA\x01\x00\x00\x00\x00\x00\x12\x00\x00\x11'
CMD_CAPTURE      = b'\x55\xAA\x01\x00\x00\x00\x00\x00\x60\x00\x00\x61'

# Change your serial port here (example for Raspberry Pi UART)
SERIAL_PORT = '/dev/serial0'  # or '/dev/ttyS0' or '/dev/ttyAMA0'

# Initial baud rate — usually 9600 for first OPEN command
INITIAL_BAUD = 9600
# Baud after OPEN — usually 115200
OPERATING_BAUD = 115200

# Open serial port at INITIAL_BAUD
ser = serial.Serial(SERIAL_PORT, INITIAL_BAUD, timeout=1)
print(f"[INFO] Serial port {SERIAL_PORT} opened at {INITIAL_BAUD} baud.\n")

def send_cmd(cmd, label):
    print(f"[INFO] Sending {label}...")
    ser.write(cmd)
    ser.flush()
    time.sleep(0.1)  # small delay
    response = ser.read(12)
    if response:
        print_hex(response, f"Response to {label}")
    else:
        print(f"[WARN] No response received for {label}.")
    print()

# Send CMD_OPEN first
send_cmd(CMD_OPEN, "CMD_OPEN")

# Now change baud rate to OPERATING_BAUD
print(f"[INFO] Switching serial baud rate to {OPERATING_BAUD} baud after CMD_OPEN...")
ser.close()
time.sleep(0.1)  # small delay before reopen
ser.baudrate = OPERATING_BAUD
ser.open()
print(f"[INFO] Serial port reopened at {OPERATING_BAUD} baud.\n")

# Send further commands
send_cmd(CMD_CMOS_LED_ON, "CMOS_LED ON")
time.sleep(0.5)  # keep LED on for a bit
send_cmd(CMD_CMOS_LED_OFF, "CMOS_LED OFF")
send_cmd(CMD_CAPTURE, "CAPTURE")

# Done
ser.close()
print("[INFO] Serial port closed.")
