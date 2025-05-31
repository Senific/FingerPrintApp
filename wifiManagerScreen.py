import subprocess
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
import logging


class WifiManagerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.status_label = Label(text="🔍 Scanning for Wi-Fi...", size_hint=(1, 0.1))
        main_layout.add_widget(self.status_label)

        self.scroll_view = ScrollView(size_hint=(1, 0.6))
        self.network_list = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.network_list.bind(minimum_height=self.network_list.setter('height'))
        self.scroll_view.add_widget(self.network_list)
        main_layout.add_widget(self.scroll_view)

        action_buttons = BoxLayout(size_hint=(1, 0.2), spacing=10)

        self.disconnect_btn = Button(text="❌ Disconnect Wi-Fi")
        self.disconnect_btn.bind(on_press=self.disconnect_wifi)
        action_buttons.add_widget(self.disconnect_btn)

        self.back_btn = Button(text="🔙 Back to Menu")
        self.back_btn.bind(on_press=self.go_back)
        action_buttons.add_widget(self.back_btn)

        main_layout.add_widget(action_buttons)
        self.add_widget(main_layout)

        self.scan_networks()

    def scan_networks(self):
        try:
            output = subprocess.check_output(
                ["nmcli", "-t", "-f", "SSID,SIGNAL", "device", "wifi", "list"],
                text=True
            ).strip()

            entries = list({line for line in output.split('\n') if line})
            self.network_list.clear_widgets()

            if not entries:
                self.status_label.text = "❌ No Wi-Fi networks found."
                return

            self.status_label.text = "📶 Available Wi-Fi Networks:"

            for line in entries:
                ssid, signal = line.split(':', 1)
                display_name = f"{ssid} - {signal}%"
                btn = Button(text=display_name, size_hint_y=None, height=50)
                btn.bind(on_press=lambda inst, s=ssid: self.prompt_password(s))
                self.network_list.add_widget(btn)

        except Exception as e:
            self.status_label.text = f"❌ Error: {e}"
            logging.error("Wi-Fi scan error", exc_info=True)

    def prompt_password(self, ssid):
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        password_input = TextInput(password=True, hint_text="Enter Password", multiline=False)
        connect_button = Button(text="Connect")

        def do_connect(_):
            password = password_input.text.strip()
            popup.dismiss()
            self.connect_to_wifi(ssid, password)

        connect_button.bind(on_press=do_connect)
        popup_layout.add_widget(Label(text=f"🔐 Connect to: {ssid}"))
        popup_layout.add_widget(password_input)
        popup_layout.add_widget(connect_button)

        popup = Popup(title="Wi-Fi Password", content=popup_layout,
                      size_hint=(0.8, 0.5), auto_dismiss=True)
        popup.open()

    def connect_to_wifi(self, ssid, password):
        try:
            logging.info(f"Updating Wi-Fi to SSID: {ssid}")
            self.status_label.text = f"🔄 Connecting to {ssid}..."

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
            self.status_label.text = f"❌ Disconnection failed: {e}"
            logging.error("Wi-Fi disconnect failed", exc_info=True)

    def go_back(self, instance):
        if self.manager:
            self.manager.current = "menu"
