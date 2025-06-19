import pigpio
import time
from fplib import fplib

# fingerprint module variables
fp = fplib()

# module initializing
init = fp.init()
print("is initialized :", init)


TOUCH_PIN = 5  # GPIO5 (Physical pin 29)

def on_touch(gpio, level, tick):
    if level == 0:
        fplib.open()
        fplib.set_led(True)
        print("👆 Finger touched")
    elif level == 1:
        fplib.set_led(False)
        fplib.close()
        print("✋ Finger released")

# Connect to pigpio daemon
pi = pigpio.pi()
if not pi.connected:
    print("❌ Failed to connect to pigpiod. Is it running?")
    exit(1)

# Set the pin as input
pi.set_mode(TOUCH_PIN, pigpio.INPUT)

# Register callback on both edges
pi.callback(TOUCH_PIN, pigpio.EITHER_EDGE, on_touch)

print("📡 Waiting for finger touch/release... Press Ctrl+C to stop.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🧹 Cleaning up...")
    pi.stop()
