import RPi.GPIO as GPIO
import time
from fplib import fplib

TOUCH_PIN = 5  # GPIO5 (physical pin 29)

def on_touch_event(channel):
    if GPIO.input(channel) == GPIO.LOW:
        fplib.open()
        fplib.set_led(True)
        print("👆 Finger touched")
    else:
        fplib.set_led(False)
        fplib.close()
        print("✋ Finger released")

# 1. Set GPIO mode
GPIO.setmode(GPIO.BCM)

# 2. Set up pin as input (external pull-up already used)
GPIO.setup(TOUCH_PIN, GPIO.IN)

# 3. Add event detection for both edges
try:
    GPIO.add_event_detect(TOUCH_PIN, GPIO.BOTH, callback=on_touch_event, bouncetime=100)
    print("✅ Edge detection (touch & release) added successfully.")
except RuntimeError as e:
    print("❌ RuntimeError:", e)
    GPIO.cleanup()
    exit(1)

# 4. Keep running
print("📡 Waiting for finger touch/release...")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("🧹 Cleaning up GPIO...")
    GPIO.cleanup()
