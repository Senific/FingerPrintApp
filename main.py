from datetime import datetime
import os
import logging

from helper import HelperUtils 

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
import sys
import threading
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.app import App
from kivy.base import EventLoop
from kivy.clock import Clock

from idleScreen import IdleScreen
from menuScreen import MenuScreen
from wifiNetworkScreen import WifiNetworkScreen
from enrollScreen import EnrollScreen
from logScreen import LogScreen
from settingsScreen import SettingsScreen
from employeeListScreen import EmployeeListScreen
from MarkAttendanceScreen  import MarkAttendanceScreen
from AttendancesScreen import AttendancesScreen
from employee_sync import EmployeeSync, EmployeeDatabase, SETTINGS_FILE,fp
from popups import PopupUtils

db = EmployeeDatabase()

# Global asyncio loop instance
async_loop = asyncio.new_event_loop()
asyncio.set_event_loop(async_loop)

# Make Kivy call async loop periodically
def run_async_loop(dt):
    try:
        async_loop.call_soon(async_loop.stop)
        async_loop.run_forever()
    except Exception as e:
        HelperUtils.logError(f"[ERROR] Async loop crashed: {e}")

# Schedule the asyncio loop to tick with Kivy's clock
Clock.schedule_interval(run_async_loop, 0)

 
# Detect Raspberry Pi
is_raspberry = False
if sys.platform == "linux":
    try:
        with open("/proc/cpuinfo", "r") as f:
            is_raspberry = "Raspberry Pi" in f.read()
    except:
        pass

# Configure Kivy
#Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
#Config.set('graphics', 'show_cursor', '0' if is_raspberry else '1')
#Config.set('modules', 'touchring', '')

# Set window size
Window.size = (480, 320)
Window.fullscreen = False
Window.left = (Window.system_size[0] - 480) // 2
Window.top = (Window.system_size[1] - 320) // 2


if is_raspberry:
    import pigpio 
    TOUCH_PIN = 5  # GPIO5 (Physical pin 29)

    async def on_validation_failed():
            PopupUtils.show_status_popup()
            PopupUtils.update_status_popup("Failed to Identify!" , 1)
            await asyncio.sleep(2)
            PopupUtils.dismiss_status_popup()
 
    
    def resetScreen(app):
        try:
            # Cancel previous scheduled "go back to main"
            if hasattr(app, "mark_timeout_event") and app.mark_timeout_event:
                app.mark_timeout_event.cancel()
            PopupUtils.dismiss_status_popup()
            app.root.current = "main" 
        except Exception as e:
            HelperUtils.logError(f"Screen Reset Error: {e}")

    async def identify():     
        try:  
            app =  App.get_running_app()     
            resetScreen(app)

            fp.open()
            fp.set_led(True) 
            if fp.is_finger_pressed():
                identifier = fp.identify()
                if identifier is not None and identifier >= 0:  
                    try: 
                        HelperUtils.logInfo(f"Identified: {identifier}") 
                        employee = await db.get_employeeByIdentifier(identifier)  
                        if employee is not None:  
                            marked_time =  datetime.now()
                            app.marked_employee = employee
                            app.marked_time = marked_time
                            result = await db.insert_attendance(employee, marked_time)
                            if result == True:  
                                # Set screen to "mark"
                                app.root.current = "mark" 
                                # Schedule new "go back to main" in 5 seconds
                                app.mark_timeout_event = Clock.schedule_once(lambda dt: setattr(app.root, "current", "main"), 5)
                            else:
                                raise RuntimeError("Failed At Marking to database")
                        else: 
                            HelperUtils.logInfo("No employee found for identifier in DB!") 
                            Clock.schedule_once(lambda dt: asyncio.ensure_future(on_validation_failed()))
                    except Exception as e:
                        HelperUtils.logError(f"Identify Exception: {e}") 
                        Clock.schedule_once(lambda dt: asyncio.ensure_future(on_validation_failed()))
                else: 
                    HelperUtils.logInfo("No employee found for finger!") 
                    Clock.schedule_once(lambda dt: asyncio.ensure_future(on_validation_failed()))
                
        except Exception as e: 
                HelperUtils.logError(f"Identify.2 Exception : {e}") 
                Clock.schedule_once(lambda dt: asyncio.ensure_future(on_validation_failed()))
        finally:
            try:
                fp.set_led(False)
                fp.close()
            except Exception as e:
                HelperUtils.logError(f"Identify.3 Exception : {e}") 
                Clock.schedule_once(lambda dt: asyncio.ensure_future(on_validation_failed()))


    def on_touch(gpio, level, tick): 
        app = App.get_running_app() 
        if app.root.current != "enroll":
            if level == 0: 
                Clock.schedule_once(lambda dt: asyncio.ensure_future(identify()))
                HelperUtils.logInfo("👆 Finger touched")
            elif level == 1: 
                HelperUtils.logInfo("✋ Finger released")
        else: 
            try:
                from employee_sync import on_touch_callback
                if  on_touch_callback is not None:
                    HelperUtils.logInfo("Touch Callback is Active") 
                    touchResult = level == 0
                    Clock.schedule_once(lambda dt: asyncio.ensure_future(on_touch_callback(touchResult)))
                else:
                    HelperUtils.logInfo("Touch Callback is None") 
            except Exception as ex:
                HelperUtils.logError(f"Touch Callback is Error: {ex}") 
  

    # Connect to pigpio daemon
    pi = pigpio.pi()
    if not pi.connected:
        HelperUtils.logWarning("❌ Failed to connect to pigpiod. Is it running?")
        exit(1)

    # Set the pin as input
    pi.set_mode(TOUCH_PIN, pigpio.INPUT)

    # Register callback on both edges
    pi.callback(TOUCH_PIN, pigpio.EITHER_EDGE, on_touch)


 
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

        await db.initialize()

        try:
            config = get_api_config()
        except FileNotFoundError:
            HelperUtils.logWarning("Settings not found. Skipping sync.")
            return

        sync = EmployeeSync(db=db)

        try:
            while True:
                try:
                    await sync.sync()
                except Exception as e:
                    HelperUtils.logError(f"Sync error: {e}")
                await asyncio.sleep(EmployeeSync.sync_interval_ms / 1000)
                HelperUtils.logInfo(f"Warning Threed Slept for {EmployeeSync.sync_interval_ms} ms"  )
        finally:
            await sync.close()



   
if __name__ == "__main__": 
    try:
        sync_thread = BackgroundSyncThread()
        sync_thread.start()  
    except Exception as e:
        HelperUtils.logError(f"Background sync failed to start: {e}")

    try:
        FingerprintApp().run()
    except Exception as e:
        HelperUtils.logError("App crashed on startup:")
