import usb.core
import usb.util
import struct
import time
import random

# Device VID/PID
VENDOR_ID = 0x2009
PRODUCT_ID = 0x7638

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

# Build CBW (Command Block Wrapper)
CBW_SIGNATURE = 0x43425355  # 'USBC'
CBW_TAG = random.randint(1, 0xFFFFFFFF)
CBW_DATA_TRANSFER_LENGTH = 0  # No data phase for this simple test
CBW_FLAGS = 0x80  # IN transfer (bit 7) — let's match sg_raw EF FF command
CBW_LUN = 0
CBW_CB_LENGTH = 10  # Length of CDB

# CDB: EF FF 00 00 00 00 00 00 00 00
cdb = [0xEF, 0xFF] + [0x00] * 8
cdb_bytes = bytes(cdb)

# Pack CBW as per USB Mass Storage Bulk-Only spec
cbw = struct.pack(
    '<I I I B B B 16s',
    CBW_SIGNATURE,
    CBW_TAG,
    CBW_DATA_TRANSFER_LENGTH,
    CBW_FLAGS,
    CBW_LUN,
    CBW_CB_LENGTH,
    cdb_bytes.ljust(16, b'\x00')  # pad to 16 bytes
)

# Send CBW
print("Sending CBW...")
ep_out.write(cbw)
time.sleep(0.1)

# No data phase → go directly to CSW (Command Status Wrapper) → 13 bytes
print("Reading CSW...")
csw = ep_in.read(13, timeout=1000)

# Parse CSW
csw_signature = struct.unpack('<I', csw[0:4])[0]
csw_tag = struct.unpack('<I', csw[4:8])[0]
csw_data_residue = struct.unpack('<I', csw[8:12])[0]
csw_status = csw[12]

# Display CSW
print(f"CSW Signature: {hex(csw_signature)}")
print(f"CSW Tag: {csw_tag}")
print(f"CSW Data Residue: {csw_data_residue}")
print(f"CSW Status: {csw_status}")

# Check CSW status
if csw_signature != 0x53425355:
    print("Invalid CSW Signature!")
elif csw_tag != CBW_TAG:
    print("CSW Tag does not match CBW Tag!")
elif csw_status == 0x00:
    print("Command Passed.")
elif csw_status == 0x01:
    print("Command Failed.")
elif csw_status == 0x02:
    print("Phase Error.")
else:
    print(f"Unknown CSW status: {csw_status}")

print("Done.")
