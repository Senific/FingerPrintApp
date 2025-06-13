import os
import time
import math
from functools import partial
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.app import App

from employee_sync import RUNTIME_DIR, IMAGES_DIR, ENROLLMENTS_DIR
from fplib import fplib

# fingerprint module variables
fp = fplib()
init = fp.init()
print("is initialized:", init)


class EnrollScreen(Screen):
    def on_pre_enter(self):
        emp = App.get_running_app().employee_to_enroll
        if emp:
            image_path = os.path.join(IMAGES_DIR, f"{emp['ID']}.jpg")
            if not os.path.exists(image_path):
                image_path = os.path.join(IMAGES_DIR, "no_photo.jpg")

            enrolled = self.check_enrollment_status(emp['ID'])
            self.set_employee_details(image_path, emp['Name'], emp['Code'], enrolled)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.selected_identifier = None
        self.enroll_popup = None

        root_layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        background = Image(
            source="assets/bg3.jpg",
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        self.add_widget(background)

        content_layout = BoxLayout(orientation='horizontal', spacing=20, size_hint=(1, 0.85))

        self.employee_image = Image(
            source="assets/nophoto.png",
            size_hint=(0.4, 1),
            allow_stretch=True,
            keep_ratio=True
        )

        info_layout = BoxLayout(orientation='vertical', spacing=10, size_hint=(0.6, 1))
        self.name_label = Label(text="", font_size='22sp', halign='left', valign='middle')
        self.code_label = Label(text="", font_size='22sp', halign='left', valign='middle')
        self.status_label = Label(text="", font_size='20sp', halign='left', valign='middle')

        for label in (self.name_label, self.code_label, self.status_label):
            label.bind(size=lambda inst, val: inst.setter('text_size')(inst, val))

        info_layout.add_widget(self.name_label)
        info_layout.add_widget(self.code_label)
        info_layout.add_widget(self.status_label)

        content_layout.add_widget(self.employee_image)
        content_layout.add_widget(info_layout)

        footer_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, 0.15))
        self.enroll_button = Button(text="Start Enrollment")
        self.mark_button = Button(text="Go To Mark")
        self.back_button = Button(text="Back", size_hint=(0.3, 1))

        self.enroll_button.bind(on_release=self.start_enrollment)
        self.mark_button.bind(on_release=self.mark)
        self.back_button.bind(on_release=self.go_back)

        footer_layout.add_widget(self.enroll_button)
        footer_layout.add_widget(self.mark_button)
        footer_layout.add_widget(self.back_button)

        root_layout.add_widget(content_layout)
        root_layout.add_widget(footer_layout)

        self.add_widget(root_layout)

    def start_enrollment(self, instance):
        emp = App.get_running_app().employee_to_enroll
        # if not emp or not emp.get('Identifiers'):
        #     print("No Identifiers found for this employee.")
        #     return

        identifiers = "1,2,3".split(",")  # test with many buttons

        count = len(identifiers)

        # Smart columns: square root logic
        columns = max(1, math.ceil(math.sqrt(count)))

        print(f"Identifiers count = {count}, smart columns = {columns}")

        # Build GridLayout
        grid = GridLayout(cols=columns, spacing=10, padding=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        for identifier in identifiers:
            btn = Button(text=f"{identifier}", size_hint_y=None, height=50)
            btn.bind(on_release=partial(self.identifier_selected, identifier))
            grid.add_widget(btn)

        # Wrap in ScrollView
        scrollview = ScrollView(size_hint=(1, 1))
        scrollview.add_widget(grid)

        # Create full content layout (ScrollView + Cancel button)
        popup_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        popup_layout.add_widget(scrollview)

        # Cancel button pinned at bottom
        close_btn = Button(text="Cancel", size_hint=(1, None), height=50)
        close_btn.bind(on_release=lambda instance: self.enroll_popup.dismiss())
        popup_layout.add_widget(close_btn)

        # Create Popup
        self.enroll_popup = Popup(title="Select Identifier to Enroll",
                                  content=popup_layout,
                                  size_hint=(0.8, 0.8),
                                  auto_dismiss=False)

        # Open popup
        self.enroll_popup.open()

    def identifier_selected(self, identifier, instance=None):
        print(f"Selected Identifier: {identifier}")
        self.selected_identifier = identifier
        self.enroll_popup.dismiss()

        # Now proceed with Enrollment logic using selected_identifier
        print("Enrollment started...")

        led = fp.set_led(True)
        print("\n |__ LED status:", led)
        time.sleep(2)
        led = fp.set_led(False)
        print("\n |__ LED status:", led)

        # Example - You can pass this identifier to enroll:
        # id, data, downloadstat = fp.enroll(idx=int(identifier))
        # print(f"\n |__ ID: {id} & is captured?", data is not None)

        fp.close()

    def mark(self, instance):
        app = App.get_running_app()
        app.employee_to_enroll = App.get_running_app().employee_to_enroll
        app.markAttendancePrevious_screen = "enroll"
        self.manager.current = "mark"

    def go_back(self, instance):
        app = App.get_running_app()
        if self.manager:
            target = getattr(app, 'previous_screen', 'main')  # default to 'main'
            self.manager.current = target

    def set_employee_details(self, image_path, name, code, enrolled):
        self.employee_image.source = image_path
        self.name_label.text = f"{name}"
        self.code_label.text = f"{code}"
        self.status_label.text = "✅ Enrolled" if enrolled else "❌ Not Enrolled"

    def check_enrollment_status(self, emp_id: int) -> bool:
        return os.path.exists(os.path.join(ENROLLMENTS_DIR, f"{emp_id}.jpg"))
