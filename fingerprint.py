import struct
import time

# Constants from sb_protocol_oem.h
STX1 = 0x55
STX2 = 0xAA
STX3 = 0x5A
STX4 = 0xA5

SB_OEM_PKT_SIZE = 12
SB_OEM_HEADER_SIZE = 2
SB_OEM_DEV_ID_SIZE = 2
SB_OEM_CHK_SUM_SIZE = 2

# Example Commands (fill all as needed)
CMD_OPEN = 0x01
CMD_CLOSE = 0x02
CMD_USB_INTERNAL_CHECK = 0x03
CMD_MODULE_INFO = 0x06
CMD_CMOS_LED = 0x12
CMD_ENROLL_COUNT = 0x20
CMD_CHECK_ENROLLED = 0x21
CMD_ENROLL_START = 0x22
CMD_ENROLL = 0x23
CMD_ENROLL1 = 0x23
CMD_ENROLL2 = 0x24
CMD_ENROLL3 = 0x25
CMD_IS_PRESS_FINGER = 0x26
CMD_DELETE = 0x40
CMD_DELETE_ALL = 0x41
CMD_VERIFY = 0x50
CMD_IDENTIFY = 0x51
CMD_VERIFY_TEMPLATE = 0x52
CMD_IDENTIFY_TEMPLATE = 0x53
CMD_CAPTURE = 0x60
CMD_GET_IMAGE = 0x62
CMD_GET_RAWIMAGE = 0x63
CMD_GET_TEMPLATE = 0x70
CMD_ADD_TEMPLATE = 0x71
CMD_GET_DATABASE_START = 0x72
CMD_GET_DATABASE_END = 0x73

ACK_OK = 0x30
NACK_INFO = 0x31

IMAGE_SIZE_MAX = 640 * 480
FP_TEMPLATE_SIZE_MAX = 5000

class Transport:
    """
    Abstract Transport Layer.
    Must implement send(data: bytes), recv(size: int) -> bytes
    """
    def send(self, data: bytes):
        raise NotImplementedError

    def recv(self, size: int) -> bytes:
        raise NotImplementedError

class FingerprintDriver:
    def __init__(self, transport: Transport):
        self.transport = transport

        self.dev_id = 1

        self.img8bit = bytearray(IMAGE_SIZE_MAX)
        self.imgRaw = bytearray(IMAGE_SIZE_MAX)
        self.templateBuf = bytearray(FP_TEMPLATE_SIZE_MAX)

        self.last_ack = 0
        self.last_ack_param = 0

    def _calc_cmd_checksum(self, packet):
        return sum(packet) & 0xFFFF

    def _send_cmd(self, cmd, param):
        pkt = struct.pack('<BBHihH',
                          STX1, STX2,
                          self.dev_id,
                          param,
                          cmd,
                          0)
        chk = self._calc_cmd_checksum(pkt[:-2])
        pkt = pkt[:-2] + struct.pack('<H', chk)
        self.transport.send(pkt)

    def _recv_ack(self):
        data = self.transport.recv(SB_OEM_PKT_SIZE)
        if len(data) != SB_OEM_PKT_SIZE:
            raise Exception("Invalid ACK packet size")

        head1, head2, dev_id, param, cmd, chk = struct.unpack('<BBHihH', data)

        if head1 != STX1 or head2 != STX2:
            raise Exception("Invalid ACK header")
        if dev_id != self.dev_id:
            raise Exception("ACK DevID mismatch")

        calc_chk = self._calc_cmd_checksum(data[:-2])
        if chk != calc_chk:
            raise Exception("ACK checksum error")

        self.last_ack = cmd
        self.last_ack_param = param

    def _send_data(self, buf):
        header = struct.pack('<BBH', STX3, STX4, self.dev_id)
        chk = sum(header) + sum(buf)
        chk &= 0xFFFF

        self.transport.send(header + buf + struct.pack('<H', chk))

    def _recv_data(self, size):
        total_size = size + SB_OEM_HEADER_SIZE + SB_OEM_DEV_ID_SIZE + SB_OEM_CHK_SUM_SIZE
        data = self.transport.recv(total_size)

        if len(data) != total_size:
            raise Exception("Invalid Data packet size")

        head1, head2, dev_id = struct.unpack('<BBH', data[:SB_OEM_HEADER_SIZE + SB_OEM_DEV_ID_SIZE])

        if head1 != STX3 or head2 != STX4:
            raise Exception("Invalid Data header")
        if dev_id != self.dev_id:
            raise Exception("Data DevID mismatch")

        payload = data[SB_OEM_HEADER_SIZE + SB_OEM_DEV_ID_SIZE:-2]
        recv_chk = struct.unpack('<H', data[-2:])[0]

        calc_chk = sum(data[:SB_OEM_HEADER_SIZE + SB_OEM_DEV_ID_SIZE]) + sum(payload)
        calc_chk &= 0xFFFF

        if recv_chk != calc_chk:
            raise Exception("Data checksum error")

        return payload

    def command_run(self, cmd, param=0):
        self._send_cmd(cmd, param)
        self._recv_ack()

    def open(self):
        self.command_run(CMD_OPEN, 1)

    def close(self):
        self.command_run(CMD_CLOSE, 0)

    def usb_internal_check(self):
        self.command_run(CMD_USB_INTERNAL_CHECK, self.dev_id)

    def cmos_led(self, on: bool):
        self.command_run(CMD_CMOS_LED, 1 if on else 0)

    def enroll_count(self):
        self.command_run(CMD_ENROLL_COUNT, 0)

    def check_enrolled(self, pos):
        self.command_run(CMD_CHECK_ENROLLED, pos)

    def enroll_start(self, pos):
        self.command_run(CMD_ENROLL_START, pos)

    def enroll_nth(self, pos, nth):
        self.command_run(CMD_ENROLL + nth, 0)

    def is_press_finger(self):
        self.command_run(CMD_IS_PRESS_FINGER, 0)

    def delete(self, pos):
        self.command_run(CMD_DELETE, pos)

    def delete_all(self):
        self.command_run(CMD_DELETE_ALL, 0)

    def verify(self, pos):
        self.command_run(CMD_VERIFY, pos)

    def identify(self):
        self.command_run(CMD_IDENTIFY, 0)

    def verify_template(self, template_buf):
        self.command_run(CMD_VERIFY_TEMPLATE, 0)
        if self.last_ack == ACK_OK:
            self._send_data(template_buf)
            self._recv_ack()

    def identify_template(self, template_buf):
        self.command_run(CMD_IDENTIFY_TEMPLATE, 0)
        if self.last_ack == ACK_OK:
            self._send_data(template_buf)
            self._recv_ack()

    def capture(self, best: bool):
        self.command_run(CMD_CAPTURE, 1 if best else 0)

    def get_image(self):
        self.command_run(CMD_GET_IMAGE, 0)
        img_data = self._recv_data(202 * 258)  # Example size; adapt as needed
        self.img8bit[:len(img_data)] = img_data

    def get_rawimage(self):
        self.command_run(CMD_GET_RAWIMAGE, 0)
        img_data = self._recv_data(202 * 258)  # Example size; adapt as needed
        self.imgRaw[:len(img_data)] = img_data

    def get_template(self, pos):
        self.command_run(CMD_GET_TEMPLATE, pos)
        if self.last_ack == ACK_OK:
            tmpl_data = self._recv_data(FP_TEMPLATE_SIZE_MAX)
            self.templateBuf[:len(tmpl_data)] = tmpl_data

    def add_template(self, pos, template_buf):
        self.command_run(CMD_ADD_TEMPLATE, pos)
        if self.last_ack == ACK_OK:
            self._send_data(template_buf)
            self._recv_ack()

    def get_database_start(self):
        self.command_run(CMD_GET_DATABASE_START, 0)

    def get_database_end(self):
        self.command_run(CMD_GET_DATABASE_END, 0)
