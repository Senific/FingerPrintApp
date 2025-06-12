import serial
import time

# Open serial port — change /dev/ttyUSB0 if needed
#ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
ser = serial.Serial('/dev/serial0', 9600, timeout=1)

def send_packet(packet_hex):
    packet = bytes.fromhex(packet_hex)
    ser.write(packet)
    print(f"Sent: {packet_hex}")
    time.sleep(0.1)
    resp = ser.read(12)  # Read response packet (basic)
    print(f"Resp: {resp.hex()}")

# Example usage:
# 1. Turn LED ON
send_packet("55 AA 01 00 01 00 00 00 12 00 13 01")

# 2. Wait 2 seconds
time.sleep(2)

# 3. Turn LED OFF
send_packet("55 AA 01 00 00 00 00 00 12 00 12 01")

# Close port
ser.close()
