import usb.core
import usb.util
import struct
import time
import random

# Device VID/PID
VENDOR_ID = 0x2009
PRODUCT_ID = 0x7638

# Device ID used in protocol
DEVICE_ID = 0x0001

# Find device
dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
if dev is None:
    raise ValueError('Device not found')

print("Device found!")

# Detach kernel driver if necessary
if dev.is_kernel_driver_active(0):
    print("Detaching kernel driver...")
    dev.detach_kernel_driver(0)

# Set configuration
dev.set_configuration()
cfg = dev.get_active_configuration()
intf = cfg[(0, 0)]

# Find Bulk OUT and Bulk IN endpoints
ep_out = usb.util.find_descriptor(
    intf,
    custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
)

ep_in = usb.util.find_descriptor(
    intf,
    custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
)

if ep_out is None or ep_in is None:
    raise ValueError("Could not find both Bulk OUT and Bulk IN endpoints")

print(f"Bulk OUT endpoint: 0x{ep_out.bEndpointAddress:02x}")
print(f"Bulk IN endpoint: 0x{ep_in.bEndpointAddress:02x}")

# Helper to compute checksum (same as Demo Tool)
def compute_checksum(dev_id, cmd, param):
    chksum = dev_id + cmd
    chksum += (param & 0xFFFF)
    chksum += ((param >> 16) & 0xFFFF)
    return chksum & 0xFFFF

# Function to send command and receive response
def send_gt521f52_command(cmd, param):
    print(f"\nSending CMD: 0x{cmd:04X}, Param: 0x{param:08X}")

    # Step 1: SEND phase → EF FE
    CBW_SIGNATURE = 0x43425355
    CBW_TAG = random.randint(1, 0xFFFFFFFF)
    CBW_DATA_TRANSFER_LENGTH = 12  # 12 bytes data OUT
    CBW_FLAGS = 0x00  # OUT
    CBW_LUN = 0
    CBW_CB_LENGTH = 10

    cdb_send = [0xEF, 0xFE] + [0x00] * 8
    cdb_send_bytes = bytes(cdb_send)

    # Build command packet
    chksum = compute_checksum(DEVICE_ID, cmd, param)
    cmd_packet = struct.pack('<HHIHH',
        DEVICE_ID,
        cmd,
        param,
        chksum,
        0x0000
    )

    # Build CBW
    cbw_send = struct.pack(
        '<I I I B B B 16s',
        CBW_SIGNATURE,
        CBW_TAG,
        CBW_DATA_TRANSFER_LENGTH,
        CBW_FLAGS,
        CBW_LUN,
        CBW_CB_LENGTH,
        cdb_send_bytes.ljust(16, b'\x00')
    )

    # Send CBW
    print("Sending CBW (EF FE)...")
    ep_out.write(cbw_send)
    time.sleep(0.01)

    # Send command packet (12 bytes)
    print("Sending Command Packet...")
    ep_out.write(cmd_packet)
    time.sleep(0.01)

    # Step 2: RECEIVE phase → EF FF
    CBW_DATA_TRANSFER_LENGTH_IN = 12
    CBW_FLAGS_IN = 0x80  # IN

    cdb_recv = [0xEF, 0xFF] + [0x00] * 8
    cdb_recv_bytes = bytes(cdb_recv)

    cbw_recv = struct.pack(
        '<I I I B B B 16s',
        CBW_SIGNATURE,
        CBW_TAG,
        CBW_DATA_TRANSFER_LENGTH_IN,
        CBW_FLAGS_IN,
        CBW_LUN,
        CBW_CB_LENGTH,
        cdb_recv_bytes.ljust(16, b'\x00')
    )

    # Send CBW for receive
    print("Sending CBW (EF FF)...")
    ep_out.write(cbw_recv)
    time.sleep(0.01)

    # Read response (12 bytes)
    print("Reading Response Packet...")
    resp = ep_in.read(12, timeout=1000)
    print(f"Response ({len(resp)} bytes):")
    print(' '.join(f'{b:02X}' for b in resp))

    # Parse response
    resp_dev_id, resp_ack, resp_param, resp_chksum, resp_zero = struct.unpack('<HHIHH', bytes(resp))
    print(f"Device ID: 0x{resp_dev_id:04X}")
    print(f"ACK / NACK: 0x{resp_ack:04X}")
    print(f"Param: 0x{resp_param:08X}")
    print(f"Checksum: 0x{resp_chksum:04X}")
    print(f"Zero: 0x{resp_zero:04X}")

# === TESTING ===

# CMD_OPEN → CMD = 0x01, Param = 0x00000001
send_gt521f52_command(0x01, 0x00000001)

# CMD_CMOS_LED ON → CMD = 0x12, Param = 0x00000001
send_gt521f52_command(0x12, 0x00000001)

# Wait a moment with LED ON
time.sleep(1)

# CMD_CMOS_LED OFF → CMD = 0x12, Param = 0x00000000
send_gt521f52_command(0x12, 0x00000000)

print("\nDone.")
