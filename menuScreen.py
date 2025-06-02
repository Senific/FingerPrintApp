import os
import threading
from subprocess import run, CalledProcessError

from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout as KivyBoxLayout


import shutil
import threading


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        background = Image(
            source="assets/bg3.jpg",
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        self.add_widget(background)

        button_grid = GridLayout(cols=2, spacing=10, size_hint=(1, 0.8))
 
        self.btn_wifi = Button(text="WiFi")
        self.btn_update = Button(text="Update")
        self.btn_restart = Button(text="Restart")
        self.btn_shutdown = Button(text="Shutdown")
        self.btn_logs = Button(text="Logs") 
        self.btn_settings = Button(text="Settings")
        self.btn_list = Button(text="List")  # ✅ New Button
        self.btn_back = Button(text="Back")

        self.status_label = Label(text="", size_hint=(1, 0.1))

        # Bind actions 
        self.btn_wifi.bind(on_release=self.on_wifi)
        self.btn_update.bind(on_release=self.on_update)
        self.btn_restart.bind(on_release=self.on_restart)
        self.btn_shutdown.bind(on_release=self.on_shutdown)
        self.btn_logs.bind(on_release=self.on_logs) 
        self.btn_settings.bind(on_release=self.on_settings)
        self.btn_list.bind(on_release=self.on_list)  # ✅ New Binding
        self.btn_back.bind(on_release=self.go_back)

        # Add buttons in desired order 
        button_grid.add_widget(self.btn_wifi)
        button_grid.add_widget(self.btn_update)
        button_grid.add_widget(self.btn_restart)
        button_grid.add_widget(self.btn_shutdown)
        button_grid.add_widget(self.btn_logs) 
        button_grid.add_widget(self.btn_settings)
        button_grid.add_widget(self.btn_list)     # ✅ New Placement
        button_grid.add_widget(self.btn_back)

        root_layout.add_widget(button_grid)
        root_layout.add_widget(self.status_label)

        self.add_widget(root_layout)

    def on_pre_enter(self):
        self.status_label.text = "Version 1.4"
 

    def on_wifi(self, instance):
        self.manager.current = 'wifi'

    def on_update(self, instance):
        self.btn_update.disabled = True
        self.update_status("Running update script...")
        threading.Thread(target=self.run_update_script).start()

    def run_update_script(self):
        try:
            app_dir = os.path.dirname(os.path.abspath(__file__))
            script_path = os.path.join(app_dir, "update.sh")
            run(["/bin/bash", script_path], check=True)
            Clock.schedule_once(lambda dt: self.update_status("Update completed successfully."), 0)
        except CalledProcessError as e:
            Clock.schedule_once(lambda dt: self.update_status(f"Update failed: {e}"), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_status(f"Error: {e}"), 0)
        finally:
            Clock.schedule_once(lambda dt: self.enable_update_button(), 0)

    def update_status(self, message):
        self.status_label.text = message

    def enable_update_button(self):
        self.btn_update.disabled = False

    def on_restart(self, instance):
        self.update_status("Restarting...")
        threading.Thread(target=lambda: os.system("sudo reboot")).start()

    def on_shutdown(self, instance):
        self.update_status("Shutting down...")
        threading.Thread(target=lambda: os.system("sudo poweroff")).start()

    def on_logs(self, instance):
        if self.manager:
            self.manager.current = 'logs'

    def on_settings(self, instance):
        if self.manager:
            self.manager.current = 'settings'

    def on_list(self, instance):  # ✅ New Method
        if self.manager:
            self.manager.current = 'list'

    def go_back(self, instance):
        if self.manager:
            self.manager.current = 'main'
 
