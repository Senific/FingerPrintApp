from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
from datetime import datetime
import os

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
            font_size='72sp',
            halign='center',
            valign='middle',
            color=(1, 1, 1, 1),  # White color
            size_hint=(None, None),
            pos_hint={"center_x": 0.5, "center_y": 0.6}
        )
        self.clock_label.bind(size=self._update_clock_label)
        self.add_widget(self.clock_label)

        # --- Footer: Company Name ---
        company_label = Label(
            text="SENIFIC (PVT) LTD - WWW.SENIFIC.COM / 076-4092662",
            font_size='12sp',
            halign='center',
            valign='bottom',
            color=(0.9, 0.9, 0.9, 1),
            size_hint=(1, None),
            height=20,
            pos_hint={"center_x": 0.5, "y": 0.01}
        )
        self.add_widget(company_label)

        # Start the clock update
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
