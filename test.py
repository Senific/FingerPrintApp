import serial
import time

# Open serial port
ser = serial.Serial("/dev/serial0", baudrate=9600, timeout=1)

# === Build Open command manually ===
# Header: 55 AA
# Device ID: 01 00
# Param: 00 00 00 00
# Cmd: 01 00
# Checksum: 01 00 + 00 + 00 + 00 + 00 = 01 00

open_command = b'\x55\xAA\x01\x00\x00\x00\x00\x00\x01\x00\x01\x01'

# Send the command
ser.write(open_command)

# Wait a bit to let the scanner respond
time.sleep(0.2)

# Read response (usually 12 bytes for ACK/NACK)
response = ser.read(12)

# Print response in hex
print("Response:", response.hex())

# Close serial port
ser.close()
