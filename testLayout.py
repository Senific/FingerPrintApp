from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle

class TestLayout(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(1, 0, 0, 1)
            Rectangle(pos=(0, 0), size=(480, 40))  # Red footer block

        self.add_widget(Label(
            text="Bottom Label",
            pos_hint={'x': 0, 'y': 0},
            size_hint=(1, None),
            height=30,
            color=(1, 1, 1, 1),
            font_size='20sp'
        ))

class TestApp(App):
    def build(self):
        return TestLayout()

TestApp().run()
