import logging
import httpx
import io

class ApiUtils:
    API_URL = "https://poca.senific.com" 

    system_code = "TB"
    username = "Admin"
    password = "Admin"

    token = ""
    client  = httpx.AsyncClient()

    @staticmethod
    async def get_token(_username, _password, _system_code, _api_url):
        url = f"{_api_url}/token"
        headers = {
            "SystemCode": _system_code,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "password",
            "username": _username,
            "password": _password
        }
        print("🔐 Authenticating (static)...")
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data, headers=headers)
            if response.status_code != 200:
                raise Exception(f"Token request failed: {response.text}")
            print("✅ Static Authenticated!")
            return response.json().get("access_token")
    
    @staticmethod
    async def authenticate():
        ApiUtils.token = await ApiUtils.get_token(
            ApiUtils.username, ApiUtils.password, ApiUtils.system_code, ApiUtils.API_URL
        )

    @staticmethod
    async def upload_fingerprint_template(identifier: int, template_data: bytes):
        #Uploads a fingerprint template (.dat) as a file to the ASP.NET API.
        if not ApiUtils.token:
            await ApiUtils.authenticate()

        url = f"{ApiUtils.API_URL}/api/Images/UploadFingerprintTemplate?identifier={identifier}"
        headers = {
            "Authorization": f"Bearer {ApiUtils.token}",
            "SystemCode": ApiUtils.system_code
        }

        # Prepare the file-like object for multipart upload
        files = {
            "file": (f"{identifier}.dat", io.BytesIO(template_data), "application/octet-stream")
        }

        try:
            response = await ApiUtils.client.post(url, headers=headers, files=files)
            response.raise_for_status()

            logging.info(f"✅ Fingerprint template uploaded for Identifier {identifier}")
            return response.json()
        except httpx.HTTPStatusError as e:
            logging.error(f"❌ API Error ({e.response.status_code}): {e.response.text}")
            raise
        except Exception as e:
            logging.error(f"❌ Request failed: {e}")
            raise


    @staticmethod
    async def delete_fingerprint_template(identifier: int):
        """
        Deletes a fingerprint template from the ASP.NET API using the identifier.
        """
        if not ApiUtils.token:
            await ApiUtils.authenticate()

        url = f"{ApiUtils.API_URL}/api/Images/DeleteFingerprintTemplate?identifier={identifier}"
        headers = {
            "Authorization": f"Bearer {ApiUtils.token}",
            "SystemCode": ApiUtils.system_code
        }

        try:
            response = await ApiUtils.client.delete(url, headers=headers)
            response.raise_for_status()

            logging.info(f"🗑️ Fingerprint template deleted for Identifier {identifier}")
            return response.json()
        except httpx.HTTPStatusError as e:
            logging.error(f"❌ API Error ({e.response.status_code}): {e.response.text}")
            raise
        except Exception as e:
            logging.error(f"❌ Request failed: {e}")
            raise
    
    @staticmethod
    async def get_fingerprint_template(identifier: int) -> bytes:
        if not ApiUtils.token:
            await ApiUtils.authenticate()

        url = f"{ApiUtils.API_URL}/api/Images/GetFingerprintTemplate?identifier={identifier}"
        headers = {
            "Authorization": f"Bearer {ApiUtils.token}",
            "SystemCode": ApiUtils.system_code
        }

        try:
            response = await ApiUtils.client.get(url, headers=headers) 
            response.raise_for_status()

            logging.info(f"📥 Fingerprint template retrieved for Identifier {identifier}")
            return response.content  # binary template data
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logging.warning(f"⚠️ Template not found for Identifier {identifier}")
                return b""  # return empty byte array
            else:
                logging.error(f"❌ API Error ({e.response.status_code}): {e.response.text}")
                raise
        except Exception as e:
            logging.error(f"❌ Request failed: {e}")
            raise
