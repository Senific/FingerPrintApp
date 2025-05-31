import subprocess
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
import logging


class WifiManagerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=20)
        self.status_label = Label(text="Scanning Wi-Fi...", size_hint=(1, 0.1))
        self.layout.add_widget(self.status_label)
        self.network_buttons = []

        self.disconnect_btn = Button(text="Disconnect Wi-Fi", size_hint=(1, 0.1))
        self.disconnect_btn.bind(on_press=self.disconnect_wifi)
        self.layout.add_widget(self.disconnect_btn)

        self.add_widget(self.layout)
        self.scan_networks()

    def scan_networks(self):
        try:
            output = subprocess.check_output(["nmcli", "-t", "-f", "SSID", "device", "wifi", "list"],
                                             text=True).strip()
            ssids = list({ssid for ssid in output.split('\n') if ssid.strip()})
            self.status_label.text = "Select a Wi-Fi network:"
            for btn in self.network_buttons:
                self.layout.remove_widget(btn)
            self.network_buttons = []

            for ssid in ssids:
                btn = Button(text=ssid, size_hint=(1, 0.1))
                btn.bind(on_press=self.prompt_password)
                self.layout.add_widget(btn)
                self.network_buttons.append(btn)

        except Exception as e:
            self.status_label.text = f"Error scanning Wi-Fi: {e}"
            logging.error("Wi-Fi scan failed", exc_info=True)

    def prompt_password(self, instance):
        ssid = instance.text

        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        password_input = TextInput(password=True, hint_text="Enter Password", multiline=False)
        status_label = Label(text="")
        connect_button = Button(text="Connect")

        def do_connect(_):
            password = password_input.text.strip()
            popup.dismiss()
            self.connect_to_wifi(ssid, password)

        connect_button.bind(on_press=do_connect)
        popup_layout.add_widget(Label(text=f"Connecting to: {ssid}"))
        popup_layout.add_widget(password_input)
        popup_layout.add_widget(status_label)
        popup_layout.add_widget(connect_button)

        popup = Popup(title="Wi-Fi Password", content=popup_layout,
                      size_hint=(0.8, 0.5), auto_dismiss=True)
        popup.open()

    def connect_to_wifi(self, ssid, password):
        try:
            subprocess.run(["nmcli", "connection", "delete", "SenificWiFi"],
                           check=False, capture_output=True)
            subprocess.run([
                "nmcli", "device", "wifi", "connect", ssid,
                "password", password, "name", "SenificWiFi"
            ], check=True)
            self.status_label.text = f"✅ Connected to {ssid}"
        except subprocess.CalledProcessError as e:
            self.status_label.text = f"❌ Connection failed: {e}"
            logging.error("Wi-Fi connection failed", exc_info=True)

    def disconnect_wifi(self, instance):
        try:
            subprocess.run(["nmcli", "connection", "down", "SenificWiFi"], check=True)
            self.status_label.text = "✅ Disconnected from Wi-Fi"
        except subprocess.CalledProcessError as e:
            self.status_label.text = f"❌ Failed to disconnect: {e}"
            logging.error("Wi-Fi disconnection failed", exc_info=True)
