import serial
import time

class FingerprintScanner:
    def __init__(self, port='/dev/serial0', baudrate=9600):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(0.1)  # Wait for serial to stabilize

    def send_packet(self, packet_hex, read_bytes=12):
        packet = bytes.fromhex(packet_hex)
        self.ser.write(packet)
        print(f"Sent: {packet_hex}")
        time.sleep(0.1)
        resp = self.ser.read(read_bytes)
        print(f"Resp: {resp.hex()}")
        return resp

    def open(self):
        self.send_packet("55 AA 01 00 00 00 00 00 01 00 01 01")

    def close(self):
        self.send_packet("55 AA 01 00 00 00 00 00 02 00 02 01")

    def led_on(self):
        self.send_packet("55 AA 01 00 01 00 00 00 12 00 13 01")

    def led_off(self):
        self.send_packet("55 AA 01 00 00 00 00 00 12 00 12 01")

    def capture(self):
        self.send_packet("55 AA 01 00 00 00 00 00 60 00 60 01")

    def identify(self):
        self.send_packet("55 AA 01 00 00 00 00 00 51 00 51 01")

    def verify(self, enroll_id):
        param_hex = enroll_id.to_bytes(4, byteorder='little').hex()
        checksum = (0x50 + sum(enroll_id.to_bytes(4, 'little'))) & 0xFFFF
        packet = f"55 AA 01 00 {param_hex[6:8]} {param_hex[4:6]} {param_hex[2:4]} {param_hex[0:2]} 50 00 {checksum & 0xFF:02X} {checksum >> 8:02X}"
        self.send_packet(packet)

    def verify_template(self):
        self.send_packet("55 AA 01 00 00 00 00 00 52 00 52 01")

    def identify_template(self):
        self.send_packet("55 AA 01 00 00 00 00 00 53 00 53 01")

    def is_press_finger(self):
        self.send_packet("55 AA 01 00 00 00 00 00 26 00 26 01")

    def get_image(self):
        self.send_packet("55 AA 01 00 00 00 00 00 2A 00 2A 01")

    def get_raw_image(self):
        self.send_packet("55 AA 01 00 00 00 00 00 2B 00 2B 01")

    def cancel(self):
        self.send_packet("55 AA 01 00 00 00 00 00 30 00 30 01")

    def get_live_image(self):
        self.send_packet("55 AA 01 00 00 00 00 00 2C 00 2C 01")

    def get_template_count(self):
        resp = self.send_packet("55 AA 01 00 00 00 00 00 47 00 47 01")
        if len(resp) >= 12:
            param_bytes = resp[4:8]
            count = int.from_bytes(param_bytes, byteorder='little')
            print(f"Template count: {count}")
            return count
        else:
            print("Invalid response length")
            return None


    def delete_id(self, enroll_id):
        param_hex = enroll_id.to_bytes(4, byteorder='little').hex()
        checksum = (0x40 + sum(enroll_id.to_bytes(4, 'little'))) & 0xFFFF
        packet = f"55 AA 01 00 {param_hex[6:8]} {param_hex[4:6]} {param_hex[2:4]} {param_hex[0:2]} 40 00 {checksum & 0xFF:02X} {checksum >> 8:02X}"
        self.send_packet(packet)

    def delete_all(self):
        self.send_packet("55 AA 01 00 00 00 00 00 41 00 41 01")

    def get_template(self):
        self.send_packet("55 AA 01 00 00 00 00 00 43 00 43 01")

    def set_template(self):
        self.send_packet("55 AA 01 00 00 00 00 00 44 00 44 01")

    def set_security_level(self, level):
        param_hex = level.to_bytes(4, byteorder='little').hex()
        checksum = (0x4F + sum(level.to_bytes(4, 'little'))) & 0xFFFF
        packet = f"55 AA 01 00 {param_hex[6:8]} {param_hex[4:6]} {param_hex[2:4]} {param_hex[0:2]} 4F 00 {checksum & 0xFF:02X} {checksum >> 8:02X}"
        self.send_packet(packet)

    def get_security_level(self):
        self.send_packet("55 AA 01 00 00 00 00 00 4E 00 4E 01")

    def get_device_info(self):
        self.send_packet("55 AA 01 00 00 00 00 00 31 00 31 01")

    def enroll_start(self, enroll_id):
        param_hex = enroll_id.to_bytes(4, byteorder='little').hex()
        checksum = (0x22 + sum(enroll_id.to_bytes(4, 'little'))) & 0xFFFF
        packet = f"55 AA 01 00 {param_hex[6:8]} {param_hex[4:6]} {param_hex[2:4]} {param_hex[0:2]} 22 00 {checksum & 0xFF:02X} {checksum >> 8:02X}"
        self.send_packet(packet)

    def enroll_step(self, step_cmd):
        cmd_hex = f"{step_cmd & 0xFF:02X} 00"
        checksum = step_cmd & 0xFFFF
        packet = f"55 AA 01 00 00 00 00 00 {cmd_hex} {checksum & 0xFF:02X} {checksum >> 8:02X}"
        self.send_packet(packet)

    def __del__(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
