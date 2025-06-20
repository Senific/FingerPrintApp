import os
import threading

from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, FloatLayout
from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.label import Label 
from kivy.clock import Clock
from datetime import datetime
import subprocess  
 
from adafruit_ads1x15.ads1115 import ADS1115
from adafruit_ads1x15.analog_in import AnalogIn 
import platform

is_raspberry_pi = platform.system() != "Windows"


if is_raspberry_pi:
    try:
        import board
        import busio
        from adafruit_ads1x15.ads1115 import ADS1115
        from adafruit_ads1x15.analog_in import AnalogIn 

        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS1115(i2c)
        adc_channel = AnalogIn(ads, 0)
    except Exception as e:
        print(f"[ADS1115] Initialization failed: {e}")
        class DummyChannel:
            voltage = 0.0
        adc_channel = DummyChannel()
else:
    print("[ADS1115] Skipping setup (not a Raspberry Pi).")
    class DummyChannel:
        voltage = 0.0
    adc_channel = DummyChannel()


class IdleScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

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
            text=datetime.now().strftime("%d %b %Y"),
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

        self.batterylow_label = Label(
            text="Low Battery, Warning!!!",
            font_size='30sp',
            halign='center',
            valign='middle',
            color= (1, 0, 0, 1),
            size_hint=(None, None),
            size=(480, 40),
            pos_hint={"center_x": 0.5, "center_y": 0.25} 
        )
        self.batterylow_label.opacity = 0
        #self.batterylow_label.bind(size=self._update_clock_label)
        self.add_widget(self.batterylow_label)

        

        company_label = Label(
            text="SENIFIC (PVT) LTD - WWW.SENIFIC.COM / 076-4092662",
            font_size='12sp',
            halign='center',
            valign='middle',
            color=(0.9, 0.9, 0.9, 1),
            size_hint=(1, None),
            height=24,
            pos_hint={"center_x": 0.5, "y": .05}
        )
        self.add_widget(company_label)

        # Combined Wi-Fi + Battery Label (top-left)
        self.status_label = Label(
            text="WiFi: 0%  B: 0%",
            font_size='18sp',
            halign='left',
            valign='top',
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(200, 40),  # Adjust width as needed
            pos_hint={"right": 1, "top": 1},
            padding=(5, 0)  # Small padding inside the label
        )
        self.status_label.bind(size=self._update_clock_label)
        self.add_widget(self.status_label)


        Clock.schedule_interval(self.update_clock, 1)
        Clock.schedule_interval(self.update_status_info, 5)
 

    def update_clock(self, dt):
        self.clock_label.text = datetime.now().strftime("%H:%M:%S")

    def _update_clock_label(self, instance, value):
        instance.text_size = instance.size

    def update_status_info(self, dt):
        wifi = self.get_wifi_strength_percent()
        battery = self.get_battery_percentage()
        new_text = f"WiFi: {wifi}%  B: {battery}"
        self.status_label.text = new_text

          
    def get_wifi_strength_percent(self):
        try:
            result = subprocess.check_output("iwconfig wlan0", shell=True).decode()
            for line in result.split("\n"):
                if "Signal level" in line:
                    dbm = int(line.split("Signal level=")[-1].split(" ")[0])
                    # Convert dBm to percentage (rough estimate)
                    percent = max(0, min(100, 2 * (dbm + 100)))
                    return percent
        except Exception:
            pass
        return 0

    def get_battery_percentage(self): 
        try:
            real_voltage = adc_channel.voltage * (110 / 10)
        except Exception as e:
            print(f"[Battery] Voltage read failed: {e}")
            real_voltage = 0.0

        charged_voltage = 12.4
        shutdown_voltage = 9.2

        fullyDelta = charged_voltage - shutdown_voltage
        delta = real_voltage - shutdown_voltage
        percentage = int((delta / fullyDelta) * 100)

        # Clamp and display
        percentage = max(0, min(percentage, 100))

        self.batterylow_label.opacity = 1 if percentage < 20 else 0

        if percentage <= 0:
            threading.Thread(target=lambda: os.system("sudo poweroff")).start()

        return f"{percentage}%"

    
    def on_touch_down(self, touch):
        self.manager.current = "menu"
        return True