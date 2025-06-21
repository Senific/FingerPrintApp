import threading
import asyncio
import codecs 
import serial
import time

from helper import HelperUtils

 

class Fingerprint():

    COMMENDS = {
        'None': 0x00,  # Default value for enum. Scanner will return error if sent this.
        'Open': 0x01,  # Open Initialization
        'Close': 0x02,  # Close Termination
        'UsbInternalCheck': 0x03,  # UsbInternalCheck Check if the connected USB device is valid
        'ChangeBaudrate': 0x04,  # ChangeBaudrate Change UART baud rate
        'SetIAPMode': 0x05,  # SetIAPMode Enter IAP Mode In this mode, FW Upgrade is available
        'CmosLed': 0x12,  # CmosLed Control CMOS LED
        'GetEnrollCount': 0x20,  # Get enrolled fingerprint count
        'CheckEnrolled': 0x21,  # Check whether the specified ID is already enrolled
        'EnrollStart': 0x22,  # Start an enrollment
        'Enroll1': 0x23,  # Make 1st template for an enrollment
        'Enroll2': 0x24,  # Make 2nd template for an enrollment
        'Enroll3': 0x25,
        # Make 3rd template for an enrollment, merge three templates into one template, save merged template to the database
        'IsPressFinger': 0x26,  # Check if a finger is placed on the sensor
        'DeleteID': 0x40,  # Delete the fingerprint with the specified ID
        'DeleteAll': 0x41,  # Delete all fingerprints from the database
        'Verify1_1': 0x50,  # Verification of the capture fingerprint image with the specified ID
        'Identify1_N': 0x51,  # Identification of the capture fingerprint image with the database
        'VerifyTemplate1_1': 0x52,  # Verification of a fingerprint template with the specified ID
        'IdentifyTemplate1_N': 0x53,  # Identification of a fingerprint template with the database
        'CaptureFinger': 0x60,  # Capture a fingerprint image(256x256) from the sensor
        'MakeTemplate': 0x61,  # Make template for transmission
        'GetImage': 0x62,  # Download the captured fingerprint image(256x256)
        'GetRawImage': 0x63,  # Capture & Download raw fingerprint image(320x240)
        'GetTemplate': 0x70,  # Download the template of the specified ID
        'SetTemplate': 0x71,  # Upload the template of the specified ID
        'GetDatabaseStart': 0x72,  # Start database download, obsolete
        'GetDatabaseEnd': 0x73,  # End database download, obsolete
        'UpgradeFirmware': 0x80,  # Not supported
        'UpgradeISOCDImage': 0x81,  # Not supported
        'Ack': 0x30,  # Acknowledge.
        'Nack': 0x31  # Non-acknowledge
    }

    PACKET_RES_0 = 0x55
    PACKET_RES_1 = 0xAA
    PACKET_DATA_0 = 0x5A
    PACKET_DATA_1 = 0xA5

    ACK = 0x30
    NACK = 0x31
 
    def __init__(self):
        self.lock = threading.RLock()

        #self.port = 'COM6'
        self.port = '/dev/serial0'
        self.baud = 115200
        self.timeout = 1
        self.ser = None

    def __del__(self):
        self.close_serial()

    @staticmethod
    def print_hex(data, width=16):
        s = ""
        for i in range(0, len(data), width):
            row = data[i:i+width]
            s += ' '.join(f"{b:02X}" for b in row) + "\n"
        return s


    @staticmethod
    def get_nack_description(code):
        nack_errors = {
            0x1001: "NACK_TIMEOUT: Capture timeout",
            0x1002: "NACK_INVALID_BAUDRATE: Invalid baud rate",
            0x1003: "NACK_INVALID_POS: Invalid position",
            0x1004: "NACK_IS_NOT_USED: Position is not used",
            0x1005: "NACK_IS_ALREADY_USED: Position already used",
            0x1006: "NACK_COMM_ERR: Communication error",
            0x1007: "NACK_VERIFY_FAILED: 1:1 Verification failed",
            0x1008: "NACK_IDENTIFY_FAILED: 1:N Identification failed",
            0x1009: "NACK_DB_IS_FULL: Database is full",
            0x100A: "NACK_DB_IS_EMPTY: Database is empty",
            0x100B: "NACK_TURN_ERR: Bad image capture (too fast)",
            0x100C: "NACK_BAD_FINGER: Poor image quality",
            0x100D: "NACK_ENROLL_FAILED: Enrollment failed",
            0x100E: "NACK_IS_NOT_SUPPORTED: Command not supported",
            0x100F: "NACK_DEV_ERR: Sensor/hardware error",
            0x1010: "NACK_CAPTURE_CANCELED: Capture canceled",
            0x1011: "NACK_INVALID_PARAM: Invalid parameter",
            0x1012: "NACK_FINGER_IS_NOT_PRESSED: No finger on sensor",
            0x1013: "NACK_TEMPLATE_UPLOAD_FAIL: Upload failed",
            0x1014: "NACK_TEMPLATE_DOWNLOAD_FAIL: Download failed",
            0x1015: "NACK_FAIL: Generic unspecified error",
            0x1016: "NACK_INVALID_TEMPLATE: Invalid template",
            0x1017: "NACK_BAD_TEMPLATE: Corrupted template",
            0x1018: "NACK_FLASH_ERR: Flash write error",
            0x1019: "NACK_INVALID_TEMPLATE_SIZE: Invalid template size",
            0x101A: "NACK_MISMATCH_TEMPLATE_TYPE: Template type mismatch",
            0x101B: "NACK_BAD_SENSOR: Sensor malfunction",
            0x101C: "NACK_WAIT_FINGER_TIMEOUT: Finger detection timeout",
        }
        return nack_errors.get(code, f"Unknown NACK code: 0x{code:04X}")



    def init(self):
        with self.lock:
            try:
                self.ser = serial.Serial(self.port, baudrate=self.baud, timeout=self.timeout)
                time.sleep(1)
                connected = self.open_serial()
                if not connected:
                    self.ser.close()
                    baud_prev = 9600 if self.baud == 115200 else 115200
                    self.ser = serial.Serial(self.port, baudrate=baud_prev, timeout=self.timeout)
                    if not self.open_serial():
                        raise Exception()
                    if self.open():
                        self.change_baud(self.baud)
                        HelperUtils.logInfo("The baud rate is changed to %s." % self.baud)
                    self.ser.close()
                    self.ser = serial.Serial(self.port, baudrate=self.baud, timeout=self.timeout)
                    if not self.open_serial():
                        raise Exception()
                HelperUtils.logInfo("Serial connected.")
                self.open()
                self._flush()
                self.close()
                return True
            except Exception as e: 
                HelperUtils.logError(f"Failed to connect to the serial: {e}") 
            return False

    def open_serial(self):
        with self.lock:
            if not self.ser:
                return False
            if self.ser.isOpen():
                self.ser.close()
            self.ser.open()
            time.sleep(0.1)
            connected = self.open()
            if connected is None:
                return False
            if connected:
                self.close()
                return True
            else:
                return False

    def close_serial(self):
        with self.lock:
            if self.ser:
                self.ser.close()

    def is_connected(self):
        with self.lock:
            if self.ser and self.ser.isOpen():
                return True
            return False

    def _send_packet(self, cmd, param=0):
        with self.lock:
            cmd = Fingerprint.COMMENDS[cmd]
            param = [int(hex(param >> i & 0xFF), 16) for i in (0, 8, 16, 24)]

            packet = bytearray(12)
            packet[0] = 0x55
            packet[1] = 0xAA
            packet[2] = 0x01
            packet[3] = 0x00
            packet[4] = param[0]
            packet[5] = param[1]
            packet[6] = param[2]
            packet[7] = param[3]
            packet[8] = cmd & 0x00FF
            packet[9] = (cmd >> 8) & 0x00FF
            chksum = sum(bytes(packet[:10]))
            packet[10] = chksum & 0x00FF
            packet[11] = (chksum >> 8) & 0x00FF
            if self.ser and self.ser.writable():
                self.ser.write(packet)
                return True
            else:
                return False

    def _send_data(self, data, parameter=False): 
        with self.lock: 
            if self.ser and self.ser.writable():
                HelperUtils.logInfo(f"length of written data : { self.ser.write(data)}")
                time.sleep(0.1)
                HelperUtils.logInfo("SENDing DATA ...")
                ack, param, _, _ = self._read_packet()
                HelperUtils.logInfo("✅")
                if parameter:
                    if ack:
                        return param
                    return -1
                return ack
            else:
                return False

    def _flush(self):
        with self.lock:
            while self.ser.readable() and self.ser.inWaiting() > 0:
                p = self.ser.read(self.ser.inWaiting())
                if p == b'':
                    break

    def _read(self):
        with self.lock:
            if self.ser and self.ser.readable():
                try:
                    p = self.ser.read()
                    if p == b'':
                        return None
                    return int(codecs.encode(p, 'hex_codec'), 16)
                except:
                    return None
            else:
                return None

    def _read_header(self):
        with self.lock:
            if self.ser and self.ser.readable():
                firstbyte = self._read()
                secondbyte = self._read()
                return firstbyte, secondbyte
            return None, None

    def _read_packet(self, wait=True):
        """

        :param wait:
        :return: ack, param, res, data
        """
        # Read response packet
        with self.lock:
            packet = bytearray(12)
            while True:
                firstbyte, secondbyte = self._read_header()
                if not firstbyte or not secondbyte:
                    if wait:
                        continue
                    else:
                        return None, None, None, None
                elif firstbyte == Fingerprint.PACKET_RES_0 and secondbyte == Fingerprint.PACKET_RES_1:
                    break
            packet[0] = firstbyte
            packet[1] = secondbyte
            p = self.ser.read(10)
            packet[2:12] = p[:]

            # Parse ACK
            ack = True if packet[8] == Fingerprint.ACK else False

            # Parse parameter
            param = bytearray(4)
            param[:] = packet[4:8]
            if param is not None:
                param = int(codecs.encode(param[::-1], 'hex_codec'), 16)

            # Parse response
            res = bytearray(2)
            res[:] = packet[8:10]
            if res is not None:
                res = int(codecs.encode(res[::-1], 'hex_codec'), 16)

            # Read data packet
            data = None
            if self.ser and self.ser.readable() and self.ser.inWaiting() > 0:
                firstbyte, secondbyte = self._read_header()
                if firstbyte and secondbyte:
                    # Data exists.
                    if firstbyte == Fingerprint.PACKET_DATA_0 and secondbyte == Fingerprint.PACKET_DATA_1:
                        HelperUtils.logInfo(">> Data exists...")
                        # print("FB-SB: ", firstbyte, secondbyte)
                        data = bytearray()
                        data.append(firstbyte)
                        data.append(secondbyte)
            read_buffer = b''                    
            if data:
                while True:
                    chunk_size = 14400
                    p = self.ser.read(size=chunk_size)
                    read_buffer += p
                    # print(p, type(p))
                    if len(p) == 0:
                        HelperUtils.logInfo(">> Transmission Completed . . .")
                        break

            return ack, param, res, read_buffer

    def open(self):
        with self.lock:
            if self._send_packet("Open"):
                ack, _, _, _ = self._read_packet(wait=False)
                return ack
            return None

    def close(self):
        with self.lock:
            if self._send_packet("Close"):
                ack, _, _, _ = self._read_packet()
                return ack
            return None

    def set_led(self, on):
        with self.lock:
            if self._send_packet("CmosLed", 1 if on else 0):
                ack, _, _, _ = self._read_packet()
                return ack
            return None

    def get_enrolled_cnt(self):
        with self.lock:
            if self._send_packet("GetEnrollCount"):
                ack, param, _, _ = self._read_packet()
                return param if ack else -1
            return None

    def is_finger_pressed(self):
        with self.lock:
            HelperUtils.logInfo("Checking if finger is pressed or not.")
            self.set_led(True)
            time.sleep(1)
            if self._send_packet("IsPressFinger"):
                ack, param, _, _ = self._read_packet()
                self.set_led(False)
                if not ack:
                    return None
                return True if param == 0 else False
            else:
                return None

    def change_baud(self, baud=115200):
        with self.lock:
            if self._send_packet("ChangeBaudrate", baud):
                ack, _, _, _ = self._read_packet()
                return True if ack else False
            return None

    def capture_finger(self, best=False):
        with self.lock:
            self.set_led(True)
            time.sleep(1)
            param = 0 if not best else 1
            if self._send_packet("CaptureFinger", param):
                ack, _, _, _ = self._read_packet()
                self.set_led(False)
                return ack
            return None

    def GetImage(self):
        '''
            Gets an image that is 258x202 (52116 bytes) and returns it in 407 Data_Packets
            Use StartDataDownload, and then GetNextDataPacket until done
            Returns: True (device confirming download starting)
        '''
        with self.lock:
            if self._send_packet("GetImage"):
                ack, param, res, data = self._read_packet()
                if not ack:
                    return None, False
                return data, True  if param == 0 else False
            else:
                return None, False
    
    def MakeTemplate(self):
        with self.lock:
            if not self.capture_finger(best=True):
                return None
            if self._send_packet("MakeTemplate"):
                ack, param, res, data = self._read_packet()
                if not ack:
                    return None, False
                return data, True  if param == 0 else False
            else:
                return None, False

    def start_enroll(self, idx):
        with self.lock:
            if self._send_packet("EnrollStart", idx):
                ack, _, _, _ = self._read_packet()
                return ack
            return None

    def enroll1(self):
        with self.lock:
            if self._send_packet("Enroll1"):
                ack, _, _, _ = self._read_packet()
                return ack
            return None

    def enroll2(self):
        with self.lock:
            if self._send_packet("Enroll2"):
                ack, _, _, _ = self._read_packet()
                return ack
            return None

    def enroll3(self):
        with self.lock:
            if self._send_packet("Enroll3"):
                ack, param, res, data = self._read_packet()
                if not ack:
                    return None, False
                return data, True  if param == 0 else False
            return None, None

    async def enroll(self, status_callback, idx=None, try_cnt=10, sleep=1 ):
        with self.lock:
            if idx is None:
                status_callback("Invalid ID provided")
                return -1,None,None
            
            # Check whether the finger already exists or not
            for i in range(try_cnt):
                existingIdx = self.identify() 
                if existingIdx is not None:
                    break
                await asyncio.sleep(sleep)
                status_callback("Checking existence...")

            if  existingIdx is not None and existingIdx >= 0 and existingIdx != idx:  
                raise RuntimeError(f"Fingerprint already resistered for {existingIdx}")

            status_callback("Start enrolling...")
            cnt = 0
            while True: 
                if self.start_enroll(idx):
                    # Enrolling started
                    break
                else:
                    cnt += 1
                    if cnt >= try_cnt:
                        return -1, None , None 
                    await asyncio.sleep(sleep)

            #Start enroll 1, 2, and 3
            for enr_num, enr in enumerate(["enroll1", "enroll2"]):
                status_callback("Start %s..." % enr)
                cnt = 0
                while not self.capture_finger(best=True):
                    cnt += 1
                    if cnt >= try_cnt:
                        return -1, None , None
                    await asyncio.sleep(sleep)
                    status_callback("Capturing a fingerprint...")
                cnt = 0
                while not getattr(self, enr)():
                    cnt += 1
                    if cnt >= try_cnt:
                        return -1, None ,None
                    await asyncio.sleep(sleep)
                    status_callback("Enrolling the captured fingerprint...")
                
            if self.capture_finger(best=True):
                status_callback("Start enroll3...")
                data, downloadstat = self.enroll3()
                if idx == -1:
                    return idx, data, downloadstat
            # Enroll process finished
            return idx, None, None

    def verifyTemplate(self, idx, data):
        with self.lock:
            data_bytes = bytearray()
            data_bytes.append(90)
            data_bytes.append(165)
            for ch in data:
                data_bytes.append(ch)
            if self._send_packet("VerifyTemplate1_1", param=idx):
                ack, _, _, _ = self._read_packet()
            if ack:
                sendstatus = self._send_data(data_bytes)
                if sendstatus:
                    #HelperUtils.logInfo('|', '>'*10, '👍 MATCH FOUND 👍')
                    HelperUtils.logInfo('👍 MATCH FOUND 👍')
                    return True
                return False

    def setTemplate(self, idx, data):
        with self.lock:
            data_bytes = bytearray()
            data_bytes.append(90)
            data_bytes.append(165)
            for ch in data:
                data_bytes.append(ch)

            if self.check_enrolled(idx):
                raise RuntimeError("Already enrolled!")
            
            existingId = self.identifyTemplate(data)
            if existingId is not None and existingId >=0: 
                raise  RuntimeError(f"Template already registered to {existingId}")

            HelperUtils.logInfo("Send Template Set Packet")
            if self._send_packet("SetTemplate", param=idx):
                ack, param, res, data_ = self._read_packet() 
                print(f"Ack {ack} , Param {param} , Res {res} , Data {data_}")
                if ack:
                    HelperUtils.logInfo("Send Data")
                    if self._send_data(data_bytes):
                        HelperUtils.logInfo(f'👍 setTemplate @ ID: {idx}')
                        return True
                    return False
                return False
            return False 
        

    def deleteAll(self):
        with self.lock:
            res = self._send_packet("DeleteAll")
            if res:
                ack, _, _, _ = self._read_packet()
                return ack
            return False

    def delete(self, idx):
        with self.lock:
            if not isinstance(idx, int) or idx < 0:
                raise RuntimeError("Invalid ID") 
            
            # Delete all fingerprints 
            res = self._send_packet("DeleteID", idx) 
            if res:
                ack, _, _, _ = self._read_packet()
                return ack
            return False

    def identify(self):
        with self.lock:
            if not self.capture_finger(best=True):
                return None
            if self._send_packet("Identify1_N"):
                ack, param, _, _ = self._read_packet()
                if ack:
                    return param
                else:
                    return -1
            return None

    def identifyTemplate(self, data):
        with self.lock:
            data_bytes = bytearray()
            data_bytes.append(90)
            data_bytes.append(165)
            for ch in data:
                data_bytes.append(ch)
            if self._send_packet("IdentifyTemplate1_N"):
                ack, _, _, _ = self._read_packet()
                if ack:
                    param = self._send_data(data_bytes, parameter=True)
                    return param
                return -1
            return None


    def check_enrolled(self, idx):
        with self.lock:
            #Check if a fingerprint is enrolled at the given ID. 
            if not isinstance(idx, int) or idx < 0:
                raise RuntimeError("Invalid ID") 

            if self._send_packet("CheckEnrolled", param=idx):
                ack, param, res, _ = self._read_packet()
                if ack: 
                    return True 
                else:
                    HelperUtils.logInfo(f"Res:{res} Param:{param} {self.get_nack_description(param)}")
                    return False
            else:
                raise RuntimeError("Failed to send CheckEnrolled command.")
                #return False

    def get_template(self, idx):
        #Downloads the fingerprint template stored at the specified ID.
        #Returns:
        #    template_data (bytes): The raw template data.
        #    success (bool): Whether the operation was successful. 
        with self.lock:
            if not isinstance(idx, int) or idx < 0:
                raise RuntimeError("Invalid ID") 

            if self._send_packet("GetTemplate", idx):
                ack, param, res, data = self._read_packet()
                if not ack:
                    HelperUtils.logInfo(f"Res:{res} Param:{param} {self.get_nack_description(param)}")
                    return None, False

                if data and len(data) > 0: 
                    return data, True
                else:
                    HelperUtils.logInfo("Template data is empty or missing.")
                    return None, False 
            else: 
                raise RuntimeError("Failed to send GetTemplate command.")
                #return None, False
