import asyncio
import logging
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
from kivy.clock import Clock
from asyncio import get_event_loop
from employee_sync import RUNTIME_DIR, IMAGES_DIR, fp
from fplib import fplib
from popups import PopupUtils
from helper import HelperUtils
from apiUtill import ApiUtils  
import employee_sync

class EnrollScreen(Screen): 
    fp : fplib = None
    def on_pre_enter(self):
        emp = App.get_running_app().employee_to_enroll  
        if emp:
            image_path = os.path.join(IMAGES_DIR, f"{emp['ID']}.jpg")
            if not os.path.exists(image_path):
                image_path = os.path.join(IMAGES_DIR, "no_photo.jpg")
 
            self.set_employee_details(image_path, emp['Name'], emp['Code'], emp['Identifiers'])

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
        if not emp or not emp.get('Identifiers'):
            PopupUtils.show_message_popup( "No Identifiers Found!")
            return
 
        identifiers = emp.get('Identifiers').split(",")  # test with many buttons
        count = len(identifiers)

        # Smart columns: square root logic
        columns = max(1, math.ceil(math.sqrt(count)))

        print(f"Identifiers count = {count}, smart columns = {columns}")

        # Build GridLayout
        grid = GridLayout(cols=columns, spacing=10, padding=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))

        for identifier in identifiers:
            id_int = int(identifier)
            is_enrolled = fp.check_enrolled(id_int)

            btn = Button(
                text=f"{identifier}",
                size_hint_y=None,
                height=50,
                background_color=(0, 1, 0, 1) if is_enrolled else (1, 1, 1, 1)  # green if enrolled
            )

            btn.bind(on_release=partial(
                self.identifier_selected, identifier, is_enrolled))

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
                                  size_hint=(1, 1),
                                  auto_dismiss=False)

        # Open popup
        self.enroll_popup.open()

    def identifier_selected(self, identifier, is_enrolled, instance=None):
        self.selected_identifier = identifier

        if is_enrolled:
            # Show confirmation popup first without dismissing enroll_popup
            def yesCallback(): 
                PopupUtils.show_status_popup()
                Clock.schedule_once(lambda dt: asyncio.ensure_future(self.deleteConfirmed(identifier)))
                  
            PopupUtils.show_confirm_popup(message= f"Delete Enrollment for identifier {identifier}?",  yesCallback = yesCallback )
        else: 
            PopupUtils.show_status_popup()
            Clock.schedule_once(lambda dt: asyncio.ensure_future(self.perform_enroll(identifier)))

    async def deleteConfirmed(self,identifier): 
        try:
            PopupUtils.update_status_popup("Deleting Enrollment...",5)
            await asyncio.sleep(1)
            await ApiUtils.delete_fingerprint_template(identifier) 
            result = fp.delete(idx=int(identifier))     
            self.enroll_popup.dismiss()
            self.on_pre_enter()
            if result:
                  PopupUtils.update_status_popup("Deleted Successfully",2)
            else:
                PopupUtils.update_status_popup("Delete Failed!",1)
        except Exception as e:
            PopupUtils.update_status_popup("Delete Failed! Check Your Internet",1) 
        await asyncio.sleep(2)
        PopupUtils.dismiss_status_popup()        
 
    enrolling_in_progress = False
 
    async def touch_callback(self, touched):
        if self.enrolling_in_progress == True:
            return

        if touched == True:
            PopupUtils.update_status_popup("Checking", 0)
            if fp.is_finger_pressed():
                idx, data, downloadstatus = await asyncio.to_thread(lambda: asyncio.run( fp.enroll(self.enrollStatus_Callback, idx = int(id))))
                if idx >= 0: 
                    data,status =  fp.get_template(idx)
                    try:
                        PopupUtils.update_status_popup("Uploading...", 4)
                        asyncio.sleep(1)
                        await ApiUtils.upload_fingerprint_template(idx, data)
                        PopupUtils.update_status_popup("Successfully Enrolled!", 2)
                    except Exception as e:
                        logging.error(e)
                        PopupUtils.update_status_popup("Failed while uploading!", 1)
                        fp.delete(idx) 
                        
                        
                    self.enrolling_in_progress = False
                    self.enroll_popup.dismiss()
                    self.on_pre_enter()
                else:  
                    PopupUtils.update_status_popup("Enrolling Failed!", 1)
                await asyncio.sleep(2)
            else: 
                PopupUtils.update_status_popup("Enrolling Failed!", 1)
                await asyncio.sleep(2) 
            
            employee_sync.on_touch_callback = self.touch_callback 
            self.enrolling_in_progress = False
            PopupUtils.dismiss_status_popup()
    

    async def perform_enroll(self, id): 
        PopupUtils.update_status_popup("Please place finger...", 3)
        employee_sync.on_touch_callback = self.touch_callback 
        print("Touch callback Added")
        await asyncio.sleep(10)
        PopupUtils.dismiss_status_popup()
       
         
     
    def enrollStatus_Callback(self, msg):
        def update_label(dt): 
            PopupUtils.update_status_popup(msg,0)
            #self.status_label_widget.text = msg 
            #self.status_label_widget.canvas.ask_update()
        logging.info(msg)
        Clock.schedule_once(update_label)  # ✅ Just pass the function, not call it
 
 
 
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

    def set_employee_details(self, image_path, name, code, identifiersStr):
        self.employee_image.source = image_path
        self.name_label.text = f"{name}"
        self.code_label.text = f"{code}"

        status,msg = HelperUtils.check_enrollment_status(fp,identifiersStr)
        self.status_label.text = msg
 

     