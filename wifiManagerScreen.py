from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.clock import Clock
import subprocess
import logging

class WifiListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.networks = {}
        self.network_buttons = {}
        self.layout = BoxLayout(orientation='vertical')

        # Scrollable area
        self.scroll = ScrollView(size_hint=(1, 0.85))
        self.network_list_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.network_list_layout.bind(minimum_height=self.network_list_layout.setter('height'))
        self.scroll.add_widget(self.network_list_layout)

        self.layout.add_widget(self.scroll)

        # Disconnect + Back Buttons
        control_layout = BoxLayout(size_hint=(1, 0.15))
        disconnect_btn = Button(text="Disconnect")
        disconnect_btn.bind(on_press=self.disconnect_wifi)
        control_layout.add_widget(disconnect_btn)

        back_btn = Button(text="Back to Menu")
        back_btn.bind(on_press=self.go_back)
        control_layout.add_widget(back_btn)

        self.layout.add_widget(control_layout)
        self.add_widget(self.layout)

        # Start scanning
        Clock.schedule_interval(self.refresh_wifi_list, 1)

    def refresh_wifi_list(self, dt):
        try:
            output = subprocess.check_output(['nmcli', '-t', '-f', 'SSID,SIGNAL', 'device', 'wifi', 'list']).decode()
            new_networks = {}
            for line in output.strip().split('\n'):
                if not line: continue
                parts = line.split(':')
                if len(parts) >= 2:
                    ssid = parts[0].strip()
                    signal = parts[1].strip()
                    new_networks[ssid] = signal

            if new_networks != self.networks:
                self.network_list_layout.clear_widgets()
                self.network_buttons.clear()

                for ssid, signal in new_networks.items():
                    btn = Button(
                        text=f"{ssid} ({signal}%)",
                        size_hint_y=None,
                        height=50
                    )
                    btn.bind(on_press=lambda instance, s=ssid: self.connect_to_wifi(s))
                    self.network_list_layout.add_widget(btn)
                    self.network_buttons[ssid] = btn

                self.networks = new_networks

        except Exception as e:
            logging.error(f"Failed to refresh Wi-Fi list: {e}")

    def connect_to_wifi(self, ssid):
        content = BoxLayout(orientation='vertical', spacing=10)
        password_input = TextInput(hint_text="Enter password", password=True)
        status_label = Label(text="")

        def on_connect(_):
            password = password_input.text
            try:
                logging.info(f"Connecting to SSID: {ssid}")
                subprocess.check_call(["nmcli", "device", "wifi", "connect", ssid, "password", password, "name", "SenificWiFi"])
                status_label.text = "Connected successfully!"
            except subprocess.CalledProcessError as e:
                status_label.text = f"Connection failed: {e}"

        connect_btn = Button(text="Connect")
        connect_btn.bind(on_press=on_connect)

        content.add_widget(password_input)
        content.add_widget(connect_btn)
        content.add_widget(status_label)

        popup = Popup(title=f"Connect to {ssid}", content=content,
                      size_hint=(0.8, 0.5))
        popup.open()

    def disconnect_wifi(self, instance):
        try:
            subprocess.check_call(["nmcli", "connection", "down", "SenificWiFi"])
            logging.info("Disconnected from SenificWiFi")
        except subprocess.CalledProcessError as e:
            logging.error(f"Disconnect failed: {e}")

    def go_back(self, instance):
        if self.manager:
            self.manager.current = "menu"
