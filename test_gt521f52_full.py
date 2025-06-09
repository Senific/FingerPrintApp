import serial
import time
import struct

class GT521F52Helper:
    def __init__(self, port="/dev/serial0", baudrate=9600, timeout=1):
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        print(f"[GT521F52] Serial port opened at {baudrate} baud.")

    def _build_packet(self, cmd, param=0):
        header = b'\x55\xAA'
        device_id = b'\x01\x00'
        param_bytes = struct.pack('<I', param)
        cmd_bytes = struct.pack('<H', cmd)
        checksum = (sum(param_bytes) + sum(cmd_bytes)) & 0xFFFF
        checksum_bytes = struct.pack('<H', checksum)

        packet = header + device_id + param_bytes + cmd_bytes + checksum_bytes
        return packet

    def _send_packet(self, packet, response_length=12, delay=0.2):
        self.ser.write(packet)
        time.sleep(delay)
        response = self.ser.read(response_length)
        print(f"[GT521F52] Response: {response.hex()}")
        return response

    def open(self):
        print("[GT521F52] Sending Open command...")
        packet = self._build_packet(cmd=0x0001)
        return self._send_packet(packet)

    def set_serial_param(self):
        print("[GT521F52] Sending SetSerialParam command...")
        packet = self._build_packet(cmd=0x0015)
        return self._send_packet(packet)

    def get_device_info(self):
        print("[GT521F52] Sending GetDeviceInfo command...")
        packet = self._build_packet(cmd=0x001F)
        return self._send_packet(packet, response_length=24)

    def led_on(self):
        print("[GT521F52] Sending LED ON command...")
        packet = self._build_packet(cmd=0x0012, param=1)
        return self._send_packet(packet)

    def led_off(self):
        print("[GT521F52] Sending LED OFF command...")
        packet = self._build_packet(cmd=0x0012, param=0)
        return self._send_packet(packet)

    def close(self):
        self.ser.close()
        print("[GT521F52] Serial port closed.")


# === Full Test Sequence with Repeated Attempts ===
if __name__ == "__main__":
    # Try 9600 first — this is the standard default for many modules
    BAUDRATE = 9600
    gt = GT521F52Helper(port="/dev/serial0", baudrate=BAUDRATE)

    # Step 1: Open
    gt.open()

    # Step 2: Attempt SetSerialParam repeatedly
    for i in range(5):  # Retry 5 times
        print(f"\n--- Attempt {i+1}: SetSerialParam ---")
        gt.set_serial_param()
        time.sleep(0.3)
        print(f"--- Attempt {i+1}: Open again ---")
        gt.open()
        time.sleep(0.3)

    # Step 3: Get Device Info
    gt.get_device_info()

    # Step 4: LED ON
    gt.led_on()
    time.sleep(3)

    # Step 5: LED OFF
    gt.led_off()

    # Close serial port
    gt.close()
