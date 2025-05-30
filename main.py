# import logging
# logging.basicConfig(filename='app.log', level=logging.DEBUG)
import os
os.environ["KIVY_NO_CONSOLELOG"] = "1"
os.environ["KIVY_NO_FILELOG"] = "1"
os.environ["KIVY_BCM_DISPMANX_ID"] = "2"
os.environ["KIVY_METRICS_DENSITY"] = "2"
os.environ["KIVY_CLOCK"] = "default"
os.environ["KIVY_VIDEO"] = "ffpyplayer"
os.environ["KIVY_TEXT"] = "pil"
os.environ["SDL_FBDEV"] = "/dev/fb1"
os.environ["KIVY_WINDOW"] = "sdl"
os.environ["SDL_FBDEV"] = "/dev/fb1" 



from kivy.config import Config
# Config.set('graphics', 'fullscreen', '1')  # or 'auto'
# Config.set('graphics', 'show_cursor', '0')
# Config.set('graphics', 'resizable', '0')
# Config.set('graphics', 'width', '320')    # Adjust to your 3.5" screen size
# Config.set('graphics', 'height', '480')

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
