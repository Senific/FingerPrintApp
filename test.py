import usb.core
import usb.util
import struct
import time
import random

# --- Device constants ---
VID = 0x2009
PID = 0x7638

# --- Find device ---
dev = usb.core.find(idVendor=VID, idProduct=PID)
if dev is None:
    raise ValueError(f'Device {VID:04X}:{PID:04X} not found!')

print(f"Device found! VID:PID = {VID:04X}:{PID:04X}")

# Detach kernel driver if needed
if dev.is_kernel_driver_active(0):
    print("Detaching kernel driver...")
    dev.detach_kernel_driver(0)

# Set configuration
dev.set_configuration()
cfg = dev.get_active_configuration()
intf = cfg[(0, 0)]

# Get endpoints
ep_out = usb.util.find_descriptor(
    intf,
    custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_OUT
)
ep_in = usb.util.find_descriptor(
    intf,
    custom_match=lambda e: usb.util.endpoint_direction(e.bEndpointAddress) == usb.util.ENDPOINT_IN
)

print(f"Bulk OUT endpoint: 0x{ep_out.bEndpointAddress:02X}")
print(f"Bulk IN endpoint: 0x{ep_in.bEndpointAddress:02X}")

# --- CBW Builder ---
def build_cbw(cdb, data_transfer_length):
    """
    Build CBW packet matching Demo Tool format.
    """
    CBW_SIGNATURE = b'USBS'
    dCBWTag = random.randint(1, 0xFFFFFFFF)
    dCBWDataTransferLength = data_transfer_length
    bmCBWFlags = 0xEF  # Matches Demo Tool
    bCBWLUN = 0
    bCBWCBLength = 0x0D  # Matches Demo Tool (13 bytes)

    # Pad CDB to 16 bytes
    CBWCB = cdb + bytes(16 - len(cdb))

    cbw_packet = struct.pack('<4sIIBBB', CBW_SIGNATURE, dCBWTag, dCBWDataTransferLength,
                             bmCBWFlags, bCBWLUN, bCBWCBLength)
    cbw_packet += CBWCB

    return cbw_packet

# --- Send CMD_OPEN ---
def send_cmd_open():
    print("\nSending CMD_OPEN...")

    # CDB for CMD_OPEN → EF FE → param = 00000001
    cdb_cmd_open = struct.pack('<HHI', 0xAA55, 0x01, 0x00000001)

    # Add checksum + zero
    checksum = (0x01 & 0xFFFF) + (0x00000001 & 0xFFFF) + ((0x00000001 >> 16) & 0xFFFF)
    cdb_cmd_open += struct.pack('<HH', checksum & 0xFFFF, 0x0000)

    # Build CBW packet for CMD_OPEN
    cbw_cmd_open = build_cbw(cdb_cmd_open, 12)

    # --- Send first CBW (EF FE) ---
    print("Sending CBW (EF FE)...")
    ep_out.write(cbw_cmd_open)

    # --- Send Command Packet (12 bytes) ---
    print("Sending Command Packet...")
    ep_out.write(cdb_cmd_open)

    # --- Send second CBW (EF FF) ---
    print("Sending CBW (EF FF)...")
    # Build second CBW with EF FF
    cbw_cmd_open2 = build_cbw(cdb_cmd_open, 12)
    # Change bmCBWFlags to 0xFF
    cbw_cmd_open2 = cbw_cmd_open2[:12] + struct.pack('B', 0xFF) + cbw_cmd_open2[13:]
    ep_out.write(cbw_cmd_open2)

    # --- Read Response Packet ---
    print("Reading Response Packet...")
    try:
        resp = ep_in.read(13, timeout=5000)
    except usb.core.USBError as e:
        print(f"USBError while reading response: {str(e)}")
        return

    print(f"Response ({len(resp)} bytes):")
    print(' '.join(f"{b:02X}" for b in resp))

    # Parse response
    ack_nack = resp[4:8]
    param_returned = struct.unpack('<I', resp[8:12])[0]
    csw_status = resp[12]

    if ack_nack == b'BS42':
        print("ACK received.")
    else:
        print("NACK or unknown response.")

    print(f"Param: 0x{param_returned:08X}")
    print(f"CSW Status: {csw_status}")

# --- Main flow ---
print("\n--- STARTING TEST FLOW ---")

# 1. CMD_OPEN
send_cmd_open()

print("\n--- TEST FLOW COMPLETE ---")
