from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock, mainthread
from kivy.uix.image import Image
from employee_sync import get_api_config,RUNTIME_DIR, SETTINGS_FILE, FERNET_KEY_FILE, DB_FILE, LAST_SYNC_FILE
import os
import json
from cryptography.fernet import Fernet
import httpx
import threading
import shutil

def get_or_create_fernet():
    if not os.path.exists(FERNET_KEY_FILE):
        key = Fernet.generate_key()
        with open(FERNET_KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(FERNET_KEY_FILE, "rb") as f:
            key = f.read()
    return Fernet(key)

fernet = get_or_create_fernet()

def save_settings(system_code, username, password):
    encrypted_pw = fernet.encrypt(password.encode()).decode()
    data = {
        "system_code": system_code,
        "username": username,
        "password": encrypted_pw
    }
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            data["password"] = fernet.decrypt(data["password"].encode()).decode()
            return data
    return get_api_config()

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        background = Image(
            source="assets/bg3.jpg",
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        self.add_widget(background)

        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        form_layout = GridLayout(cols=2, spacing=10, size_hint=(1, 0.6))

        self.system_code_input = TextInput(multiline=False)
        self.username_input = TextInput(multiline=False)
        self.password_input = TextInput(password=True, multiline=False)

        form_layout.add_widget(Label(text="System Code:", halign="right"))
        form_layout.add_widget(self.system_code_input)

        form_layout.add_widget(Label(text="Username:", halign="right"))
        form_layout.add_widget(self.username_input)

        form_layout.add_widget(Label(text="Password:", halign="right"))
        form_layout.add_widget(self.password_input)

        layout.add_widget(form_layout)

        self.feedback_label = Label(size_hint=(1, 0.1))
        layout.add_widget(self.feedback_label)

        button_box = BoxLayout(size_hint=(1, 0.2), spacing=20)
        self.save_button = Button(text="Save")
        self.back_button = Button(text="Back")
        self.back_button.disabled = not os.path.exists(SETTINGS_FILE)

        self.save_button.bind(on_release=self.save_credentials)
        self.back_button.bind(on_release=self.go_back)

        button_box.add_widget(self.save_button)
        button_box.add_widget(self.back_button)

        layout.add_widget(button_box)
        self.add_widget(layout)

        Clock.schedule_once(lambda dt: self.load_values(), 0.1)

    def load_values(self):
        try:
            settings = load_settings()
            self.system_code_input.text = settings.get("system_code", "")
            self.username_input.text = settings.get("username", "")
            self.password_input.text = settings.get("password", "")
        except Exception:
            pass

    def save_credentials(self, instance):
        self.feedback_label.text = "Validating credentials..."
        system_code = self.system_code_input.text.strip()
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()

        threading.Thread(target=self.validate_and_save, args=(system_code, username, password), daemon=True).start()

    def validate_and_save(self, system_code, username, password):
        url = "https://poca.senific.com/token"
        headers = {
            "SystemCode": system_code,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "password",
            "username": username,
            "password": password
        }

        try:
            response = httpx.post(url, headers=headers, data=data, timeout=10)
            self.process_validation_result(response, system_code, username, password)
        except Exception as e:
            self.update_feedback(False, f"❌ Error: {str(e)}")

    @mainthread
    def process_validation_result(self, response, system_code, username, password):
        if response.status_code == 200:
            save_settings(system_code, username, password)
            self.update_feedback(True, "✅ Settings saved successfully, Restarting...")
            threading.Thread(target=lambda: os.system("sudo reboot")).start()
        else:
            self.update_feedback(False, "❌ Invalid credentials")

    @mainthread
    def update_feedback(self, success, message):
        self.feedback_label.text = message
        self.back_button.disabled = not success

    def perform_reset(self, popup):
        popup.dismiss()
        try:   
            # Delete specific files if they exist
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
            if os.path.exists(LAST_SYNC_FILE):
                os.remove(LAST_SYNC_FILE)

            # Delete the whole RuntimeResources directory
            if os.path.exists(RUNTIME_DIR):
                shutil.rmtree(RUNTIME_DIR)
 
            threading.Thread(target=lambda: os.system("sudo reboot")).start()
        except Exception as e:
            self.update_status(f"❌ Reset error: {e}")
        

    def go_back(self, instance):
        self.manager.current = "menu"
