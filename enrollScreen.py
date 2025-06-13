import os
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.app import App

from employee_sync import RUNTIME_DIR , IMAGES_DIR, ENROLLMENTS_DIR
from fplib import fplib

# fingerprint module variables
fp = fplib() 

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
        self.mark_button.bind(on_release=self.mark);
        self.back_button.bind(on_release=self.go_back)

        footer_layout.add_widget(self.enroll_button)
        footer_layout.add_widget(self.mark_button)
        footer_layout.add_widget(self.back_button)

        root_layout.add_widget(content_layout)
        root_layout.add_widget(footer_layout)

        self.add_widget(root_layout)

    def start_enrollment(self, instance):
        print("Enrollment started...")
        if fp.is_finger_pressed():
            print("\n |__ Finger is pressed")
            id, data, downloadstat = fp.enroll(idx=5)
            print(f"\n |__ ID: {id} & is captured?", data is not None)
            print(f"\n |__ enrolled count:", fp.get_enrolled_cnt())
            fp.close()

    def mark(self, instance):
        app = App.get_running_app()
        app.employee_to_enroll =  App.get_running_app().employee_to_enroll
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
    
  