import RPi.GPIO as GPIO
import time

TOUCH_PIN = 5

def on_finger_touch(channel):
    print("👆 Finger touched!")

# Clean previous state
GPIO.cleanup()

# Use BCM numbering
GPIO.setmode(GPIO.BCM)

# Setup the pin with pull-down resistor
GPIO.setup(TOUCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    GPIO.add_event_detect(TOUCH_PIN, GPIO.RISING, callback=on_finger_touch, bouncetime=200)
    print("✅ Edge detection added successfully.")
except RuntimeError as e:
    print(f"❌ RuntimeError: {e}")
    exit(1)

try:
    print("Waiting for input...")
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
