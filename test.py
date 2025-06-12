# test_driver_cli.py

from fingerprint import FingerprintDriver, USBTransport, SerialTransport
import sys
import time

def main():
    # transport = USBTransport(VID, PID)
    # OR Serial:
    transport = SerialTransport('/dev/serial0', 9600)

    driver = FingerprintDriver(transport)

    try:
        print("Opening device...")
        driver.open()
        print(f"Device opened. Last ACK param = {driver.last_ack_param}")

        print("Turning LED ON...")
        driver.cmos_led(True)

        print("Checking finger press...")
        driver.is_press_finger()
        print(f"IsPressFinger param = {driver.last_ack_param}")

        print("Capturing image...")
        driver.capture(True)

        print("Getting image...")
        driver.get_image()
        with open('fingerprint_image.raw', 'wb') as f:
            f.write(driver.img8bit)
        print("Image saved to fingerprint_image.raw")

        print("Enroll start at pos 0...")
        driver.enroll_start(0)
        for i in range(3):
            input(f"Place finger and press Enter for enroll step {i+1}...")
            driver.enroll_nth(0, i)
            print(f"Enroll step {i+1} done.")

        print("Identifying...")
        driver.identify()
        print(f"Identify param = {driver.last_ack_param}")

        print("Turning LED OFF...")
        driver.cmos_led(False)

        print("Closing device...")
        driver.close()
        print("Device closed.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if hasattr(transport, 'close'):
            transport.close()

if __name__ == "__main__":
    main()
