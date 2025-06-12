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

# --- USB Mass Storage Reset + Clear HALT ---
print("\nSending USB Mass Storage Reset + Clear HALT...")
try:
    dev.ctrl_transfer(0x21, 0xFF, 0, 0, None)
    time.sleep(0.1)

    dev.clear_halt(ep_out.bEndpointAddress)
    dev.clear_halt(ep_in.bEndpointAddress)
    time.sleep(0.1)

    print("Reset and Clear HALT done.\n")
except usb.core.USBError as e:
    print(f"WARNING: Reset/Clear HALT failed: {e}\n")

# --- Set Interface Alternate Setting ---
print("Setting Interface Alternate Setting...")
try:
    dev.set_interface_altsetting(interface=0, alternate_setting=0)
    time.sleep(0.1)
    print("Interface Alternate Setting done.\n")
except usb.core.USBError as e:
    print(f"WARNING: set_interface_altsetting failed: {e}\n")

# --- Vendor Switch Commands ---
def send_vendor_switch(request):
    print(f"Sending Vendor Switch: bRequest=0x{request:02X}")
    try:
        dev.ctrl_transfer(0x40, request, 0x0001, 0x0000, [0x01])
        time.sleep(0.1)
        print("Vendor Switch sent OK.\n")
    except usb.core.USBError as e:
        print(f"WARNING: Vendor Switch failed: {e}\n")

# --- CBW Builder ---
def build_cbw(cdb, data_transfer_length, bmCBWFlags):
    CBW_SIGNATURE = b'USBS'
    dCBWTag = random.randint(1, 0xFFFFFFFF)
    dCBWDataTransferLength = data_transfer_length
    bCBWLUN = 0
    bCBWCBLength = 0x0D

    CBWCB = cdb + bytes(16 - len(cdb))

    cbw_packet = struct.pack('<4sIIBBB', CBW_SIGNATURE, dCBWTag, dCBWDataTransferLength,
                             bmCBWFlags, bCBWLUN, bCBWCBLength)
    cbw_packet += CBWCB

    return cbw_packet

# --- Send CMD_OPEN ---
def send_cmd_open():
    print("Sending CMD_OPEN...")

    cdb_cmd_open = struct.pack('<HHI', 0xAA55, 0x01, 0x00000001)

    checksum = (0x01 & 0xFFFF) + (0x00000001 & 0xFFFF) + ((0x00000001 >> 16) & 0xFFFF)
    cdb_cmd_open += struct.pack('<HH', checksum & 0xFFFF, 0x0000)

    print("Sending CBW (EF FE)...")
    cbw_cmd_open = build_cbw(cdb_cmd_open, 12, 0xEF)
    ep_out.write(cbw_cmd_open)
    time.sleep(0.05)

    print("Sending Command Packet...")
    ep_out.write(cdb_cmd_open)
    time.sleep(0.05)

    print("Sending CBW (EF FF)...")
    cbw_cmd_open2 = build_cbw(cdb_cmd_open, 12, 0xFF)
    ep_out.write(cbw_cmd_open2)
    time.sleep(0.05)

    print("Reading Response Packet...")
    try:
        resp = ep_in.read(13, timeout=5000)
    except usb.core.USBError as e:
        print(f"USBError while reading response: {str(e)}")
        return

    print(f"Response ({len(resp)} bytes):")
    print(' '.join(f"{b:02X}" for b in resp))

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

# TEST VENDOR SWITCH COMMANDS ONE BY ONE:
# UNCOMMENT ONE AT A TIME TO TEST WHICH ONE WORKS

send_vendor_switch(0x01)
# send_vendor_switch(0x02)
# send_vendor_switch(0x03)

# Once you find which one works, keep only that one active.

# CMD_OPEN
send_cmd_open()

print("\n--- TEST FLOW COMPLETE ---")
