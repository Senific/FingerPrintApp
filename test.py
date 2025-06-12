import time
from fingerprint import FingerprintScanner

scanner = FingerprintScanner('/dev/serial0', 9600)

scanner.open()
scanner.led_on()
time.sleep(2)
scanner.led_off()
scanner.close()
