import os
import sqlite3
from datetime import datetime
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
from employee_sync import DB_FILE, IMAGES_DIR
from kivy.clock import Clock

class MarkAttendanceScreen(Screen):
    def on_pre_enter(self):
        app = App.get_running_app()
        self.emp = app.employee_to_enroll
        self.sensor_triggered = getattr(app, "sensor_triggered", False)
        if self.emp:
            image_path = os.path.join(IMAGES_DIR, f"{self.emp['ID']}.jpg")
            if not os.path.exists(image_path):
                image_path = os.path.join(IMAGES_DIR, "no_photo.jpg")
            self.markedTime = datetime.now()
            self.set_details(image_path, self.emp['Name'], self.emp['Code'],self.markedTime)
          

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = FloatLayout()

        # Background
        background = Image(
            source="assets/bg3.jpg",
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        layout.add_widget(background)

        # Content Container
        content = BoxLayout(orientation='vertical', spacing=10, padding=[10, 10], size_hint=(1, 1))

        # Info Section (Image + Labels)
        info_section = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, None), height=200)

        self.image = Image(
            source="assets/nophoto.png",
            width=100, 
            allow_stretch=True,
            keep_ratio=True
        )

        labels = BoxLayout(orientation='vertical', spacing=5)
        self.name_label = Label(text="Name: ", font_size=22, halign='left', valign='middle')
        self.code_label = Label(text="Code: ", font_size=22, halign='left', valign='middle')
        self.time_label = Label(text="Time: ", font_size=22, halign='left', valign='middle')

        for lbl in [self.name_label, self.code_label, self.time_label]:
            lbl.bind(size=lbl.setter('text_size'))

        labels.add_widget(self.name_label)
        labels.add_widget(self.code_label)
        labels.add_widget(self.time_label)

        info_section.add_widget(self.image)
        info_section.add_widget(labels)

        # Buttons (aligned bottom)
        button_bar = BoxLayout(orientation='horizontal', spacing=10, size_hint=(1, None), height=40)
 

        self.mark_btn = Button(text="Mark", font_size=14)
        self.mark_btn.bind(on_release=self.mark_attendance) 

        self.back_btn = Button(text="Back", font_size=14, size_hint=(None, 1), width=80)
        self.back_btn.bind(on_release=self.go_back)
 
        button_bar.add_widget(self.mark_btn)
        button_bar.add_widget(self.back_btn)

        # Add sections
        content.add_widget(info_section)
        content.add_widget(button_bar)

        # Add content to main layout
        layout.add_widget(content)
        self.add_widget(layout)

    def set_details(self, image_path, name, code,time):
        self.image.source = image_path
        self.name_label.text = f"{name}"
        self.code_label.text = f"{code}"
        self.time_label.text =  f"{ self.markedTime.strftime('%Y-%m-%d %H:%M:%S')}"
        #self.mark_btn.disabled = self.sensor_triggered

    def mark_attendance(self, instance):
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO Attendances (Employee_ID, Code, Name, Time, State, Deleted)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (self.emp['ID'], self.emp['Code'], self.emp['Name'],  now, 'Unknown', 0)) 
            conn.commit()
            conn.close()
            print(f'✅ Attendance Marking completed for Employee { self.code_label.text }')

            if self.sensor_triggered:  
                # 🔁 Auto return after 3 seconds
                Clock.schedule_once(lambda dt: self.go_back(None), 3)
            else:
                self.go_back(instance)
        except Exception as e:
            print( f"❌ Error Marking Attendance: {str(e)}") 

    def go_back(self, instance):
        app = App.get_running_app()
        if self.manager:
            target = getattr(app, 'markAttendancePrevious_screen', 'main')
            self.manager.current = target

 