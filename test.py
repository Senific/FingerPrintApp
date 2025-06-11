import usb.core
import usb.util

# Replace these with your device VID and PID from lsusb
VENDOR_ID = 0x0c2e
PRODUCT_ID = 0x0b05

# Find the device
dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)

if dev is None:
    raise ValueError('Device not found')

print("Device found!")

# Detach kernel driver if needed (very common for USB SCSI devices)
if dev.is_kernel_driver_active(0):
    dev.detach_kernel_driver(0)

# Set configuration
dev.set_configuration()

# Claim interface (usually interface 0)
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

print(f"Bulk OUT endpoint: 0x{ep_out.bEndpointAddress:02x}")
print(f"Bulk IN endpoint: 0x{ep_in.bEndpointAddress:02x}")

# Prepare dummy SCSI command (as your Demo Tool does)
# CDB: 0xEF, 0xFF → Read
# Here we send the CDB first, followed by expected data phase
# Many devices require wrapping this in a SCSI CBW structure — we will try raw first

try:
    # Example command — you will need to refine this later
    cdb = [0xEF, 0xFF] + [0x00] * 8  # 10-byte CDB like your tool uses

    # Send CDB as control transfer (first experiment — may need bulk later)
    # This is not always accepted, depends on firmware — for full SCSI we'd use SG_IO ioctl.
    # But pyusb has no direct SCSI wrapper — we simulate with Bulk transfer:

    # Send dummy data
    data_out = bytes([0x00] * 512)  # Send zeroed data — you can send real commands here

    print("Sending data...")
    ep_out.write(data_out)

    print("Reading response...")
    data_in = ep_in.read(512, timeout=1000)

    print(f"Response: {data_in}")

except usb.core.USBError as e:
    print(f"USB Error: {e}")
