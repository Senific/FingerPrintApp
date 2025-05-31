from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
import subprocess
import logging

class WifiListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_connection = None
        self.networks = {}
        self.layout = BoxLayout(orientation='vertical')

        # Scrollable network list
        self.scroll = ScrollView(size_hint=(1, 0.85))
        self.network_list_layout = BoxLayout(orientation='vertical', size_hint_y=None)
        self.network_list_layout.bind(minimum_height=self.network_list_layout.setter('height'))
        self.scroll.add_widget(self.network_list_layout)
        self.layout.add_widget(self.scroll)

        # Control buttons
        control_layout = BoxLayout(size_hint=(1, 0.15))
        disconnect_btn = Button(text="Disconnect")
        disconnect_btn.bind(on_press=self.disconnect_wifi)
        control_layout.add_widget(disconnect_btn)

        back_btn = Button(text="Back to Menu")
        back_btn.bind(on_press=self.go_back)
        control_layout.add_widget(back_btn)

        self.layout.add_widget(control_layout)
        self.add_widget(self.layout)

        Clock.schedule_interval(self.refresh_wifi_list, 1)

    def refresh_wifi_list(self, dt):
        try:
            # Get current connection
            output = subprocess.check_output(["nmcli", "-t", "-f", "NAME,DEVICE", "connection", "show", "--active"]).decode()
            self.current_connection = None
            for line in output.strip().split('\n'):
                if "wlan0" in line:
                    self.current_connection = line.split(":")[0]
                    break

            # Get all visible networks
            output = subprocess.check_output(['nmcli', '-t', '-f', 'SSID,SIGNAL', 'device', 'wifi', 'list']).decode()
            new_networks = {}
            for line in output.strip().split('\n'):
                if not line:
                    continue
                parts = line.split(':')
                if len(parts) >= 2:
                    ssid = parts[0].strip()
                    signal = parts[1].strip()
                    new_networks[ssid] = signal

            if new_networks != self.networks:
                self.network_list_layout.clear_widgets()
                for ssid, signal in new_networks.items():
                    is_connected = (ssid == self.current_connection)
                    btn = Button(
                        text=f"{ssid} ({signal}%)" + (" [Connected]" if is_connected else ""),
                        size_hint_y=None,
                        height=50,
                        background_color=(0.2, 0.6, 0.2, 1) if is_connected else (1, 1, 1, 1),
                        color=(0, 0, 0, 1)
                    )
                    btn.bind(on_press=lambda instance, s=ssid, c=is_connected: self.handle_network_click(s, c))
                    self.network_list_layout.add_widget(btn)

                self.networks = new_networks

        except Exception as e:
            logging.error(f"Failed to refresh Wi-Fi list: {e}")

    def handle_network_click(self, ssid, is_connected):
        if is_connected:
            self.show_disconnect_popup(ssid)
        else:
            self.show_connect_popup(ssid)

    def show_connect_popup(self, ssid):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        password_input = TextInput(hint_text="Enter password", password=True)
        connect_btn = Button(text="Connect")

        def on_connect(_):
            password = password_input.text.strip()
            if not password:
                self.show_message("Error", "Password cannot be empty.")
                return

            try:
                subprocess.check_call([
                    "nmcli", "device", "wifi", "connect", ssid,
                    "password", password, "name", "SenificWiFi"
                ])
                self.show_message("Success", f"Connected to {ssid}")
            except subprocess.CalledProcessError as e:
                self.show_message("Error", f"Failed to connect: {e}")
            popup.dismiss()

        connect_btn.bind(on_press=on_connect)
        content.add_widget(password_input)
        content.add_widget(connect_btn)

        popup = Popup(title=f"Connect to {ssid}", content=content, size_hint=(0.8, 0.4))
        popup.open()

    def show_disconnect_popup(self, ssid):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)
        message = Label(text=f"Disconnect from {ssid}?")
        disconnect_btn = Button(text="Yes, Disconnect")

        def on_disconnect(_):
            try:
                subprocess.check_call(["nmcli", "connection", "down", "SenificWiFi"])
                self.show_message("Disconnected", f"{ssid} has been disconnected.")
            except subprocess.CalledProcessError as e:
                self.show_message("Error", f"Failed to disconnect: {e}")
            popup.dismiss()

        disconnect_btn.bind(on_press=on_disconnect)
        content.add_widget(message)
        content.add_widget(disconnect_btn)

        popup = Popup(title="Disconnect?", content=content, size_hint=(0.8, 0.3))
        popup.open()

    def disconnect_wifi(self, instance):
        try:
            subprocess.check_call(["nmcli", "connection", "down", "SenificWiFi"])
            self.show_message("Success", "Disconnected successfully.")
        except subprocess.CalledProcessError as e:
            self.show_message("Error", f"Failed to disconnect: {e}")

    def show_message(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        content.add_widget(Label(text=message))
        ok_btn = Button(text="OK", size_hint_y=None, height=40)
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        ok_btn.bind(on_press=popup.dismiss)
        content.add_widget(ok_btn)
        popup.open()

    def go_back(self, instance):
        if self.manager:
            self.manager.current = "menu"
