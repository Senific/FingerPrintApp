import serial
import time

def print_hex(data, label):
    hex_str = ' '.join(f'{b:02X}' for b in data)
    print(f"[{label}] ({len(data)} bytes) {hex_str}")

# Commands (standard GT-521F52 / GTM-5210F52 packet format: 12 bytes)
CMD_OPEN          = b'\x55\xAA\x01\x00\x00\x00\x00\x00\x01\x00\x01\x01'
CMD_GET_DEVICE_INFO = b'\x55\xAA\x01\x00\x00\x00\x00\x00\x30\x00\x00\x31'
CMD_CMOS_LED_ON   = b'\x55\xAA\x01\x00\x00\x00\x00\x00\x12\x00\x01\x12'
CMD_CMOS_LED_OFF  = b'\x55\xAA\x01\x00\x00\x00\x00\x00\x12\x00\x00\x11'

# Serial config
SERIAL_PORT = '/dev/serial0'
INITIAL_BAUD = 9600
OPERATING_BAUD = 115200
READ_TIMEOUT = 1  # seconds

def send_cmd(ser, cmd, label, expected_len=12):
    print(f"[INFO] Sending {label}...")
    ser.write(cmd)
    ser.flush()
    time.sleep(0.1)
    
    # Read expected_len bytes with timeout handling
    response = b''
    start_time = time.time()
    while len(response) < expected_len and (time.time() - start_time) < READ_TIMEOUT:
        chunk = ser.read(expected_len - len(response))
        if not chunk:
            break
        response += chunk
    
    if response:
        print_hex(response, f"Response to {label}")
    else:
        print(f"[WARN] No response received for {label}.")
    print()

# === TEST 1: Stay at 9600 baud ===
print("\n=== TEST 1: Stay at 9600 baud ===\n")
ser = serial.Serial(SERIAL_PORT, INITIAL_BAUD, timeout=READ_TIMEOUT, rtscts=False, dsrdtr=False)
print(f"[INFO] Serial port {SERIAL_PORT} opened at {INITIAL_BAUD} baud.\n")

send_cmd(ser, CMD_OPEN, "CMD_OPEN")
time.sleep(0.3)

send_cmd(ser, CMD_GET_DEVICE_INFO, "GET_DEVICE_INFO", expected_len=24)  # GT-521F52 returns 24 bytes here
time.sleep(0.3)

send_cmd(ser, CMD_CMOS_LED_ON, "CMOS_LED ON at 9600")
time.sleep(0.5)
send_cmd(ser, CMD_CMOS_LED_OFF, "CMOS_LED OFF at 9600")

ser.close()
print("[INFO] Serial port closed.\n")

# === TEST 2: Switch to 115200 baud ===
print("\n=== TEST 2: Switch to 115200 baud after OPEN ===\n")
ser = serial.Serial(SERIAL_PORT, INITIAL_BAUD, timeout=READ_TIMEOUT, rtscts=False, dsrdtr=False)
print(f"[INFO] Serial port {SERIAL_PORT} opened at {INITIAL_BAUD} baud.\n")

send_cmd(ser, CMD_OPEN, "CMD_OPEN")
time.sleep(0.3)

send_cmd(ser, CMD_GET_DEVICE_INFO, "GET_DEVICE_INFO", expected_len=24)
time.sleep(0.3)

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
