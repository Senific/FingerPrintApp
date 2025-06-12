import os
import fcntl
import struct
import time

# Constants
SG_IO = 0x2285
SG_DXFER_TO_DEV = -2
SG_DXFER_FROM_DEV = -3
SG_DXFER_NONE = -1

# Device path → your GT-521F52 device
DEV_PATH = "/dev/sg0"

# Build CMD_USB_INTERNAL_CHECK Command Packet → 12 bytes
def build_cmd_usb_internal_check():
    cdb_cmd_usb_check = struct.pack('<HHI', 0xAA55, 0x0030, 0x00000001)

    checksum = (0x0030 & 0xFFFF) + (0x00000001 & 0xFFFF) + ((0x00000001 >> 16) & 0xFFFF)
    cdb_cmd_usb_check += struct.pack('<HH', checksum & 0xFFFF, 0x0000)

    return cdb_cmd_usb_check

# Build SG_IO header
def build_sg_io_hdr(cdb, data_out, data_in, dxfer_dir):
    interface_id = ord('S')
    dxfer_len = len(data_out) if dxfer_dir == SG_DXFER_TO_DEV else len(data_in)

    SG_IO_HDR_FORMAT = 'BBBBIIBBHIQIQIIBBBBHH'
    sg_io_hdr = struct.pack(
        SG_IO_HDR_FORMAT,
        interface_id,
        0,                # dxfer_direction
        len(cdb),         # cmd_len
        0,                # mx_sb_len
        0,                # iovec_count
        dxfer_len,        # dxfer_len
        data_out if dxfer_dir == SG_DXFER_TO_DEV else data_in,  # dxferp (ptr)
        cdb,              # cmdp (ptr)
        None,             # sbp
        5000,             # timeout (ms)
        0,                # flags
        0,                # pack_id
        0,                # usr_ptr
        0,                # status
        0,                # masked_status
        0,                # msg_status
        0,                # sb_len_wr
        0,                # host_status
        0                 # driver_status
    )
    return sg_io_hdr

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

    # Open device
    fd = os.open(DEV_PATH, os.O_RDWR)

    # Prepare data buffers
    data_in = bytearray(13)  # Expect 13-byte response

    # Build SG_IO hdr
    SG_IO_HDR_FORMAT = 'BBBBIIBBHIQIQIIBBBBHH'
    sg_io_hdr = struct.pack(
        SG_IO_HDR_FORMAT,
        ord('S'),                   # interface_id
        0,                          # dxfer_direction (ignored here)
        len(cdb),                   # cmd_len
        0,                          # mx_sb_len
        0,                          # iovec_count
        len(data_out),              # dxfer_len
        id(data_out),               # dxferp
        id(cdb),                    # cmdp
        0,                          # sbp
        5000,                       # timeout (ms)
        0,                          # flags
        0,                          # pack_id
        0,                          # usr_ptr
        0,                          # status
        0,                          # masked_status
        0,                          # msg_status
        0,                          # sb_len_wr
        0,                          # host_status
        0                           # driver_status
    )

    # Send ioctl
    try:
        fcntl.ioctl(fd, SG_IO, sg_io_hdr)
        print("SG_IO ioctl sent successfully.")
    except Exception as e:
        print(f"SG_IO ioctl failed: {str(e)}")
        os.close(fd)
        return

    # Close device
    os.close(fd)

# Main
if __name__ == "__main__":
    send_cmd_usb_internal_check()
