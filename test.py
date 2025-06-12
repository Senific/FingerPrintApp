import os
import fcntl
import struct
import ctypes

# Constants
SG_IO = 0x2285
SG_DXFER_TO_DEV = -2
SG_DXFER_FROM_DEV = -3
SG_DXFER_NONE = -1

DEV_PATH = "/dev/sg0"

# Define SG_IO header structure
class sg_io_hdr(ctypes.Structure):
    _fields_ = [
        ("interface_id", ctypes.c_int),
        ("dxfer_direction", ctypes.c_int),
        ("cmd_len", ctypes.c_ubyte),
        ("mx_sb_len", ctypes.c_ubyte),
        ("iovec_count", ctypes.c_ushort),
        ("dxfer_len", ctypes.c_uint),
        ("dxferp", ctypes.c_void_p),
        ("cmdp", ctypes.c_void_p),
        ("sbp", ctypes.c_void_p),
        ("timeout", ctypes.c_uint),
        ("flags", ctypes.c_uint),
        ("pack_id", ctypes.c_int),
        ("usr_ptr", ctypes.c_void_p),
        ("status", ctypes.c_ubyte),
        ("masked_status", ctypes.c_ubyte),
        ("msg_status", ctypes.c_ubyte),
        ("sb_len_wr", ctypes.c_ubyte),
        ("host_status", ctypes.c_ushort),
        ("driver_status", ctypes.c_ushort),
        ("resid", ctypes.c_int),
        ("duration", ctypes.c_uint),
        ("info", ctypes.c_uint),
    ]

# Build CMD_USB_INTERNAL_CHECK Command Packet → 12 bytes
def build_cmd_usb_internal_check():
    cdb_cmd_usb_check = struct.pack('<HHI', 0xAA55, 0x0030, 0x00000001)

    checksum = (0x0030 & 0xFFFF) + (0x00000001 & 0xFFFF) + ((0x00000001 >> 16) & 0xFFFF)
    cdb_cmd_usb_check += struct.pack('<HH', checksum & 0xFFFF, 0x0000)

    return cdb_cmd_usb_check

# Main SG_IO send function
def send_cmd_usb_internal_check():
    print("Sending CMD_USB_INTERNAL_CHECK via SG_IO...")

    # Build CDB → EF FE
    cdb = bytearray(16)
    cdb[0] = 0xEF
    cdb[1] = 0xFE
    cdb[4] = 12  # Data-Out length (12 bytes)

    # Build Data-Out → 12-byte Command Packet
    data_out = build_cmd_usb_internal_check()
    data_out_buffer = ctypes.create_string_buffer(data_out)

    # Sense buffer → not used but required
    sense_buffer = ctypes.create_string_buffer(32)

    # Build SG_IO header
    hdr = sg_io_hdr()
    hdr.interface_id = ord('S')
    hdr.dxfer_direction = SG_DXFER_TO_DEV
    hdr.cmd_len = len(cdb)
    hdr.mx_sb_len = len(sense_buffer)
    hdr.iovec_count = 0
    hdr.dxfer_len = len(data_out)
    hdr.dxferp = ctypes.addressof(data_out_buffer)
    hdr.cmdp = ctypes.addressof(ctypes.create_string_buffer(bytes(cdb)))
    hdr.sbp = ctypes.addressof(sense_buffer)
    hdr.timeout = 5000  # 5000 ms
    hdr.flags = 0
    hdr.pack_id = 0
    hdr.usr_ptr = None
    hdr.status = 0
    hdr.masked_status = 0
    hdr.msg_status = 0
    hdr.sb_len_wr = 0
    hdr.host_status = 0
    hdr.driver_status = 0
    hdr.resid = 0
    hdr.duration = 0
    hdr.info = 0

    # Open device
    fd = os.open(DEV_PATH, os.O_RDWR)

    # Send ioctl
    try:
        fcntl.ioctl(fd, SG_IO, hdr)
        print("SG_IO ioctl sent successfully.")

        # Check status
        print(f"SG_IO status: {hdr.status}, host_status: {hdr.host_status}, driver_status: {hdr.driver_status}")

        if hdr.status == 0 and hdr.host_status == 0 and hdr.driver_status == 0:
            print("CMD_USB_INTERNAL_CHECK likely accepted.")
        else:
            print("CMD_USB_INTERNAL_CHECK may have failed (check response/status).")

    except Exception as e:
        print(f"SG_IO ioctl failed: {str(e)}")

    # Close device
    os.close(fd)

# Main
if __name__ == "__main__":
    send_cmd_usb_internal_check()
