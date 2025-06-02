import asyncio
import os
import httpx
import aiosqlite
import json
from urllib.parse import quote
from cryptography.fernet import Fernet

# 🔧 Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUNTIME_DIR = os.path.join(BASE_DIR, "RuntimeResources")
IMAGES_DIR = os.path.join(RUNTIME_DIR, "Images")
ENROLLMENTS_DIR = os.path.join(RUNTIME_DIR, "Enrollments")
SETTINGS_FILE = os.path.join(RUNTIME_DIR, "settings.txt")
FERNET_KEY_FILE = os.path.join(RUNTIME_DIR, "fernet.key") 
DB_FILE = os.path.join(RUNTIME_DIR, "employees.db")
LAST_SYNC_FILE = os.path.join(RUNTIME_DIR, "last_sync.txt")

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

    async def sync(self):
        print(f"🔄 Starting sync... System Code: {self.system_code}") 
        if not self.token:
            await self.authenticate()

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

        self.save_last_sync_time(new_sync_time)
        print(f"✅ Sync completed. Last sync updated to: {new_sync_time}")
