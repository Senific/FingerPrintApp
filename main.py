import logging
import os
os.environ["KIVY_BCM_DISPMANX_ID"] = "1"
 
from datetime import datetime 
# Log to a temporary file
log_file = "/tmp/fingerprint_debug.log"
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.debug("App started at {}".format(datetime.now()))

try:
    # Import your app code
    from main import FingerprintApp  # replace if needed
    FingerprintApp().run()
except Exception as e:
    logging.exception("Exception occurred:")

from kivy.core.window import Window
from idleScreen import IdleScreen
from menuScreen import MenuScreen
from wifiConnectScreen import WifiConnectScreen

# Desired window size
# win_width, win_height = 480, 320
# Window.size = (win_width, win_height)
# Window.fullscreen = False

# Get the screen width and height (physical monitor resolution)
#screen_width, screen_height = Window.system_size  # Kivy 2.1+ provides system_size

# Calculate top-left coordinates to center window
# Window.left = (screen_width - win_width) // 2
# Window.top = (screen_height - win_height) // 2

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
