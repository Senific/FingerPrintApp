from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        btn_set_finger = Button(text="Set Finger", size_hint=(1, 0.2))
        btn_wifi = Button(text="Wifi", size_hint=(1, 0.2))
        btn_update = Button(text="Update", size_hint=(1, 0.2))
        btn_back = Button(text="Back", size_hint=(1, 0.2))
        
        btn_back.bind(on_release=self.go_back)
        
        layout.add_widget(btn_set_finger)
        layout.add_widget(btn_wifi)
        layout.add_widget(btn_update)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def on_set_finger(self, instance):
        print("Set Finger button pressed")
        # Here you can switch to fingerprint setup screen or any other action

    def on_wifi(self, instance):
        print("Wifi button pressed")
        # Switch to wifi screen, for example:
        self.manager.current = 'wifi'

    def on_update(self, instance):
        print("Update button pressed")
        # Handle update logic here

    def go_back(self, instance):
    # Switch back to IdleScreen
        if self.manager:
            self.manager.current = 'main'
