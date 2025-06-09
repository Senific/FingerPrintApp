import serial
import time

# === Serial Port Setup ===
# Try 9600 first. If no response, change to 115200.
BAUDRATE = 9600  # or 115200 depending on your module

ser = serial.Serial("/dev/serial0", baudrate=BAUDRATE, timeout=1)

# === GT-521F52 Open Command Packet ===
# Format: 12 bytes
# [Header1][Header2][DeviceID][Param][Cmd][Checksum]
# Open Command: 55 AA 01 00 00 00 00 00 01 00 01 01

open_command_packet = b'\x55\xAA\x01\x00\x00\x00\x00\x00\x01\x00\x01\x01'

# === Send Open Command ===
print(f"Sending Open command at {BAUDRATE} baud...")
ser.write(open_command_packet)

# === Wait for Response ===
time.sleep(0.5)
response = ser.read(12)  # Expect 12-byte standard response packet

# === Show Response ===
if response:
    print("Response received:", response.hex())
else:
    print("❌ No response received.")

# Close serial port
ser.close()
