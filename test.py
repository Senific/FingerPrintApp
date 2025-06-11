import usb.core
import usb.util
import time

# CHANGE THIS TO YOUR DEVICE'S VID:PID
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

# Prepare Command Descriptor Block (CDB): EF FF 00 00 00 00 00 00 00 00
cdb = [0xEF, 0xFF] + [0x00] * 8
cdb_bytes = bytes(cdb)

# Send CDB (SCSI commands are usually wrapped in a CBW — this is simplified for testing)
# Many devices accept sending CDB directly via Bulk OUT — your module accepted it via sg_raw!

# Send dummy data (512 zeros) → many modules expect some data phase
data_out = bytes([0x00] * 512)

try:
    print("Sending CDB...")
    ep_out.write(data_out)
    time.sleep(0.1)  # Short wait

    print("Reading response...")
    data_in = ep_in.read(512, timeout=1000)

    print(f"Response ({len(data_in)} bytes):")
    print(' '.join(f'{b:02X}' for b in data_in))

except usb.core.USBError as e:
    print(f"USB Error: {e}")
