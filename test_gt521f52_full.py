import serial
import time

def print_hex(data, label):
    print(f"[{label}] " + ' '.join(f'{b:02X}' for b in data))

# Commands
CMD_OPEN      = b'\x55\xAA\x01\x00\x00\x00\x00\x00\x01\x00\x01\x01'
CMD_CMOS_LED_ON  = b'\x55\xAA\x01\x00\x00\x00\x00\x00\x12\x00\x01\x12'
CMD_CMOS_LED_OFF = b'\x55\xAA\x01\x00\x00\x00\x00\x00\x12\x00\x00\x11'

# Port and baud
SERIAL_PORT = '/dev/serial0'
INITIAL_BAUD = 9600
OPERATING_BAUD = 115200

def send_cmd(ser, cmd, label):
    print(f"[INFO] Sending {label}...")
    ser.write(cmd)
    ser.flush()
    time.sleep(0.1)
    response = ser.read(12)
    if response:
        print_hex(response, f"Response to {label}")
    else:
        print(f"[WARN] No response received for {label}.")
    print()

# === Test 1: Keep at 9600 baud ===
print("\n=== TEST 1: Stay at 9600 baud ===\n")
ser = serial.Serial(SERIAL_PORT, INITIAL_BAUD, timeout=1)
print(f"[INFO] Serial port {SERIAL_PORT} opened at {INITIAL_BAUD} baud.\n")

send_cmd(ser, CMD_OPEN, "CMD_OPEN")
time.sleep(0.2)

send_cmd(ser, CMD_CMOS_LED_ON, "CMOS_LED ON at 9600")
time.sleep(0.5)
send_cmd(ser, CMD_CMOS_LED_OFF, "CMOS_LED OFF at 9600")

ser.close()
print("[INFO] Serial port closed.\n")

# === Test 2: Switch to 115200 baud ===
print("\n=== TEST 2: Switch to 115200 baud after OPEN ===\n")
ser = serial.Serial(SERIAL_PORT, INITIAL_BAUD, timeout=1)
print(f"[INFO] Serial port {SERIAL_PORT} opened at {INITIAL_BAUD} baud.\n")

send_cmd(ser, CMD_OPEN, "CMD_OPEN")
time.sleep(0.2)

print(f"[INFO] Switching serial baud rate to {OPERATING_BAUD} baud...")
ser.close()
time.sleep(0.1)
ser.baudrate = OPERATING_BAUD
ser.open()
print(f"[INFO] Serial port reopened at {OPERATING_BAUD} baud.\n")

send_cmd(ser, CMD_CMOS_LED_ON, "CMOS_LED ON at 115200")
time.sleep(0.5)
send_cmd(ser, CMD_CMOS_LED_OFF, "CMOS_LED OFF at 115200")

ser.close()
print("[INFO] Serial port closed.")
