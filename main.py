from kivy.core.window import Window

# Desired window size
win_width, win_height = 480, 320
Window.size = (win_width, win_height)
Window.fullscreen = False

# Get the screen width and height (physical monitor resolution)
screen_width, screen_height = Window.system_size  # Kivy 2.1+ provides system_size

# Calculate top-left coordinates to center window
Window.left = (screen_width - win_width) // 2
Window.top = (screen_height - win_height) // 2

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
from datetime import datetime

class IdleScreen(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        background = Image(
            source="assets/bg.jpg",
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        self.add_widget(background)

        self.clock_label = Label(
            text="00:00:00",
            font_size='80sp',
            halign='center',
            valign='middle',
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(480, 100),
            pos_hint={"center_x": 0.5, "center_y": 0.6}
        )
        self.clock_label.bind(size=self._update_clock_label)
        self.add_widget(self.clock_label)

        self.resolution_label = Label(
            text= datetime.now().strftime("%d %b %Y"),
            font_size='30sp',
            halign='center',
            valign='middle',
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(480, 40),
            pos_hint={"center_x": 0.5, "center_y": 0.4}
        )
        self.resolution_label.bind(size=self._update_clock_label)
        self.add_widget(self.resolution_label)

        company_label = Label(
            text="SENIFIC (PVT) LTD - WWW.SENIFIC.COM / 076-4092662",
            font_size='18sp',
            halign='center',
            valign='middle',
            color=(0.9, 0.9, 0.9, 1),
            size_hint=(1, None),
            height=24,
            pos_hint={"center_x": 0.5, "y": .2}
        )
        self.add_widget(company_label)

        Clock.schedule_interval(self.update_clock, 1)

    def update_clock(self, dt):
        self.clock_label.text = datetime.now().strftime("%H:%M:%S")

    def _update_clock_label(self, instance, value):
        instance.text_size = instance.size

class FingerprintApp(App):
    def build(self):
        return IdleScreen()

if __name__ == "__main__":
    FingerprintApp().run()
