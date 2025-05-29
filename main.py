import logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)



from kivy.core.window import Window

from idleScreen import IdleScreen
from menuScreen import MenuScreen
from wifiConnectScreen import WifiConnectScreen

# Desired window size
# win_width, win_height = 480, 320
# Window.size = (win_width, win_height)
Window.fullscreen = True

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
