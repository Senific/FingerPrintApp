import logging

# Suppress overly verbose httpx/httpcore debug logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


# Setup minimal file logging
log_file = os.path.expanduser("~/app_debug.log")
os.makedirs(os.path.dirname(log_file), exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    filename=log_file,
    filemode="a"
)

import asyncio
import os
import sys
import threading
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.app import App

from idleScreen import IdleScreen
from menuScreen import MenuScreen
from wifiNetworkScreen import WifiNetworkScreen
from enrollScreen import EnrollScreen
from logScreen import LogScreen
from settingsScreen import SettingsScreen
from employeeListScreen import EmployeeListScreen
from MarkAttendanceScreen  import MarkAttendanceScreen
from AttendancesScreen import AttendancesScreen
from employee_sync import EmployeeSync, EmployeeDatabase, SETTINGS_FILE


# Detect Raspberry Pi
is_raspberry = False
if sys.platform == "linux":
    try:
        with open("/proc/cpuinfo", "r") as f:
            is_raspberry = "Raspberry Pi" in f.read()
    except:
        pass

# Configure Kivy
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
Config.set('graphics', 'show_cursor', '0' if is_raspberry else '1')
Config.set('modules', 'touchring', '')

# Set window size
Window.size = (480, 320)
Window.fullscreen = False
Window.left = (Window.system_size[0] - 480) // 2
Window.top = (Window.system_size[1] - 320) // 2

class FingerprintApp(App):
    def build(self):
        self.employee_to_enroll = None
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(IdleScreen(name='main'))
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(WifiNetworkScreen(name='wifi'))
        sm.add_widget(EnrollScreen(name='enroll'))
        sm.add_widget(LogScreen(name='logs'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(EmployeeListScreen(name='employees'))
        sm.add_widget(MarkAttendanceScreen(name='mark'))
        sm.add_widget(AttendancesScreen(name='attendances'))
        if not os.path.exists(SETTINGS_FILE):
            sm.current = 'settings'  # 👈 force settings screen
        else:
            sm.current = 'main'  # or any other default

        return sm



class BackgroundSyncThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.loop = asyncio.new_event_loop()

    def run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.sync_loop())

    async def sync_loop(self):
        from employee_sync import get_api_config  # Safe import inside thread

        db = EmployeeDatabase()
        await db.initialize()

        try:
            config = get_api_config()
        except FileNotFoundError:
            logging.warning("Settings not found. Skipping sync.")
            return

        sync = EmployeeSync(db=db)

        try:
            while True:
                try:
                    await sync.sync()
                except Exception as e:
                    logging.error(f"Sync error: {e}")
                await asyncio.sleep(EmployeeSync.sync_interval_ms / 1000)
                print(f"Warning Threed Slept for {EmployeeSync.sync_interval_ms} ms"  )
        finally:
            await sync.close()

if __name__ == "__main__":
    try:
        sync_thread = BackgroundSyncThread()
        sync_thread.start()
    except Exception as e:
        logging.error(f"Background sync failed to start: {e}")

    try:
        FingerprintApp().run()
    except Exception as e:
        logging.exception("App crashed on startup:")
