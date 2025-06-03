import os
import aiosqlite
import asyncio
from threading import Thread

from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from employee_sync import RUNTIME_DIR


class AttendancesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.all_attendances = []

        main_layout = BoxLayout(orientation='vertical', spacing=5)

        # 📜 Scrollable Attendance List
        self.scroll = ScrollView(size_hint=(1, 0.9))
        self.layout = GridLayout(cols=1, spacing=1, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.scroll.add_widget(self.layout)

        # 🔙 Back Button
        self.back_button = Button(
            text="Back",
            size_hint=(1, 0.1),
            on_press=self.go_back
        )

        main_layout.add_widget(self.scroll)
        main_layout.add_widget(self.back_button)

        self.add_widget(main_layout)

    def go_back(self, instance): 
        self.manager.current = "menu"

    def on_enter(self):
        Thread(target=self.populate_attendances).start()

    def populate_attendances(self):
        attendances = asyncio.run(self.fetch_attendances())
        self.all_attendances = attendances
        Clock.schedule_once(lambda dt: self.update_ui(attendances))

    async def fetch_attendances(self):
        db_path = os.path.join(RUNTIME_DIR, "employees.db")
        records = []
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("""
                SELECT Code, Name, Time
                FROM Attendances
                WHERE DELETED = 0
                ORDER BY Time DESC
            """) as cursor:
                async for row in cursor:
                    records.append({
                        "Code": row[0],
                        "Name": row[1],
                        "Time": row[2]
                    })
        return records

    def update_ui(self, records):
        self.layout.clear_widgets()
        self.layout.add_widget(self._make_row("Code", "Name", "Time", header=True))

        if not records:
            self.layout.add_widget(self._make_row("No records found.", "", "", odd=False))
            return

        for index, rec in enumerate(records):
            odd = index % 2 == 1
            self.layout.add_widget(self._make_row(rec["Code"], rec["Name"], rec["Time"], odd=odd))

    def _make_row(self, code, name, time, header=False, odd=False):
        row = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, padding=(10, 0), spacing=10)

        with row.canvas.before:
            if header:
                Color(0.2, 0.6, 0.2, 1)
            elif odd:
                Color(0.95, 0.95, 0.95, 1)
            else:
                Color(1, 1, 1, 1)
            row.bg_rect = Rectangle(size=row.size, pos=row.pos)

        row.bind(size=lambda *_: setattr(row.bg_rect, 'size', row.size))
        row.bind(pos=lambda *_: setattr(row.bg_rect, 'pos', row.pos))

        color = (1, 1, 1, 1) if header else (0, 0, 0, 1)

        def make_label(text):
            lbl = Label(
                text=f"[b]{text}[/b]" if header else text,
                markup=True,
                halign='left',
                valign='middle',
                color=color,
                font_size=14
            )
            lbl.bind(size=lbl.setter('text_size'))
            return lbl

        row.add_widget(make_label(code))
        row.add_widget(make_label(name))
        row.add_widget(make_label(time))

        return row
