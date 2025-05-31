import logging
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from subprocess import run, CalledProcessError, PIPE

PROFILE_NAME = "SenificWiFi"

class WifiConnectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        self.ssid_input = TextInput(
            hint_text="Wi-Fi SSID",
            multiline=False,
            size_hint=(0.8, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.7},
            text="Kasun’s iPhone"
        )
        layout.add_widget(self.ssid_input)

        self.pass_input = TextInput(
            hint_text="Password",
            multiline=False,
            password=True,
            size_hint=(0.8, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.55},
            text="K255#1345"
        )
        layout.add_widget(self.pass_input)

        self.status_label = Label(
            text="",
            size_hint=(0.8, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.4},
            color=(1, 0, 0, 1),
            halign='center',
            valign='middle'
        )
        self.status_label.bind(size=self._update_text_size)
        layout.add_widget(self.status_label)

        connect_btn = Button(
            text="Connect Wi-Fi",
            size_hint=(0.5, 0.15),
            pos_hint={"center_x": 0.5, "center_y": 0.25},
        )
        connect_btn.bind(on_press=self.connect_wifi)
        layout.add_widget(connect_btn)

        back_btn = Button(
            text="Back",
            size_hint=(0.5, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.12}
        )
        back_btn.bind(on_press=self.go_back)
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def _update_text_size(self, instance, value):
        instance.text_size = instance.size

    def connect_wifi(self, instance):
        ssid = self.ssid_input.text.strip()
        password = self.pass_input.text.strip()

        if not ssid:
            self.status_label.text = "SSID cannot be empty"
            return

        try:
            self.status_label.text = "Updating Wi-Fi profile..."
            logging.info(f"Updating Wi-Fi to SSID: {ssid}")

            # Delete previous profile if exists
            run(["nmcli", "connection", "delete", PROFILE_NAME], stdout=PIPE, stderr=PIPE)

            # Create and connect with new profile
            run([
                "nmcli", "device", "wifi", "connect", ssid,
                "password", password,
                "name", PROFILE_NAME
            ], check=True)

            # Set autoconnect and higher priority
            run(["nmcli", "connection", "modify", PROFILE_NAME, "connection.autoconnect", "yes"], check=True)
            run(["nmcli", "connection", "modify", PROFILE_NAME, "connection.autoconnect-priority", "10"], check=True)

            self.status_label.text = f"✅ Connected to {ssid}"
            logging.info(f"Connected to {ssid} via NetworkManager")

        except CalledProcessError as e:
            self.status_label.text = f"❌ Failed to connect: {e}"
            logging.error(f"nmcli error: {e}")
        except Exception as e:
            self.status_label.text = f"❌ Error: {e}"
            logging.exception("Unhandled Wi-Fi config error")

    def go_back(self, instance):
        if self.manager:
            self.manager.current = "menu"
