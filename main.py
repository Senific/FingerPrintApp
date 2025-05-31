from kivy.app import App
from kivy.uix.label import Label

import os
os.environ["KIVY_BCM_DISPMANX_ID"] = "1"

class TestApp(App):
    def build(self):
        return Label(text='Hello from Kivy!')

TestApp().run()
