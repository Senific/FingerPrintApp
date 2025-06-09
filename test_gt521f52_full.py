import serial
import time
import struct

class GT521F52Helper:
    def __init__(self, port="/dev/serial0", baudrate=9600, timeout=1):
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        print(f"[GT521F52] Serial port opened at {baudrate} baud.")

    def _build_packet(self, cmd, param=0):
        # Build a 12-byte command packet
        header = b'\x55\xAA'
        device_id = b'\x01\x00'
        param_bytes = struct.pack('<I', param)  # 4 bytes little-endian
        cmd_bytes = struct.pack('<H', cmd)      # 2 bytes little-endian
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


# === Full Test Sequence ===
if __name__ == "__main__":
    # Try 9600 first, if no success, try 115200
    BAUDRATE = 9600
    gt = GT521F52Helper(port="/dev/serial0", baudrate=BAUDRATE)

    # Step 1: Open
    gt.open()

    # Step 2: Try SetSerialParam (send twice as per datasheet suggestion)
    gt.set_serial_param()
    time.sleep(0.2)
    gt.set_serial_param()
    time.sleep(0.2)

    # Step 3: Open again
    gt.open()

    # Step 4: Get Device Info
    gt.get_device_info()

    # Step 5: LED ON
    gt.led_on()
    time.sleep(3)

    # Step 6: LED OFF
    gt.led_off()

    # Close serial port
    gt.close()
