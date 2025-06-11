import usb.core
import usb.util
import struct
import time

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

# --- Helper: send command ---
def send_gt521f52_command(ep_out, ep_in, cmd, param=0):
    print(f"\nSending CMD: 0x{cmd:04X}, Param: 0x{param:08X}")

    # Send CBW header (EF FE)
    cbw_send = struct.pack('<4sIIIBB', b'USBC', 0x5355, 0, 12, 0xEF, 0xFE)
    ep_out.write(cbw_send)

    # Build command packet
    checksum = (cmd & 0xFFFF) + (param & 0xFFFF) + ((param >> 16) & 0xFFFF)
    packet = struct.pack('<HHIHI', 0x55AA, cmd, param, checksum & 0xFFFF, 0)

    # Send command packet
    ep_out.write(packet)

    # Send second CBW header (EF FF)
    cbw_send = struct.pack('<4sIIIBB', b'USBC', 0x5355, 0, 12, 0xEF, 0xFF)
    ep_out.write(cbw_send)

    # Read response
    try:
        resp = ep_in.read(13, timeout=5000)
    except usb.core.USBError as e:
        print(f"USBError while reading response: {str(e)}")
        return {'ACK': False, 'error': True}

    print(f"Response ({len(resp)} bytes):")
    print(' '.join(f"{b:02X}" for b in resp))

    # Parse response
    ack_nack = resp[4:8]
    param_returned = struct.unpack('<I', resp[8:12])[0]
    csw_status = resp[12]

    result = {
        'ACK': ack_nack == b'BS42',
        'NACK': ack_nack != b'BS42',
        'param': param_returned,
        'csw_status': csw_status,
        'error': False
    }

    if result['ACK']:
        print("ACK received.")
    else:
        print("NACK or unknown response.")

    print(f"Param: 0x{param_returned:08X}")
    print(f"CSW Status: {csw_status}")

    return result

# --- Safe Delete All ---
def safe_delete_all(ep_out, ep_in):
    print("[SAFE DELETE ALL] Starting safe delete sequence...")

    # Step 1: Turn LED ON
    print("Turning LED ON...")
    resp = send_gt521f52_command(ep_out, ep_in, 0x12, 0x00000001)  # CMD_CMOS_LED_ON
    time.sleep(0.1)

    if not resp or resp.get('ACK') != True:
        print("WARNING: LED ON may have failed — aborting delete.")
        return

    # Step 2: CMD_DELETE_ALL
    print("Sending CMD_DELETE_ALL...")
    resp = send_gt521f52_command(ep_out, ep_in, 0x41, 0x00000000)  # CMD_DELETE_ALL

    if not resp or resp.get('ACK') != True:
        print("ERROR: Delete all failed or returned NACK.")
    else:
        print("SUCCESS: All fingerprints deleted.")

    # Step 3: Turn LED OFF
    print("Turning LED OFF...")
    send_gt521f52_command(ep_out, ep_in, 0x13, 0x00000000)  # CMD_CMOS_LED_OFF

    print("[SAFE DELETE ALL] Done.\n")

# --- Main flow ---
print("\n--- STARTING TEST FLOW ---")

# 1. CMD_OPEN
send_gt521f52_command(ep_out, ep_in, 0x01, 0x00000001)  # CMD_OPEN

# 2. Safe delete all
safe_delete_all(ep_out, ep_in)

# 3. CMD_CLOSE
send_gt521f52_command(ep_out, ep_in, 0x02, 0x00000000)  # CMD_CLOSE

print("\n--- TEST FLOW COMPLETE ---")
