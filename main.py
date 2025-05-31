import os
import sys

from kivy.config import Config
# Detect if running on Raspberry Pi
is_raspberry = False

if sys.platform == "linux":
    try:
        with open("/proc/cpuinfo", "r") as f:
            cpuinfo = f.read()
        is_raspberry = "Raspberry Pi" in cpuinfo or "BCM" in cpuinfo
    except:
        pass

# Input setup
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')  # No multitouch emulation

# Cursor visibility based on device
if is_raspberry:
    Config.set('graphics', 'show_cursor', '0')  # Hide cursor on Raspberry Pi
else:
    Config.set('graphics', 'show_cursor', '1')  # Show cursor elsewhere

# Disable the touch cross
Config.set('modules', 'touchring', '')


import logging
from datetime import datetime

# Path to admin's home directory
log_dir = os.path.expanduser("~admin")
log_file = os.path.join(log_dir, "app_debug.log")

# Ensure directory exists (it should already exist, but just in case)
os.makedirs(log_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filename=log_file,
    filemode="a"
)

from kivy.core.window import Window
from idleScreen import IdleScreen
from menuScreen import MenuScreen
from wifiConnectScreen import WifiConnectScreen

# Desired window size
win_width, win_height = 480, 320
Window.size = (win_width, win_height)
Window.fullscreen = False

# Get the screen width and height (physical monitor resolution)
screen_width, screen_height = Window.system_size  # Kivy 2.1+ provides system_size

# Calculate top-left coordinates to center window
Window.left = (screen_width - win_width) // 2
Window.top = (screen_height - win_height) // 2

from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.app import App
 

class FingerprintApp(App):
    def build(self):
        sm = ScreenManager(transition=FadeTransition())
 
        sm.add_widget(IdleScreen(name='main'))
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(WifiConnectScreen(name='wifi'))

        return sm

if __name__ == "__main__":
    FingerprintApp().run()
