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

# Initialize device
def init_device():
    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if dev is None:
        raise ValueError('Device not found')

    print("Device found!")

    if dev.is_kernel_driver_active(0):
        print("Detaching kernel driver...")
        dev.detach_kernel_driver(0)

    dev.set_configuration()
    cfg = dev.get_active_configuration()
    intf = cfg[(0, 0)]

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

    return dev, ep_out, ep_in

# Compute checksum (same as Demo Tool)
def compute_checksum(dev_id, cmd, param):
    chksum = dev_id + cmd
    chksum += (param & 0xFFFF)
    chksum += ((param >> 16) & 0xFFFF)
    return chksum & 0xFFFF

# Send command and receive response
def send_gt521f52_command(ep_out, ep_in, cmd, param, expect_data_len=0):
    print(f"\nSending CMD: 0x{cmd:04X}, Param: 0x{param:08X}")

    # Step 1: SEND phase → EF FE
    CBW_SIGNATURE = 0x43425355
    CBW_TAG = random.randint(1, 0xFFFFFFFF)
    CBW_DATA_TRANSFER_LENGTH = 12
    CBW_FLAGS = 0x00
    CBW_LUN = 0
    CBW_CB_LENGTH = 10

    cdb_send = [0xEF, 0xFE] + [0x00] * 8
    cdb_send_bytes = bytes(cdb_send)

    chksum = compute_checksum(DEVICE_ID, cmd, param)
    cmd_packet = struct.pack('<HHIHH',
        DEVICE_ID,
        cmd,
        param,
        chksum,
        0x0000
    )

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

    print("Sending CBW (EF FE)...")
    ep_out.write(cbw_send)
    time.sleep(0.01)

    print("Sending Command Packet...")
    ep_out.write(cmd_packet)
    time.sleep(0.01)

    # Step 2: RECEIVE phase → EF FF
    CBW_DATA_TRANSFER_LENGTH_IN = 12
    CBW_FLAGS_IN = 0x80

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

    print("Sending CBW (EF FF)...")
    ep_out.write(cbw_recv)
    time.sleep(0.01)

    print("Reading Response Packet...")
    resp = ep_in.read(13, timeout=1000)
    print(f"Response ({len(resp)} bytes):")
    print(' '.join(f'{b:02X}' for b in resp))

    # Parse response
    resp_packet = resp[0:12]
    csw_status = resp[12]

    resp_dev_id, resp_ack, resp_param, resp_chksum, resp_zero = struct.unpack('<HHIHH', bytes(resp_packet))

    print(f"Device ID: 0x{resp_dev_id:04X}")
    print(f"ACK / NACK: 0x{resp_ack:04X}")
    print(f"Param: 0x{resp_param:08X}")
    print(f"Checksum: 0x{resp_chksum:04X}")
    print(f"Zero: 0x{resp_zero:04X}")
    print(f"CSW Status: {csw_status}")

    # Interpret CSW status
    if csw_status == 0x00:
        print("CSW Status: Command Passed.")
    elif csw_status == 0x01:
        print("CSW Status: Command Failed.")
    elif csw_status == 0x02:
        print("CSW Status: Phase Error.")
    else:
        print(f"CSW Status: Unknown ({csw_status})")

    # If extra data is expected (e.g. devinfo, image), read it
    if expect_data_len > 0:
        print(f"Reading {expect_data_len} bytes of data...")
        data = bytearray()
        while len(data) < expect_data_len:
            chunk = ep_in.read(min(512, expect_data_len - len(data)), timeout=2000)
            data.extend(chunk)
        print(f"Read {len(data)} bytes.")
        return resp_ack, resp_param, bytes(data)

    return resp_ack, resp_param, None

# Main test loop
if __name__ == "__main__":
    dev, ep_out, ep_in = init_device()

    # CMD_OPEN
    ack, param, devinfo = send_gt521f52_command(ep_out, ep_in, 0x01, 0x00000001, expect_data_len=24)
    print(f"Device Info: {' '.join(f'{b:02X}' for b in devinfo)}")

    # CMD_CMOS_LED ON
    send_gt521f52_command(ep_out, ep_in, 0x12, 0x00000001)

    # Wait for finger press
    print("\nWaiting for finger...")
    while True:
        ack, param, _ = send_gt521f52_command(ep_out, ep_in, 0x26, 0x00000000)
        if param == 0:  # 0 = finger pressed
            print("Finger detected!")
            break
        else:
            print("No finger. Retrying...")
            time.sleep(0.5)

    # CMD_CAPTURE
    send_gt521f52_command(ep_out, ep_in, 0x60, 0x00000001)

    # CMD_GET_IMAGE → capture size depends on your sensor (usually 202x258 = 52016 bytes)
    IMAGE_SIZE = 202 * 258
    _, _, image_data = send_gt521f52_command(ep_out, ep_in, 0x62, 0x00000000, expect_data_len=IMAGE_SIZE)

    # Save image as .pgm (portable graymap) → viewable in image viewers
    print("Saving fingerprint image as 'fingerprint.pgm'...")
    with open("fingerprint.pgm", "wb") as f:
        f.write(f"P5\n202 258\n255\n".encode())
        f.write(image_data)

    print("Image saved.")

    # CMD_CMOS_LED OFF
    send_gt521f52_command(ep_out, ep_in, 0x12, 0x00000000)

    print("\nDone.")
