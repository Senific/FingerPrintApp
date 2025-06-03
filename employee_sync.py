import asyncio
import os
import httpx
import aiosqlite
import json
from urllib.parse import quote
from cryptography.fernet import Fernet
from datetime import datetime, timedelta

# 🔧 Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUNTIME_DIR = os.path.join(BASE_DIR, "RuntimeResources")
IMAGES_DIR = os.path.join(RUNTIME_DIR, "Images")
ENROLLMENTS_DIR = os.path.join(RUNTIME_DIR, "Enrollments")
SETTINGS_FILE = os.path.join(RUNTIME_DIR, "settings.txt")
FERNET_KEY_FILE = os.path.join(RUNTIME_DIR, "fernet.key") 
DB_FILE = os.path.join(RUNTIME_DIR, "employees.db")
LAST_SYNC_FILE = os.path.join(RUNTIME_DIR, "last_sync.txt")
SECONDARY_SETTINGS_FILE = os.path.join(RUNTIME_DIR, "SecondarySettings.txt")

os.makedirs(RUNTIME_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(ENROLLMENTS_DIR, exist_ok=True)

# 🔐 Fernet Key Loader
def get_fernet():
    if not os.path.exists(FERNET_KEY_FILE):
        raise FileNotFoundError("Fernet key not found. Please configure settings via the UI.")
    with open(FERNET_KEY_FILE, "rb") as f:
        key = f.read()
    return Fernet(key)

# 🔧 Read settings.txt and decrypt password
def get_api_config():
    if not os.path.exists(SETTINGS_FILE):
        raise FileNotFoundError("Settings file not found. Please configure settings via the UI.")
    with open(SETTINGS_FILE, "r") as f:
        data = json.load(f)

    fernet = get_fernet()
    data["password"] = fernet.decrypt(data["password"].encode()).decode()
    data["api_url"] = "https://poca.senific.com"  # Can be made configurable if needed
    return data



class Employee:
    def __init__(self, ID, Name, Code, Description):
        self.ID = ID
        self.Name = Name
        self.Code = Code
        self.Description = Description


class EmployeeDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = DB_FILE
        self.db_path = db_path

    async def initialize(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS Employees (
                    ID INTEGER PRIMARY KEY,
                    Name TEXT,
                    Code TEXT,
                    Description TEXT
                )
            ''')

            await db.execute('''
                CREATE TABLE IF NOT EXISTS Attendances (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Employee_ID INTEGER,
                    Code TEXT,
                    Name TEXT,
                    Time TEXT,
                    State TEXT,
                    Deleted BIT
                )
            ''')
            await db.commit()

    async def upsert_employee(self, emp: Employee):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO Employees (ID, Name, Code, Description)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(ID) DO UPDATE SET
                    Name=excluded.Name,
                    Code=excluded.Code,
                    Description=excluded.Description
            ''', (emp.ID, emp.Name, emp.Code, emp.Description))
            await db.commit()

    async def delete_employee(self, emp_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM Employees WHERE ID=?", (emp_id,))
            await db.commit()


class EmployeeSync:
    def __init__(self, db, sync_file=None):
        config = get_api_config()
        self.username = config["username"]
        self.password = config["password"]
        self.system_code = config["system_code"]
        self.api_url = config["api_url"]
        self.db = db
        self.sync_file = sync_file or LAST_SYNC_FILE
        self.token = None
        self.client = httpx.AsyncClient()

    sync_interval_ms = 1000  # Default value accessible globally

    @staticmethod
    async def get_token(username, password, system_code, api_url):
        url = f"{api_url}/token"
        headers = {
            "SystemCode": system_code,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "password",
            "username": username,
            "password": password
        }
        print("🔐 Authenticating (static)...")
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data, headers=headers)
            if response.status_code != 200:
                raise Exception(f"Token request failed: {response.text}")
            print("✅ Static Authenticated!")
            return response.json().get("access_token")

    async def authenticate(self):
        self.token = await EmployeeSync.get_token(
            self.username, self.password, self.system_code, self.api_url
        )

    @staticmethod
    def has_enrollment_image(emp_id: int) -> bool:
        return os.path.exists(os.path.join(ENROLLMENTS_DIR, f"{emp_id}.jpg"))

    async def close(self):
        await self.client.aclose()

    def save_secondary_settings(self, interval_ms: int):
        try:
            with open(SECONDARY_SETTINGS_FILE, "w") as f:
                f.write(str(interval_ms))
            print(f"💾 Saved sync interval: {interval_ms} ms to SecondarySettings.txt")
        except Exception as e:
            print(f"❌ Failed to save sync interval: {e}")

    def load_secondary_settings(self) -> int:
        if os.path.exists(SECONDARY_SETTINGS_FILE):
            try:
                with open(SECONDARY_SETTINGS_FILE, "r") as f:
                    return int(f.read().strip())
            except:
                pass
        return 1000  # Default fallback

    async def get_system_info(self):
        url = f"{self.api_url}/api/Values/GetSystemInfo?code={quote(self.system_code)}" 
        try:
            response = await self.client.get(url, timeout=10)
            response.raise_for_status() 
            return response.json()
        except Exception as e:
            print(f"❌ Failed to get system info: {e}")
            return None


    async def get_server_time(self):
        url = f"{self.api_url}/api/values/GetDateTime"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                response.raise_for_status()
                return response.text.strip('"')
        except Exception as e:
            print(f"❌ Failed to get server time: {e}")
            return None

    def get_last_sync_time(self):
        if os.path.exists(self.sync_file):
            with open(self.sync_file, "r") as f:
                return f.read().strip()
        return "1/1/2000"

    def save_last_sync_time(self, sync_time):
        with open(self.sync_file, "w") as f:
            f.write(sync_time)

    async def download_employee_image(self, emp_id):
        url = f"{self.api_url}/api/images/getimage?id={emp_id}&type=0&idType=0"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "SystemCode": self.system_code
        }
        try:
            response = await self.client.get(url, headers=headers)
            if response.status_code == 200:
                image_path = os.path.join(IMAGES_DIR, f"{emp_id}.jpg")
                with open(image_path, "wb") as f:
                    f.write(response.content)
        except Exception as e:
            print(f"❌ Failed to download image for {emp_id}: {e}")

    def delete_employee_image(self, emp_id):
        path = os.path.join(IMAGES_DIR, f"{emp_id}.jpg")
        if os.path.exists(path):
            os.remove(path)


    async def upload_attendance(self, employee_id: int, state: str, time_str: str):
        """
        Uploads a single attendance record to the ASP.NET API.
        """
        if not self.token:
            await self.authenticate()

        url = f"{self.api_url}/api/Payroll/AddOrUpdateAttendance"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "SystemCode": self.system_code,
            "Content-Type": "application/json"
        }

        payload = {
            "Employee_ID": employee_id,
            "Time": time_str,
            "State": state
        }

        try:
            response = await self.client.post(url, headers=headers, json=payload)
            response.raise_for_status()

            print(f"✅ Attendance uploaded for Employee {employee_id}")
            return response.json()  # Do NOT await
        except httpx.HTTPStatusError as e:
            print(f"❌ API Error ({e.response.status_code}): {e.response.text}")
            raise
        except Exception as e:
            print(f"❌ Request failed: {e}")
            raise

    async def upload_attendances(self):
        print("📤 Uploading attendances...")

        async with aiosqlite.connect(self.db.db_path) as db:
            async with db.execute("""
                SELECT ID, Employee_ID, Code, Name, Time, State
                FROM Attendances
                WHERE Deleted IS NOT 1
            """) as cursor:
                records = await cursor.fetchall()

            if not records:
                print("✅ No attendances to upload.")
                return

            for row in records:
                local_id, employee_id, code, name, time_str, state = row
                try:
                    await self.upload_attendance(employee_id, state, time_str)

                    # 🔁 Mark the record as deleted
                    await db.execute("UPDATE Attendances SET Deleted = 1 WHERE ID = ?", (local_id,))
                    await db.commit()

                    print(f"✅ Uploaded and marked as deleted attendance ID {local_id}")
                except Exception as e:
                    print(f"❌ Error while uploading attendance ID {local_id}: {e}")

            # 🧹 Delete records older than 2 months where Deleted = 1
            two_months_ago = (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d %H:%M:%S")
            await db.execute("""
                DELETE FROM Attendances
                WHERE Deleted = 1 AND datetime(Time) < datetime(?)
            """, (two_months_ago,))
            await db.commit()

            print("🧹 Old deleted attendance records cleaned up (older than 2 months).")

        
    async def sync(self):
        print(f"🔄 Starting sync... System Code: {self.system_code}") 
        if not self.token:
            await self.authenticate()
 
        system_info = await self.get_system_info() 
        if not system_info:
            print("❌ Unable to fetch system info. Aborting sync.")
            return

        EmployeeSync.sync_interval_ms = system_info.get("FingerMachineSyncInterval", 1000)
        print(f"Sync Interval: {EmployeeSync.sync_interval_ms}ms")
        self.save_secondary_settings(EmployeeSync.sync_interval_ms)

        last_sync = self.get_last_sync_time()
        print(f"🕒 Last sync: {last_sync}")

        new_sync_time = await self.get_server_time()
        if not new_sync_time:
            print("❌ Server time unavailable")
            return

        url = f"{self.api_url}/api/Employees/GetNewChanges?lastSyncDate={quote(last_sync)}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "SystemCode": self.system_code
        }

        try:
            response = await self.client.get(url, headers=headers)
            if response.status_code == 401:
                await self.authenticate()
                headers["Authorization"] = f"Bearer {self.token}"
                response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"❌ Sync failed: {e}")
            return

        print(f"📦 Syncing {len(data)} employees...")
        for idx, emp in enumerate(data, 1):
            emp_id = emp["ID"]
            if emp["Deleted"]:
                await self.db.delete_employee(emp_id)
                self.delete_employee_image(emp_id)
            else:
                employee = Employee(emp_id, emp["Name"], emp["Code"], emp["Description"])
                await self.db.upsert_employee(employee)
                await self.download_employee_image(emp_id)

            print(f"🔄 {idx}/{len(data)}")
            await asyncio.sleep(0.01)

        # 🔼 Upload and clear local attendances
        await self.upload_attendances()
        self.save_last_sync_time(new_sync_time)
        print(f"✅ Sync completed. Last sync updated to: {new_sync_time}")
