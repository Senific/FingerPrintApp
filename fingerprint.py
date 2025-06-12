import serial
import time

class FingerprintScanner:
    def __init__(self, port='/dev/serial0', baudrate=9600):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(0.1)  # Wait for serial to stabilize

    def send_packet(self, packet_hex):
        packet = bytes.fromhex(packet_hex)
        self.ser.write(packet)
        print(f"Sent: {packet_hex}")
        time.sleep(0.1)
        resp = self.ser.read(12)  # Basic response packet
        print(f"Resp: {resp.hex()}")
        return resp

    def open(self):
        # CMD_OPEN = 0x0001
        self.send_packet("55 AA 01 00 00 00 00 00 01 00 01 01")

    def close(self):
        # CMD_CLOSE = 0x0002
        self.send_packet("55 AA 01 00 00 00 00 00 02 00 02 01")

    def led_on(self):
        # CMOS_LED ON = CMD 0x0012, param = 0x00000001
        self.send_packet("55 AA 01 00 01 00 00 00 12 00 13 01")

    def led_off(self):
        # CMOS_LED OFF = CMD 0x0012, param = 0x00000000
        self.send_packet("55 AA 01 00 00 00 00 00 12 00 12 01")

    def capture(self):
        # CMD_CAPTURE = 0x0060, param = 0x00000000 (normal capture)
        self.send_packet("55 AA 01 00 00 00 00 00 60 00 60 01")

    def identify(self):
        # CMD_IDENTIFY = 0x0051
        self.send_packet("55 AA 01 00 00 00 00 00 51 00 51 01")

    def enroll_start(self, enroll_id):
        # CMD_ENROLL_START = 0x0022
        param_hex = enroll_id.to_bytes(4, byteorder='little').hex()
        checksum = (0x22 + (enroll_id & 0xFF) + ((enroll_id >> 8) & 0xFF) + ((enroll_id >> 16) & 0xFF) + ((enroll_id >> 24) & 0xFF)) & 0xFFFF
        packet = f"55 AA 01 00 {param_hex[6:8]} {param_hex[4:6]} {param_hex[2:4]} {param_hex[0:2]} 22 00 {checksum & 0xFF:02X} {checksum >> 8:02X}"
        self.send_packet(packet)

    def enroll_step(self, step_cmd):
        # step_cmd = 0x0023 (ENROLL_1), 0x0024 (ENROLL_2), 0x0025 (ENROLL_3)
        cmd_hex = f"{step_cmd & 0xFF:02X} 00"
        checksum = step_cmd & 0xFFFF
        packet = f"55 AA 01 00 00 00 00 00 {cmd_hex} {checksum & 0xFF:02X} {checksum >> 8:02X}"
        self.send_packet(packet)

    def delete_id(self, enroll_id):
        # CMD_DELETE_ID = 0x0040
        param_hex = enroll_id.to_bytes(4, byteorder='little').hex()
        checksum = (0x40 + (enroll_id & 0xFF) + ((enroll_id >> 8) & 0xFF) + ((enroll_id >> 16) & 0xFF) + ((enroll_id >> 24) & 0xFF)) & 0xFFFF
        packet = f"55 AA 01 00 {param_hex[6:8]} {param_hex[4:6]} {param_hex[2:4]} {param_hex[0:2]} 40 00 {checksum & 0xFF:02X} {checksum >> 8:02X}"
        self.send_packet(packet)

    def __del__(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
