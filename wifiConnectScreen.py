from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition, FloatLayout 
from kivy.app import App 
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.window import Window
from subprocess import run, CalledProcessError

Window.size = (480, 320)
Window.fullscreen = False

class WifiConnectScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Use a layout inside this screen
        layout = FloatLayout()

        # SSID Input
        self.ssid_input = TextInput(
            hint_text="Wi-Fi SSID",
            multiline=False,
            size_hint=(0.8, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.7},
        )
        self.add_widget(self.ssid_input)

        # Password Input
        self.pass_input = TextInput(
            hint_text="Password",
            multiline=False,
            password=True,
            size_hint=(0.8, 0.1),
            pos_hint={"center_x": 0.5, "center_y": 0.55},
        )
        self.add_widget(self.pass_input)

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
        self.add_widget(self.status_label)

        # Connect Button
        connect_btn = Button(
            text="Connect Wi-Fi",
            size_hint=(0.5, 0.15),
            pos_hint={"center_x": 0.5, "center_y": 0.25},
        )
        connect_btn.bind(on_press=self.connect_wifi)
        self.add_widget(connect_btn)

    def _update_text_size(self, instance, value):
        instance.text_size = instance.size

    def connect_wifi(self, instance):
        ssid = self.ssid_input.text.strip()
        password = self.pass_input.text.strip()

        if not ssid:
            self.status_label.text = "SSID cannot be empty"
            return

        # Update wpa_supplicant.conf
        try:
            self.status_label.text = "Updating Wi-Fi config..."
            self.update_wifi_config(ssid, password)
            self.status_label.text = "Wi-Fi config updated. Restarting interface..."

            # Restart Wi-Fi interface (may require sudo)
            run(["sudo", "wpa_cli", "-i", "wlan0", "reconfigure"], check=True)

            self.status_label.text = "Wi-Fi connected (or reconnecting)."
        except CalledProcessError as e:
            self.status_label.text = f"Failed to restart Wi-Fi: {e}"
        except Exception as e:
            self.status_label.text = f"Error: {e}"

    def update_wifi_config(self, ssid, password):
        # Backup old config
        run(["sudo", "cp", "/etc/wpa_supplicant/wpa_supplicant.conf", "/etc/wpa_supplicant/wpa_supplicant.conf.bak"], check=True)

        # Construct new network block
        network_block = '\nnetwork={\n'
        network_block += f'    ssid="{ssid}"\n'
        if password:
            network_block += f'    psk="{password}"\n'
        else:
            network_block += '    key_mgmt=NONE\n'  # open network
        network_block += '}\n'

        # Read current file, append new network block at end
        with open("/etc/wpa_supplicant/wpa_supplicant.conf", "r") as f:
            content = f.read()

        if "network={" in content:
            # Naive approach: append new network block at the end
            new_content = content.strip() + network_block
        else:
            # No network block? Just add it.
            new_content = content + network_block

        # Write back
        with open("/tmp/wpa_supplicant.conf.tmp", "w") as f:
            f.write(new_content)

        # Move temp file to original with sudo
        run(["sudo", "mv", "/tmp/wpa_supplicant.conf.tmp", "/etc/wpa_supplicant/wpa_supplicant.conf"], check=True)

class WifiApp(App):
    def build(self):
        return WifiConnectScreen()

if __name__ == "__main__":
    WifiApp().run()
