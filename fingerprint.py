import serial
import time

class FingerprintScanner:
    def __init__(self, port='/dev/serial0', baudrate=9600):
        self.ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(0.1)  # Wait for serial to stabilize

    def receive_packet(self, expected_length=12, timeout=1.0):
        start_time = time.time()
        packet = b''

        # Step 1: Wait for header 55 AA
        while True:
            if time.time() - start_time > timeout:
                print("Timeout waiting for header.")
                return b''

            header = self.ser.read(2)
            if len(header) == 2 and header[0] == 0x55 and header[1] == 0xAA:
                packet += header
                break
            else:
                time.sleep(0.005)

        # Step 2: Read the rest of the packet
        while len(packet) < expected_length:
            if time.time() - start_time > timeout:
                print("Timeout waiting for full packet.")
                return packet

            remaining = expected_length - len(packet)
            chunk = self.ser.read(remaining)
            if chunk:
                packet += chunk
            else:
                time.sleep(0.005)

        print(f"Resp: {packet.hex()}")
        return packet

    def send_packet(self, packet_hex, read_bytes=12):
        packet = bytes.fromhex(packet_hex)
        self.ser.write(packet)
        print(f"Sent: {packet_hex}")
        time.sleep(0.05)
        return self.receive_packet(expected_length=read_bytes)

    def parse_response(self, resp):
        if len(resp) < 12:
            print("Invalid response length")
            return None, None

        resp_code = resp[8] + (resp[9] << 8)
        param_bytes = resp[4:8]
        param = int.from_bytes(param_bytes, byteorder='little')

        print(f"Response Code: 0x{resp_code:04X}, Param: {param}")

        return resp_code, param

    def open(self):
        resp = self.send_packet("55 AA 01 00 00 00 00 00 01 00 01 01")
        return self.parse_response(resp)

    def close(self):
        resp = self.send_packet("55 AA 01 00 00 00 00 00 02 00 02 01")
        return self.parse_response(resp)

    def led_on(self):
        resp = self.send_packet("55 AA 01 00 01 00 00 00 12 00 13 01")
        return self.parse_response(resp)

    def led_off(self):
        resp = self.send_packet("55 AA 01 00 00 00 00 00 12 00 12 01")
        return self.parse_response(resp)

    def is_press_finger(self):
        resp = self.send_packet("55 AA 01 00 00 00 00 00 26 00 26 01", read_bytes=12)
        resp_code, param = self.parse_response(resp)
        if resp_code == 0x0030:
            return param
        else:
            print(f"Unexpected response code: 0x{resp_code:04X}")
            return None

    def wait_for_finger_press(self, timeout=10, verbose=True):
        self.led_on()
        if verbose:
            print("Waiting for finger press...")
        start_time = time.time()
        while True:
            param = self.is_press_finger()
            if param == 1:
                if verbose:
                    print("Finger is pressed.")
                break
            if time.time() - start_time > timeout:
                if verbose:
                    print("Timeout waiting for finger press.")
                break
            time.sleep(0.1)

    def wait_for_finger_release(self, timeout=10, verbose=True):
        if verbose:
            print("Waiting for finger release...")
        start_time = time.time()
        while True:
            param = self.is_press_finger()
            if param == 0:
                if verbose:
                    print("Finger is released.")
                break
            if time.time() - start_time > timeout:
                if verbose:
                    print("Timeout waiting for finger release.")
                break
            time.sleep(0.1)

    def capture(self):
        resp = self.send_packet("55 AA 01 00 00 00 00 00 60 00 60 01")
        return self.parse_response(resp)

    def enroll_start(self, enroll_id):
        param_hex = enroll_id.to_bytes(4, byteorder='little').hex()
        checksum = (0x22 + sum(enroll_id.to_bytes(4, 'little'))) & 0xFFFF
        packet = f"55 AA 01 00 {param_hex[6:8]} {param_hex[4:6]} {param_hex[2:4]} {param_hex[0:2]} 22 00 {checksum & 0xFF:02X} {checksum >> 8:02X}"
        resp = self.send_packet(packet)
        return self.parse_response(resp)

    def enroll_step(self, step_cmd):
        cmd_hex = f"{step_cmd & 0xFF:02X} 00"
        checksum = step_cmd & 0xFFFF
        packet = f"55 AA 01 00 00 00 00 00 {cmd_hex} {checksum & 0xFF:02X} {checksum >> 8:02X}"
        resp = self.send_packet(packet)
        return self.parse_response(resp)

    def identify(self):
        resp = self.send_packet("55 AA 01 00 00 00 00 00 51 00 51 01")
        return self.parse_response(resp)

    def verify(self, enroll_id):
        param_hex = enroll_id.to_bytes(4, byteorder='little').hex()
        checksum = (0x50 + sum(enroll_id.to_bytes(4, 'little'))) & 0xFFFF
        packet = f"55 AA 01 00 {param_hex[6:8]} {param_hex[4:6]} {param_hex[2:4]} {param_hex[0:2]} 50 00 {checksum & 0xFF:02X} {checksum >> 8:02X}"
        resp = self.send_packet(packet)
        return self.parse_response(resp)

    def delete_id(self, enroll_id):
        param_hex = enroll_id.to_bytes(4, byteorder='little').hex()
        checksum = (0x40 + sum(enroll_id.to_bytes(4, 'little'))) & 0xFFFF
        packet = f"55 AA 01 00 {param_hex[6:8]} {param_hex[4:6]} {param_hex[2:4]} {param_hex[0:2]} 40 00 {checksum & 0xFF:02X} {checksum >> 8:02X}"
        resp = self.send_packet(packet)
        return self.parse_response(resp)

    def delete_all(self):
        resp = self.send_packet("55 AA 01 00 00 00 00 00 41 00 41 01")
        return self.parse_response(resp)

    def get_template_count(self):
        resp = self.send_packet("55 AA 01 00 00 00 00 00 20 00 20 01", read_bytes=24)
        resp_code, param = self.parse_response(resp)
        if resp_code == 0x0030:
            print(f"Template count: {param}")
            return param
        else:
            print("Failed to get template count.")
            return None

    def get_device_info(self):
        resp = self.send_packet("55 AA 01 00 00 00 00 00 31 00 31 01")
        return self.parse_response(resp)

    def set_security_level(self, level):
        param_hex = level.to_bytes(4, byteorder='little').hex()
        checksum = (0x4F + sum(level.to_bytes(4, 'little'))) & 0xFFFF
        packet = f"55 AA 01 00 {param_hex[6:8]} {param_hex[4:6]} {param_hex[2:4]} {param_hex[0:2]} 4F 00 {checksum & 0xFF:02X} {checksum >> 8:02X}"
        resp = self.send_packet(packet)
        return self.parse_response(resp)

    def get_security_level(self):
        resp = self.send_packet("55 AA 01 00 00 00 00 00 4E 00 4E 01")
        return self.parse_response(resp)

    def cancel(self):
        resp = self.send_packet("55 AA 01 00 00 00 00 00 30 00 30 01")
        return self.parse_response(resp)

    def __del__(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
