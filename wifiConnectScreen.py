import os
import logging
from subprocess import run, CalledProcessError
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput


class WifiConnectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        self.ssid_input = TextInput(
            hint_text="Wi-Fi SSID",
            multiline=False,
            size_hint=(0.8, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.7},
            text="Kasun'iphone"
        )
        layout.add_widget(self.ssid_input)

        self.pass_input = TextInput(
            hint_text="Password",
            multiline=False,
            password=True,
            size_hint=(0.8, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.55},
            text='K255#1345'
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
            self.status_label.text = "Updating Wi-Fi config..."
            logging.info(self.status_label.text)
            self.update_wifi_config(ssid, password)

            self.status_label.text = "Restarting Wi-Fi (nmcli)..."
            logging.info(self.status_label.text)

            # Connect using NetworkManager (nmcli)
            run(["sudo", "nmcli", "device", "wifi", "connect", ssid, "password", password], check=True)

            self.status_label.text = f"✅ Connected to {ssid}"
            logging.info(f"Wi-Fi connected to {ssid}")

        except CalledProcessError as e:
            self.status_label.text = f"❌ Failed to connect: {e}"
            logging.error(f"Wi-Fi reconnect error: {e}")
        except Exception as e:
            self.status_label.text = f"Error: {e}"
            logging.error("Wifi Connect Exception:")
            logging.exception(e)

    def update_wifi_config(self, ssid, password):
        import logging
        import os

        config_path = "/etc/wpa_supplicant/wpa_supplicant.conf"
        tmp_path = "/tmp/wpa_supplicant.conf.tmp"
        backup_path = "/etc/wpa_supplicant/wpa_supplicant.conf.bak"

        # Read current config
        try:
            with open(config_path, "r") as f:
                content = f.read()
        except FileNotFoundError:
            logging.warning("No existing wpa_supplicant.conf found. Creating a new one.")
            content = "ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=US\n"

        # Check if the SSID already exists (case-insensitive)
        if f'ssid="{ssid}"' in content:
            logging.info(f"SSID '{ssid}' already exists in config. Skipping add.")
            return

        logging.info("Backing up existing config...")
        run(["sudo", "cp", config_path, backup_path], check=False)

        # Append new network block
        network_block = f'''
    network={{
        ssid="{ssid}"
        psk="{password}"\n}}''' if password else f'''
    network={{
        ssid="{ssid}"
        key_mgmt=NONE\n}}'''

        new_content = content.strip() + "\n" + network_block + "\n"

        with open(tmp_path, "w") as f:
            f.write(new_content)

        # Replace the original file with the updated one
        run(["sudo", "mv", tmp_path, config_path], check=True)

        logging.info("✅ wpa_supplicant.conf updated successfully.")


    def go_back(self, instance):
        if self.manager:
            self.manager.current = "menu"
