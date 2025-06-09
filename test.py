import serial
import time

# === Setup ===
ser = serial.Serial("/dev/serial0", baudrate=9600, timeout=1)
print("[GT521F52] Serial port opened at 9600 baud.")

# === Helper function ===
def send_packet(packet, response_length=12, delay=0.2, label=""):
    ser.write(packet)
    time.sleep(delay)
    response = ser.read(response_length)
    print(f"[GT521F52] {label} Response: {response.hex()}")
    return response

# === Command Packets ===

# Open Command
open_command = b'\x55\xAA\x01\x00\x00\x00\x00\x00\x01\x00\x01\x01'

# SetSerialParam Command
set_serial_param_command = b'\x55\xAA\x01\x00\x00\x00\x00\x00\x15\x00\x16\x16'

# GetDeviceInfo Command (response = 24 bytes)
get_device_info_command = b'\x55\xAA\x01\x00\x00\x00\x00\x00\x1F\x00\x20\x20'

# LED ON Command (param = 1)
led_on_command = b'\x55\xAA\x01\x00\x01\x00\x00\x00\x12\x00\x13\x13'

# LED OFF Command (param = 0)
led_off_command = b'\x55\xAA\x01\x00\x00\x00\x00\x00\x12\x00\x12\x12'

# === Test Sequence ===

# Step 1: Open
send_packet(open_command, label="Open Initial")

# Step 2: SetSerialParam (retry 5 times)
for i in range(5):
    print(f"\n--- Attempt {i+1}: SetSerialParam ---")
    send_packet(set_serial_param_command, label=f"SetSerialParam Attempt {i+1}")
    time.sleep(0.3)
    print(f"--- Attempt {i+1}: Open again ---")
    send_packet(open_command, label=f"Open Attempt {i+1}")
    time.sleep(0.3)

# Step 3: Get Device Info
send_packet(get_device_info_command, response_length=24, label="GetDeviceInfo")

# Step 4: LED ON
send_packet(led_on_command, label="LED ON")
time.sleep(3)

# Step 5: LED OFF
send_packet(led_off_command, label="LED OFF")

# === Done ===
ser.close()
print("[GT521F52] Serial port closed.")
