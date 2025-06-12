import os
import fcntl
import struct
import ctypes
import time

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

# Send CMD_USB_INTERNAL_CHECK
def send_cmd_usb_internal_check():
    print("Sending CMD_USB_INTERNAL_CHECK via SG_IO...")

    cdb = bytearray(16)
    cdb[0] = 0xEF
    cdb[1] = 0xFE
    cdb[4] = 12  # Data-Out length (12 bytes)

    data_out = build_cmd_usb_internal_check()
    data_out_buffer = ctypes.create_string_buffer(data_out)
    sense_buffer = ctypes.create_string_buffer(32)

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
    hdr.timeout = 5000
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

    fd = os.open(DEV_PATH, os.O_RDWR)

    try:
        fcntl.ioctl(fd, SG_IO, hdr)
        print("SG_IO ioctl sent successfully.")
        print(f"SG_IO status: {hdr.status}, host_status: {hdr.host_status}, driver_status: {hdr.driver_status}")

        if hdr.status == 0 and hdr.host_status == 0 and hdr.driver_status == 0:
            print("CMD_USB_INTERNAL_CHECK accepted → device may be unlocked!")
        else:
            print("CMD_USB_INTERNAL_CHECK returned CHECK CONDITION or error.")
    except Exception as e:
        print(f"SG_IO ioctl failed: {str(e)}")

    os.close(fd)

# Send Request Sense
def send_request_sense():
    print("Sending Request Sense via SG_IO...")

    cdb = bytearray(6)
    cdb[0] = 0x03
    cdb[4] = 18  # Allocation length

    data_in_buffer = ctypes.create_string_buffer(18)
    sense_buffer = ctypes.create_string_buffer(32)

    hdr = sg_io_hdr()
    hdr.interface_id = ord('S')
    hdr.dxfer_direction = SG_DXFER_FROM_DEV
    hdr.cmd_len = len(cdb)
    hdr.mx_sb_len = len(sense_buffer)
    hdr.iovec_count = 0
    hdr.dxfer_len = len(data_in_buffer)
    hdr.dxferp = ctypes.addressof(data_in_buffer)
    hdr.cmdp = ctypes.addressof(ctypes.create_string_buffer(bytes(cdb)))
    hdr.sbp = ctypes.addressof(sense_buffer)
    hdr.timeout = 5000
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

    fd = os.open(DEV_PATH, os.O_RDWR)

    try:
        fcntl.ioctl(fd, SG_IO, hdr)
        print("SG_IO ioctl sent successfully (Request Sense).")
        print(f"SG_IO status: {hdr.status}, host_status: {hdr.host_status}, driver_status: {hdr.driver_status}")

        sense_data = bytes(data_in_buffer)
        print("Sense Data:")
        print(' '.join(f'{b:02X}' for b in sense_data))

    except Exception as e:
        print(f"SG_IO ioctl failed (Request Sense): {str(e)}")

    os.close(fd)

# Send MODE SENSE(6)
def send_mode_sense6():
    print("Sending MODE SENSE(6) via SG_IO...")

    cdb = bytearray(6)
    cdb[0] = 0x1A  # MODE SENSE(6)
    cdb[2] = 0x3F  # All pages
    cdb[4] = 0xC0  # Allocation length (192 bytes)

    data_in_buffer = ctypes.create_string_buffer(192)
    sense_buffer = ctypes.create_string_buffer(32)

    hdr = sg_io_hdr()
    hdr.interface_id = ord('S')
    hdr.dxfer_direction = SG_DXFER_FROM_DEV
    hdr.cmd_len = len(cdb)
    hdr.mx_sb_len = len(sense_buffer)
    hdr.iovec_count = 0
    hdr.dxfer_len = len(data_in_buffer)
    hdr.dxferp = ctypes.addressof(data_in_buffer)
    hdr.cmdp = ctypes.addressof(ctypes.create_string_buffer(bytes(cdb)))
    hdr.sbp = ctypes.addressof(sense_buffer)
    hdr.timeout = 5000
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

    fd = os.open(DEV_PATH, os.O_RDWR)

    try:
        fcntl.ioctl(fd, SG_IO, hdr)
        print("SG_IO ioctl sent successfully (MODE SENSE).")
        print(f"SG_IO status: {hdr.status}, host_status: {hdr.host_status}, driver_status: {hdr.driver_status}")

        mode_data = bytes(data_in_buffer)
        print("MODE SENSE Data:")
        print(' '.join(f'{b:02X}' for b in mode_data))

    except Exception as e:
        print(f"SG_IO ioctl failed (MODE SENSE): {str(e)}")

    os.close(fd)

# Main flow
if __name__ == "__main__":
    print("--- FIRST CMD_USB_INTERNAL_CHECK ---")
    send_cmd_usb_internal_check()

    print("\n--- FIRST REQUEST SENSE ---")
    send_request_sense()

    print("\nWaiting 200 ms...")
    time.sleep(0.2)

    print("\n--- SECOND CMD_USB_INTERNAL_CHECK ---")
    send_cmd_usb_internal_check()

    print("\n--- SECOND REQUEST SENSE ---")
    send_request_sense()

    print("\nWaiting 200 ms...")
    time.sleep(0.2)

    print("\n--- MODE SENSE(6) ---")
    send_mode_sense6()

    print("\n--- THIRD REQUEST SENSE ---")
    send_request_sense()

    print("\nWaiting 200 ms...")
    time.sleep(0.2)

    print("\n--- FINAL CMD_USB_INTERNAL_CHECK ---")
    send_cmd_usb_internal_check()

    print("\n--- FLOW COMPLETE ---")
