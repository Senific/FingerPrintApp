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
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock
from kivy.app import App
from employee_sync import EmployeeSync
from employee_sync import RUNTIME_DIR


class EmployeeListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.all_employees = []

        main_layout = BoxLayout(orientation='vertical', spacing=5)

        # 🔍 Search Bar Layout
        search_bar = BoxLayout(orientation='horizontal', size_hint=(1, 0.15), spacing=5, padding=[5, 5])

        self.search_input = TextInput(
            hint_text="Search by Name or Code...",
            multiline=False
        )
        self.search_input.bind(on_text_validate=self.on_search_enter_pressed)  # <-- Bind Enter key

        self.search_button = Button(text="Search", size_hint_x=None, width=100)
        self.search_button.bind(on_press=self.on_search_button_pressed)

        search_bar.add_widget(self.search_input)
        search_bar.add_widget(self.search_button)

        # 📜 ScrollView and employee list
        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.layout = GridLayout(cols=1, spacing=1, size_hint_y=None, padding=0)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.scroll.add_widget(self.layout)

        # 🔙 Back Button
        self.back_button = Button(
            text="Back",
            size_hint=(1, 0.1),
            on_press=self.go_back
        )

        main_layout.add_widget(search_bar)
        main_layout.add_widget(self.scroll)
        main_layout.add_widget(self.back_button)

        self.add_widget(main_layout)

    def go_back(self, instance): 
        self.manager.current = "menu" 

    def on_enter(self):
        Thread(target=self.populate_employees).start()

    def populate_employees(self):
        employees = asyncio.run(self.fetch_employees())
        self.all_employees = employees
        Clock.schedule_once(lambda dt: self.update_ui(employees))

    async def fetch_employees(self):
        db_path = os.path.join(RUNTIME_DIR, "employees.db")
        employees = []
        async with aiosqlite.connect(db_path) as db:
            async with db.execute("SELECT ID, Name, Code FROM Employees ORDER BY Name ASC") as cursor:
                async for row in cursor:
                    employees.append({"ID": row[0], "Name": row[1], "Code": row[2]})
        return employees

    def update_ui(self, employee_list):
        self.layout.clear_widgets()
        self.layout.add_widget(self._make_row("Name", "Code", header=True))

        if not employee_list:
            self.layout.add_widget(self._make_row("No employees found.", "", odd=False))
            return

        for index, emp in enumerate(employee_list):
            odd = index % 2 == 1
            self.layout.add_widget(self._make_row(emp["Name"], emp["Code"], odd=odd, emp=emp))

    def on_search_button_pressed(self, instance):
        self.perform_search()

    def on_search_enter_pressed(self, instance):
        self.perform_search()

    def perform_search(self):
        text = self.search_input.text.strip().lower()
        if not text:
            # Don't show full list on empty search — show nothing
            Clock.schedule_once(lambda dt: self.update_ui([]))
            return

        filtered = [
            e for e in self.all_employees
            if text in e["Name"].lower() or text in e["Code"].lower()
        ]
        Clock.schedule_once(lambda dt: self.update_ui(filtered))

    def _make_row(self, name, code, header=False, odd=False, emp=None):
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

        name_lbl = Label(
            text=f"[b]{name}[/b]" if header else name,
            markup=True,
            halign='left',
            valign='middle',
            color=color,
            font_size=14
        )
        name_lbl.bind(size=name_lbl.setter('text_size'))

        code_lbl = Label(
            text=f"[b]{code}[/b]" if header else code,
            markup=True,
            halign='left',
            valign='middle',
            color=color,
            font_size=14
        )
        code_lbl.bind(size=code_lbl.setter('text_size'))

        row.add_widget(name_lbl)
        row.add_widget(code_lbl)

        if header:
            row.add_widget(Label(text="[b]Action[/b]", markup=True, color=color, font_size=14))
        else:
            enrolled = EmployeeSync.has_enrollment_image(emp["ID"])
            btn = Button(
                text="Enroll",
                size_hint_x=None,
                width=100,
                font_size=14,
                background_color=(0, 0.6, 0, 1) if enrolled else (1, 1, 1, 1),
                color=(1, 1, 1, 1) if enrolled else (0, 0, 0, 1)
            )
            btn.bind(on_release=lambda instance: self.goto_enroll(emp))
            row.add_widget(btn)

        return row


    def goto_enroll(self, emp):
        app = App.get_running_app()
        app.employee_to_enroll = emp 
        app.previous_screen = "employees"  
        self.manager.current = "enroll"
