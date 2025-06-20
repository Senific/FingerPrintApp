import asyncio
import time
from fplib import fplib

# fingerprint module variables
fp = fplib()

# module initializing
init = fp.init()
print("is initialized :", init)

# Run only task that is specified


async def main():
    test_template_data = bytearray([
    0x01, 0x00, 0x04, 0x10, 0x52, 0x00, 0xBE, 0x32, 0x87, 0x84, 0x86, 0x19, 0xFE, 0xEF, 0x09, 0x43,
    0x88, 0x85, 0x03, 0x19, 0xC0, 0xEF, 0xCD, 0x03, 0x87, 0x7D, 0x46, 0x26, 0xB4, 0xD0, 0xDE, 0x6B,
    0x88, 0x82, 0x83, 0x26, 0x40, 0x00, 0xE5, 0x9B, 0x86, 0x75, 0x0A, 0x46, 0x32, 0xE1, 0x21, 0xA4,
    0x84, 0x58, 0x04, 0x68, 0xFE, 0x0F, 0x92, 0x14, 0x88, 0x7F, 0x86, 0x46, 0xB2, 0x38, 0xD9, 0x4C,
    0x86, 0x55, 0x4A, 0x9B, 0xB4, 0xF8, 0xEA, 0x74, 0x87, 0x6A, 0x91, 0x97, 0xEE, 0xF8, 0x99, 0x9B,
    0x84, 0x67, 0xC3, 0x46, 0xFE, 0xDF, 0x02, 0xA4, 0x88, 0x1A, 0x02, 0xA7, 0x39, 0xDE, 0x32, 0xEC,
    0x88, 0x8F, 0x45, 0x06, 0x36, 0xD7, 0x8D, 0x2D, 0x85, 0xBD, 0x47, 0xF8, 0x89, 0xFE, 0x81, 0xC5,
    0x88, 0x99, 0x03, 0xFD, 0x2D, 0xFF, 0xC2, 0xC4, 0x84, 0x53, 0x83, 0x57, 0xFE, 0xE7, 0x26, 0x75,
    0x89, 0x22, 0x83, 0xA8, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x91, 0x67, 0x28, 0xF2, 0x95, 0x16, 0xA6, 0xB4, 0x2A, 0x85,
    0x42, 0x49, 0xF4, 0x34, 0x23, 0x25, 0x99, 0x2F, 0xD5, 0x56, 0x78, 0xF5, 0x33, 0xFF, 0x04, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x2B, 0x4D, 0xA3, 0x4E,
    ])

    test_template_data_14 = bytearray([
        0x01, 0x00, 0x04, 0x1A, 0x5A, 0x00, 0x6D, 0x2A, 0x86, 0xD7, 0xC6, 0xDD, 0x7F, 0xF8, 0x82, 0xC2,
        0x88, 0xED, 0x86, 0x9B, 0xFF, 0xF8, 0xCE, 0xFA, 0x87, 0xE8, 0x08, 0xAC, 0xC5, 0xE0, 0xD6, 0x62,
        0x89, 0x05, 0x05, 0x9C, 0xBF, 0xF8, 0x2E, 0xF3, 0x86, 0xE5, 0x06, 0xA9, 0x47, 0xD0, 0xDE, 0x93,
        0x88, 0x0B, 0x05, 0x88, 0x41, 0xEF, 0x06, 0x54, 0x86, 0xE3, 0x83, 0xB7, 0x07, 0xD8, 0x3E, 0x24,
        0x86, 0x63, 0x44, 0x47, 0x7A, 0x1F, 0x55, 0x6C, 0x88, 0x0C, 0x44, 0x86, 0x05, 0xE8, 0x85, 0xCC,
        0x89, 0x8A, 0x83, 0xF6, 0xF9, 0x0F, 0xAD, 0x54, 0x84, 0xD7, 0xC1, 0xF6, 0x41, 0xFF, 0xB5, 0x5C,
        0x85, 0xD7, 0x02, 0xC7, 0x45, 0x00, 0xCD, 0x8C, 0x87, 0x06, 0x89, 0x76, 0x47, 0xE8, 0x01, 0xC5,
        0x85, 0xDC, 0x85, 0xB8, 0x07, 0xE0, 0x39, 0x6D, 0x87, 0x09, 0xCD, 0x68, 0xC9, 0xE7, 0x62, 0x05,
        0x86, 0xE0, 0x06, 0xFA, 0xCB, 0xDF, 0x61, 0x35, 0x87, 0x75, 0x91, 0x6B, 0x2E, 0xFF, 0x5A, 0x75,
        0x87, 0x13, 0xCE, 0x4A, 0xFF, 0xE7, 0x99, 0x85, 0x85, 0xD1, 0x43, 0xFE, 0xC9, 0x0F, 0x6D, 0x32,
        0x88, 0xE4, 0xC4, 0xAC, 0x3F, 0xF9, 0x9D, 0xEA, 0x87, 0x6A, 0xC4, 0x1C, 0xF6, 0x27, 0x69, 0xBA,
        0x85, 0x70, 0x86, 0xBC, 0xFF, 0xD7, 0x7A, 0xA5, 0x88, 0x1F, 0xC4, 0x7C, 0xFF, 0xE7, 0x16, 0x95,
        0x84, 0x5A, 0xC4, 0x19, 0xFE, 0x07, 0xA5, 0x95, 0x87, 0x7C, 0x0B, 0xFD, 0x2D, 0xF8, 0xC5, 0xF5,
        0x85, 0xD7, 0x84, 0xFC, 0xCD, 0xEF, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x33, 0x26, 0x19, 0x04, 0xB7, 0x42, 0x22, 0x7B, 0x52, 0x35,
        0x84, 0x42, 0x67, 0x73, 0xC2, 0x36, 0x86, 0x81, 0x95, 0x1C, 0x39, 0x36, 0x95, 0x13, 0x44, 0x24,
        0x6D, 0x35, 0x53, 0x42, 0x23, 0x94, 0x1A, 0x02, 0x47, 0x5A, 0x4C, 0xFF, 0x2F, 0xB8, 0xF2, 0x3F,
        0x22, 0x28, 0x6F, 0xFC, 0x5F, 0xD3, 0x72, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0x05, 0x85, 0x8F, 0x86,
    ])


    while True: 
        print("")
        print("0 Exit")
        print("1. LED ON/OFF")
        print("2. is_finger_pressed")
        print("3. make fingerprint template")
        print("4. enroll fingerprint to device memory")
        print("5. delete saved template from device (delite all/ delete by id)")
        print("6. identify / recognize fingerprint")
        print("7. settemplate - set a template data to device")
        print("8. check enrolled")
        print("9. Get Template")
        print("10. Identify Template")
        print("")
        task = int( input("Task: " )) 

        if task == 0:
            break
        #=#=# ---------------------------- T.A.S.K.S ---------------------------------- #=#=#
        # 1. turning ON & OFF LED
        if task == 1:
            # ON
            led = fp.set_led(True)
            print("\n |__ LED status :", led) 

            time.sleep(2)

            led = fp.set_led(False)
            print("\n |__ LED status :", led)
            
        # 2. check if finger is pressed or not
        if task == 2: 
            pressed = fp.is_finger_pressed()
            print("\n |__ is finger pressed ?", pressed)
            
        # 3. make fingerprint template
        if task == 3:
            data, downloadstat =fp.MakeTemplate()
            print(f"\n |__ Is template fetched ?", downloadstat)
            
            img_arr = []
            if downloadstat:
                data = bytearray(data)
                for ch in data:
                    img_arr.append(ch)
            print("fetched template data: ", img_arr)

        # 4. enroll fingerprint to device memory
        if task == 4:
            idx = int(input("Enter ID: "))
            if fp.is_finger_pressed():
                # Checking for finger press 
                print("\n |__Finger is pressed")
                # Starting enrollment 
                id,  downloadstat = await fp.enroll(lambda msg: print(msg) , idx=idx)
                print(f"\n |__ID: {id}")
                # To get total enrollment count
                print(f"\n |__ enrolled counts :", fp.get_enrolled_cnt())
                
        # 5. delete saved template from device (delite all/ delete by id)
        if task == 5:
            #status = fp.delete(idx=0) # delete by id
            print ("Enter -1 to Delete All, Otherwise enter the ID")
            idx = int(input("Enter ID: "))
            if idx == -1: 
                status = fp.deleteAll()
            else:
                status = fp.delete(idx)
                
            print("\n |__ Delete status: ", status)
            # To get total enrollment count
            print(f"\n |__ enrolled counts :", fp.get_enrolled_cnt())
            
        # 6. identify / recognize fingerprint
        if task == 6:
            id = fp.identify()
            print("\n |__ identified id:", id)
        

 
        # 7. settemplate - set a template data to device
        if task == 7:
            idx = int(input("Enter ID: "))

            
            DATA = test_template_data_14  #[] # a 502 length python list, that we get after running "task 3"
            fp.delete(idx=idx)
            status = fp.setTemplate(idx=idx, data=DATA)
            print("\n |__ set template status :", status)

        # 8. Check Enrolled
        if task == 8:
            idx = int(input("Enter ID: "))
            enrolled = fp.check_enrolled(idx)
            print("Enrolled:", enrolled)

        # 9. Get Template
        if task == 9:
            idx = int(input("Enter ID: "))
            data,success = fp.get_template(idx)
            if success:
                print(f"{fp.print_hex(data)}")
        #10 Identify Template 
        if task == 10:

            id = fp.identifyTemplate(test_template_data_14)
            print("\n |__ identified id:", id)
            
asyncio.run( main())