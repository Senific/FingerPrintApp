import os
import threading
from subprocess import run, CalledProcessError
from tkinter import Image
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        background = Image(
            source="assets/bg.jpg",
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        self.add_widget(background)

        self.btn_set_finger = Button(text="Set Finger", size_hint=(1, 0.18))
        self.btn_wifi = Button(text="Wifi", size_hint=(1, 0.18))
        self.btn_update = Button(text="Update", size_hint=(1, 0.18))
        self.btn_back = Button(text="Back", size_hint=(1, 0.18))
        
        # Status label at the bottom with small height
        self.status_label = Label(text="", size_hint=(1, 0.1))

        self.btn_set_finger.bind(on_release=self.on_set_finger)
        self.btn_wifi.bind(on_release=self.on_wifi)
        self.btn_update.bind(on_release=self.on_update)
        self.btn_back.bind(on_release=self.go_back)

        layout.add_widget(self.btn_set_finger)
        layout.add_widget(self.btn_wifi)
        layout.add_widget(self.btn_update)
        layout.add_widget(self.btn_back)
        layout.add_widget(self.status_label)  # <- moved here to bottom

        self.add_widget(layout)

    def on_pre_enter(self):
        self.status_label.text = "Version 1.0"


    def on_set_finger(self, instance):
        self.update_status("Set Finger button pressed")
        # Additional logic here...

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
            print(script_path)
            run(["/bin/bash", script_path], check=True)
            Clock.schedule_once(lambda dt: self.update_status("Update completed successfully."), 0)
        except CalledProcessError as e:
            Clock.schedule_once(lambda dt, err=e: self.update_status(f"Update failed: {err}"), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt, err=e: self.update_status(f"Error: {err}"), 0)
        finally:
            Clock.schedule_once(lambda dt: self.enable_update_button(), 0)


    def update_status(self, message):
        self.status_label.text = message

    def enable_update_button(self):
        self.btn_update.disabled = False

    def go_back(self, instance): 
        if self.manager:
            self.manager.current = 'main'
