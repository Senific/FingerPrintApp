# popups.py
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout

class PopupUtils:
    status_popup:Popup = None
    status_lable:Label = None
    status_image:Image = None 

    @staticmethod
    def show_message_popup(message: str, title="Error"):
        error_label = Label(
            text=message,
            font_size='16sp',
            halign='center',
            valign='middle',
            size_hint=(1, None),
            height=80
        )
        error_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

        ok_btn = Button(text="OK", size_hint=(1, None), height=50)

        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(error_label)
        layout.add_widget(ok_btn)

        popup = Popup(
            title=title,
            content=layout,
            size_hint=(0.8, None),
            height=200,
            auto_dismiss=False
        )

        ok_btn.bind(on_release=popup.dismiss)
        popup.open()

    @staticmethod
    def show_confirm_popup(message: str, title="Confirm", yesCallback = None, NoCallback = None ):
        confirm_layout = BoxLayout(orientation='vertical', spacing=10, padding=20)

        confirm_label = Label(
            text=message,
            font_size='18sp',
            halign='center',
            valign='middle',
            size_hint=(1, None),
            height=100
        )
        confirm_label.bind(size=lambda inst, val: setattr(inst, 'text_size', val))
        confirm_layout.add_widget(confirm_label)

        btn_layout = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=None, height=50)
        yes_btn = Button(text="Yes")
        no_btn = Button(text="No")

        btn_layout.add_widget(yes_btn)
        btn_layout.add_widget(no_btn)
        confirm_layout.add_widget(btn_layout)

        confirm_popup = Popup(
            title="",
            content=confirm_layout,
            size_hint=(1, 1),
            auto_dismiss=False
        )

        def on_no_pressed(inst):
            if NoCallback is not None:
                NoCallback()
            confirm_popup.dismiss()
        def on_yes_pressed(inst): 
            if yesCallback is not None:
                yesCallback()
            confirm_popup.dismiss()
        yes_btn.bind(on_release=lambda inst: on_yes_pressed(inst) )
        no_btn.bind(on_release=lambda inst: on_no_pressed(inst) )

        confirm_popup.open()

    @staticmethod
    def dismiss_status_popup():
        if PopupUtils.status_popup is not None:
            PopupUtils.status_popup.dismiss()
    @staticmethod
    def show_status_popup():
            PopupUtils.status_lable = Label(
                text="Starting enrollment...",
                font_size='18sp',
                halign='center',
                valign='middle',
                size_hint=(1, None),
                height=40
            )
            PopupUtils.status_lable.bind(size=lambda inst, val: setattr(inst, 'text_size', val))

            PopupUtils.status_image = Image(
                source="assets/finger.png",  # default image
                size_hint=(None, None),
                size=(100, 100),
                allow_stretch=True,
                keep_ratio=True,
                opacity=1
            )

            # Wrap both in a vertical layout
            status_content = BoxLayout(orientation='vertical', spacing=20, size_hint=(1, 1), padding=40)
            status_content.add_widget(PopupUtils.status_lable)

            # Add a container to center the image
            image_wrapper = BoxLayout(orientation='horizontal', size_hint=(1, None), height=120)
            image_wrapper.add_widget(Label(size_hint=(0.5, 1)))  # Left spacer
            image_wrapper.add_widget(PopupUtils.status_image)
            image_wrapper.add_widget(Label(size_hint=(0.5, 1)))  # Right spacer

            status_content.add_widget(image_wrapper)

            PopupUtils.status_popup = Popup(
                title='Enrollment',
                content=status_content,
                size_hint=(1, 1),
                auto_dismiss=False
            )
            PopupUtils.status_popup.open()
    @staticmethod
    def update_status_popup(msg, img_code):
        PopupUtils.status_lable.text = msg 
        if img_code == 0:
            PopupUtils.status_image.source = "assets/loading.png"
        if img_code == 1:
            PopupUtils.status_image.source = "assets/fail.png"
        if img_code == 2:
            PopupUtils.status_image.source = "assets/success.png"            
        if img_code == 3:
            PopupUtils.status_image.source = "assets/finger.png"            
        if img_code == 4:
            PopupUtils.status_image.source = "assets/uploading.png"            
        if img_code == 5:
            PopupUtils.status_image.source = "assets/delete.png"            


    @staticmethod
    def update_status_popup_threadsafe(msg, imageCode):
        Clock.schedule_once(lambda dt: PopupUtils.update_status_popup(msg, imageCode))

         