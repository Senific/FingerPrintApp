from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
import sys
import io


class StreamCapture(io.TextIOBase):
    def __init__(self, callback):
        self.callback = callback

    def write(self, text):
        if text.strip():
            self.callback(text.strip())

    def flush(self):
        pass


class LogScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.log_lines = []

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        self.scroll = ScrollView(size_hint=(1, 0.9))

        self.label = Label(
            text='',
            markup=True,
            font_size='13sp',
            halign='left',
            valign='top',
            size_hint=(None, None)
        )

        self.label.bind(texture_size=self.update_height)
        self.scroll.bind(width=self.update_label_width)

        self.scroll.add_widget(self.label)
        layout.add_widget(self.scroll)

        back_button = Button(text="Back", size_hint=(1, 0.1))
        back_button.bind(on_release=self.go_back)
        layout.add_widget(back_button)

        self.add_widget(layout)

        # Redirect stdout and stderr
        sys.stdout = StreamCapture(self.add_log)
        sys.stderr = sys.stdout

        Clock.schedule_interval(self.refresh, 0.5)

    def update_height(self, *_):
        self.label.height = self.label.texture_size[1]

    def update_label_width(self, *_):
        self.label.width = self.scroll.width
        self.label.text_size = (self.scroll.width, None)

    def add_log(self, text):
        self.log_lines.append(text)
        if len(self.log_lines) > 300:
            self.log_lines = self.log_lines[-300:]

    def refresh(self, dt):
        self.label.text = "\n".join(self.colorize(line) for line in self.log_lines)
        self.scroll.scroll_y = 0  # always scroll to bottom

    def colorize(self, line: str) -> str:
        lower = line.lower()
        if "error" in lower:
            return f"[color=ff3333]❌ [ERROR] {line}[/color]"
        elif "warning" in lower:
            return f"[color=ffaa00]⚠️ [WARNING] {line}[/color]"
        elif "success" in lower or "complete" in lower or "done" in lower:
            return f"[color=33ff33]✅ [SUCCESS] {line}[/color]"
        elif "info" in lower or "[base" in lower:
            return f"[color=66ccff]ℹ️ [INFO] {line}[/color]"
        elif "token" in lower:
            return f"[color=cccccc]🔐 {line}[/color]"
        else:
            return f"[color=ffffff]{line}[/color]"

    def go_back(self, instance):
        self.manager.current = 'menu'
