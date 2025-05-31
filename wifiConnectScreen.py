from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from subprocess import run, CalledProcessError
import logging;

class WifiConnectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        # SSID Input
        self.ssid_input = TextInput(
            hint_text="Wi-Fi SSID",
            multiline=False,
            size_hint=(0.8, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.7},
            text= 'Kasun\'iphone'
        )
        layout.add_widget(self.ssid_input)

        # Password Input
        self.pass_input = TextInput(
            hint_text="Password",
            multiline=False,
            password=True,
            size_hint=(0.8, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.55},
            text= 'K255#1345'
        )
        layout.add_widget(self.pass_input)

        # Status Label
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

        # Connect Button
        connect_btn = Button(
            text="Connect Wi-Fi",
            size_hint=(0.5, 0.15),
            pos_hint={"center_x": 0.5, "center_y": 0.25},
        )
        connect_btn.bind(on_press=self.connect_wifi)
        layout.add_widget(connect_btn)

        # Back Button - just below the Connect Button
        back_btn = Button(
            text="Back",
            size_hint=(0.5, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.12}  # slightly below connect button
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
            self.status_label.text = "Wi-Fi config updated. Restarting interface..."
            logging.info(self.status_label.text)
            run(["sudo", "wpa_cli", "-i", "wlan0", "reconfigure"], check=True)

            self.status_label.text = "Wi-Fi connected (or reconnecting)."
            logging.info(self.status_label.text)
        except CalledProcessError as e:
            self.status_label.text = f"Failed to restart Wi-Fi: {e}"
        except Exception as e:
            self.status_label.text = f"Error: {e}"
            logging.error("Wifi Connect Exception:")
            logging.error(e)
            
    def update_wifi_config(self, ssid, password):
        try:
            logging.debug("📡 Starting update_wifi_config")

            # Backup
            run(["sudo", "/usr/local/bin/update_wifi.sh"], check=True)
 
            # Build config
            network_block = '\nnetwork={\n'
            network_block += f'    ssid="{ssid}"\n'
            if password:
                network_block += f'    psk="{password}"\n'
            else:
                network_block += '    key_mgmt=NONE\n'
            network_block += '}\n'

            logging.debug(f"Generated network block:\n{network_block}")

            # Read existing config
            with open("/etc/wpa_supplicant/wpa_supplicant.conf", "r") as f:
                content = f.read()
            logging.debug("✅ Read current wpa_supplicant.conf")

            if "network={" in content:
                new_content = content.strip() + network_block
            else:
                new_content = content + network_block

            # Write to temp
            with open("/tmp/wpa_supplicant.conf.tmp", "w") as f:
                f.write(new_content)
            logging.debug("✅ Temp config written")

            # Replace
            run(["sudo", "mv", "/tmp/wpa_supplicant.conf.tmp",
                "/etc/wpa_supplicant/wpa_supplicant.conf"], check=True)
            logging.debug("✅ Config moved into place")

        except Exception as e:
            logging.exception("❌ update_wifi_config failed")
            raise e  # Re-raise so the outer try block can still show status_label



 
    def go_back(self, instance):
        if self.manager:
            self.manager.current = "menu"
