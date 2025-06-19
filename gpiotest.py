import RPi.GPIO as GPIO
import time

TOUCH_PIN = 5  # GPIO5

GPIO.setmode(GPIO.BCM)

# Use pull-up if external transistor pulls low
GPIO.setup(TOUCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def touched(channel):
    print("👆 Touch Detected")

try:
    GPIO.add_event_detect(TOUCH_PIN, GPIO.FALLING, callback=touched, bouncetime=200)
    print("✅ Ready, waiting for touch...")
    while True:
        time.sleep(1)
except RuntimeError as e:
    print("❌ RuntimeError:", e)
finally:
    GPIO.cleanup()
