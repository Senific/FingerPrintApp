from gpiozero import Button
from signal import pause
from fplib import fplib

TOUCH_PIN = 5  # BCM GPIO5

def on_touch():
    fplib.open()
    fplib.set_led(True)
    print("👆 Finger touched")

def on_release():
    fplib.set_led(False)
    fplib.close()
    print("✋ Finger released")

# Create button using internal pull-down (we're using external pull-up, so no pull here)
touch_sensor = Button(TOUCH_PIN, pull_up=False)

# Attach event handlers
touch_sensor.when_pressed = on_touch
touch_sensor.when_released = on_release

print("📡 Waiting for finger touch/release...")

# Keep running
pause()
