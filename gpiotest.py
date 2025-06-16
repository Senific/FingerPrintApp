import RPi.GPIO as GPIO
import time

TOUCH_PIN = 5  # GPIO5 (physical pin 29)

def on_touch_detected(channel):
    print("👆 Touch detected on GPIO", channel)

# 1. Set GPIO mode
GPIO.setmode(GPIO.BCM)

# 2. Set up pin as input with internal PULL DOWN (optional if using external resistor)
GPIO.setup(TOUCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# 3. Try to add event detection
try:
    GPIO.add_event_detect(TOUCH_PIN, GPIO.RISING, callback=on_touch_detected, bouncetime=200)
    print("✅ Edge detection added successfully.")
except RuntimeError as e:
    print("❌ RuntimeError:", e)
    GPIO.cleanup()
    exit(1)

# 4. Keep running
print("📡 Waiting for touch...")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("🧹 Cleaning up GPIO...")
    GPIO.cleanup()
