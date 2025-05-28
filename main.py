import os

# Force Kivy to use the framebuffer display
os.environ["KIVY_WINDOW"] = "sdl2"
os.environ["KIVY_TEXT"] = "sdl2"
os.environ["SDL_FBDEV"] = "/dev/fb1"
os.environ["SDL_VIDEODRIVER"] = "fbcon"


from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.clock import Clock
from datetime import datetime


class IdleScreen(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # --- Background Image --- 
        background = Image(
            source="assets/bg.jpg",
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        self.add_widget(background)

        # --- Center Clock --- 
        self.clock_label = Label(
            text="00:00:00",
            font_size='48sp',
            halign='center',
            valign='middle',
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(480, 100),
            pos_hint={"center_x": 0.5, "center_y": 0.6}
        )
        self.clock_label.bind(size=self._update_clock_label)
        self.add_widget(self.clock_label)

        # --- Footer: Company Name --- 
        company_label = Label(
            text="SENIFIC (PVT) LTD - WWW.SENIFIC.COM / 076-4092662",
            font_size='12sp',
            halign='center',
            valign='middle',
            color=(0.9, 0.9, 0.9, 1),
            size_hint=(1, None),
            height=24,
            pos_hint={"center_x": 0.5, "y": .2 }  # Slightly above bottom
        )

        self.add_widget(company_label)

        
        # Start the clock update
        Clock.schedule_interval(self.update_clock, 1)

    def update_clock(self, dt):
        self.clock_label.text = datetime.now().strftime("%H:%M:%S") + "AZ"

    def _update_clock_label(self, instance, value):
        instance.text_size = instance.size

  

class FingerprintApp(App):
    def build(self):
        return IdleScreen()

if __name__ == "__main__":
    FingerprintApp().run()
