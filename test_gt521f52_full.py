import serial
import time

# === Serial Port Setup ===
ser = serial.Serial("/dev/serial0", baudrate=9600, timeout=1)

# === Helper function to send command ===
def send_command(packet, desc=""):
    print(f"\n[GT521F52] Sending {desc}...")
    ser.write(packet)
    time.sleep(0.5)
    response = ser.read(12)
    if response:
        print(f"[GT521F52] Response: {response.hex()}")
    else:
        print(f"[GT521F52] ❌ No response received.")

# === Command Packets ===

# CMD_OPEN
cmd_open = b'\x55\xAA\x01\x00\x00\x00\x00\x00\x01\x00\x01\x01'

# CMD_CMOS_LED ON (param=1)
cmd_led_on = b'\x55\xAA\x01\x00\x01\x00\x00\x00\x12\x00\x13\x13'

# CMD_CMOS_LED OFF (param=0)
cmd_led_off = b'\x55\xAA\x01\x00\x00\x00\x00\x00\x12\x00\x12\x12'

# CMD_CAPTURE (param=0 → normal)
cmd_capture = b'\x55\xAA\x01\x00\x00\x00\x00\x00\x60\x00\x60\x60'

# === Test Sequence ===
try:
    print("[GT521F52] Serial port opened at 9600 baud.")

    # Open command
    send_command(cmd_open, "CMD_OPEN")

    # LED ON
    send_command(cmd_led_on, "CMD_CMOS_LED ON")

    time.sleep(2)  # Wait 2 sec with LED ON

    # LED OFF
    send_command(cmd_led_off, "CMD_CMOS_LED OFF")

    # Capture
    send_command(cmd_capture, "CMD_CAPTURE")

finally:
    ser.close()
    print("\n[GT521F52] Serial port closed.")
