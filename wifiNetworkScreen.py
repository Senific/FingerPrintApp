from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
import subprocess
import threading
import sys

class WifiNetworkScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical')
        self.scroll = ScrollView()
        self.network_box = BoxLayout(orientation='vertical', size_hint_y=None)
        self.network_box.bind(minimum_height=self.network_box.setter('height'))
        self.scroll.add_widget(self.network_box)
        self.layout.add_widget(self.scroll)

        self.back_button = Button(text='Back to Menu', size_hint=(1, None), height=50)
        self.back_button.bind(on_press=self.go_back)
        self.layout.add_widget(self.back_button)

        self.add_widget(self.layout)
        self.network_buttons = {}
        self.current_ssid = None

        self.text_input_ref = None
        self.refresh_event = None

    def on_enter(self):
        self.refresh_event = Clock.schedule_interval(self.refresh_networks, 2)

    def on_leave(self):
        if self.refresh_event:
            self.refresh_event.cancel()
            self.refresh_event = None

    def go_back(self, instance):
        if self.manager:
            self.manager.current = 'menu'

    def refresh_networks(self, dt):
        threading.Thread(target=self.scan_networks).start()

    def scan_networks(self):
        try:
            if sys.platform.startswith('win'):
                dummy_networks = [
                    ("TestWiFi_1", "78"),
                    ("MyHomeNetwork", "64"),
                    ("GuestWiFi", "55"),
                    ("CafeNet", "40"),
                    ("PublicFreeWiFi", "25")
                ]
                active_ssid = "MyHomeNetwork"

                def update_ui():
                    self.network_box.clear_widgets()
                    self.network_buttons.clear()
                    for ssid, signal in dummy_networks:
                        btn_text = f"{ssid} ({signal}%)"
                        btn = Button(text=btn_text, size_hint_y=None, height=50)
                        btn.bind(on_press=self.on_network_selected)
                        self.network_box.add_widget(btn)
                        self.network_buttons[btn] = ssid
                        if ssid == active_ssid:
                            btn.background_color = (0, 1, 0, 1)
                            self.current_ssid = ssid

                Clock.schedule_once(lambda dt: update_ui())
            else:
                connected = subprocess.check_output("nmcli -t -f active,ssid dev wifi", shell=True).decode()
                active_ssid = None
                for line in connected.splitlines():
                    if line.startswith("yes:"):
                        active_ssid = line.split(":", 1)[1]
                        break

                result = subprocess.check_output("nmcli -t -f ssid,signal dev wifi", shell=True).decode()
                networks = []
                for line in result.splitlines():
                    parts = line.strip().split(":")
                    if len(parts) == 2:
                        ssid, signal = parts
                        if ssid:
                            networks.append((ssid, signal))

                def update_ui():
                    self.network_box.clear_widgets()
                    self.network_buttons.clear()
                    for ssid, signal in networks:
                        btn_text = f"{ssid} ({signal}%)"
                        btn = Button(text=btn_text, size_hint_y=None, height=50)
                        btn.bind(on_press=self.on_network_selected)
                        self.network_box.add_widget(btn)
                        self.network_buttons[btn] = ssid
                        if ssid == active_ssid:
                            btn.background_color = (0, 1, 0, 1)
                            self.current_ssid = ssid

                Clock.schedule_once(lambda dt: update_ui())

        except Exception as e:
            msg = str(e)
            Clock.schedule_once(lambda dt, msg=msg: self.show_popup("Error", msg))

    def on_network_selected(self, instance):
        ssid = self.network_buttons[instance]
        if ssid == self.current_ssid:
            self.confirm_disconnect(ssid)
        else:
            self.prompt_password(ssid)

    def prompt_password(self, ssid):
        content = BoxLayout(orientation='vertical', padding=[20, 20, 20, 20], spacing=10)

        input_field = TextInput(
            hint_text='Password',
            password=True,
            multiline=False,
            size_hint=(1, None),
            height=40
        )
        content.add_widget(input_field)

        popup = Popup(
            title=f"Connect to {ssid}",
            content=content,
            size_hint=(0.9, None),
            height=200,
            auto_dismiss=True
        )

        def on_connect(instance):
            password = input_field.text.strip()
            if password:
                popup.dismiss()
                threading.Thread(target=self.connect_to_network, args=(ssid, password)).start()
            else:
                self.show_popup("Input Error", "Password cannot be empty")

        connect_button = Button(
            text='Connect',
            size_hint=(1, None),
            height=40
        )
        connect_button.bind(on_press=on_connect)
        content.add_widget(connect_button)

        popup.open()
        Clock.schedule_once(lambda dt: setattr(input_field, 'focus', True), 0.1)
        self.text_input_ref = input_field

    def connect_to_network(self, ssid, password):
        self.show_popup("Connecting", f"Connecting to {ssid}...")
        def do_connect():
            try:
            subprocess.run(["nmcli", "connection", "delete", "SenificWiFi"], check=False)
            subprocess.run(["nmcli", "device", "wifi", "connect", ssid, "password", password, "name", "SenificWiFi"], check=True)
            self.current_ssid = ssid
            Clock.schedule_once(lambda dt: self.refresh_networks(0))
                Clock.schedule_once(lambda dt: self.show_popup("Connected", f"Connected to {ssid}"))
        except subprocess.CalledProcessError as e:
                Clock.schedule_once(lambda dt, msg=str(e): self.show_popup("Connection Failed", msg))

    def confirm_disconnect(self, ssid):
        content = BoxLayout(orientation='vertical')
        lbl = Label(text=f"Disconnect from {ssid}?")
        content.add_widget(lbl)

        def do_disconnect(instance):
            try:
                result = subprocess.check_output("nmcli -t -f NAME,DEVICE connection show --active", shell=True).decode()
                for line in result.strip().splitlines():
                    name, device = line.split(":")
                    if device == "wlan0":
                        subprocess.run(["nmcli", "connection", "down", name], check=False)
                        break
                self.current_ssid = None
                Clock.schedule_once(lambda dt: self.refresh_networks(0))
            except Exception as e:
                Clock.schedule_once(lambda dt, msg=str(e): self.show_popup("Error", msg))
            popup.dismiss()

        btn = Button(text="Disconnect", size_hint_y=None, height=40)
        btn.bind(on_press=do_disconnect)
        content.add_widget(btn)

        popup = Popup(title="Disconnect", content=content, size_hint=(0.8, 0.4))
        popup.open()

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text=message, size_hint_y=None, height=100, text_size=(400, None), halign='center', valign='middle')
        label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
        close_btn = Button(text='Close', size_hint_y=None, height=40)

        popup = Popup(title=title, content=content, size_hint=(0.9, None), height=200, auto_dismiss=True)
        close_btn.bind(on_press=popup.dismiss)

        content.add_widget(label)
        content.add_widget(close_btn)
        popup.open()
