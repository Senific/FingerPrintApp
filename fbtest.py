import os
os.environ["KIVY_BCM_DISPMANX_DISPLAY"] = "1"
os.environ["KIVY_WINDOW"] = "sdl2"
os.environ["SDL_FBDEV"] = "/dev/fb1"
os.environ["KIVY_GL_BACKEND"] = "gl"

from kivy.app import App
from kivy.uix.label import Label

class TestApp(App):
    def build(self):
        return Label(text="Hello LCD", font_size='24sp')

TestApp().run()
