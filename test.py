import serial

ser = serial.Serial("/dev/serial0", baudrate=9600, timeout=1)

ser.write(b'\x55\xAA...')  # Example command to fingerprint module

response = ser.read(32)
print(response)
