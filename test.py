import argparse
import time
from fplib import fplib

# CLI argument parser
parser = argparse.ArgumentParser(description='GT-521Fx2 Fingerprint CLI')
parser.add_argument('--task', type=int, required=True, help='Task number to run (1-7)')
args = parser.parse_args()

# fingerprint module variables
fp = fplib()  # Start at 9600

# module initializing
init = fp.init()
print("is initialized:", init)

# Run only task that is specified
task = args.task

# #=#=# ---------------------------- T.A.S.K.S ---------------------------------- #=#=#
# 1. turning ON & OFF LED
if task == 1:
    led = fp.set_led(True)
    print("\n |__ LED status:", led)
    time.sleep(2)
    led = fp.set_led(False)
    print("\n |__ LED status:", led)

# 2. check if finger is pressed or not
if task == 2:
    pressed = fp.is_finger_pressed()
    print("\n |__ is finger pressed?", pressed)

# 3. make fingerprint template
if task == 3:
    data, downloadstat = fp.MakeTemplate()
    print(f"\n |__ Is template fetched?", downloadstat)

    img_arr = []
    if downloadstat:
        data = bytearray(data)
        for ch in data:
            img_arr.append(ch)
    print("fetched template data:", img_arr)



# 4. enroll fingerprint to device memory
if task == 4:
    if fp.is_finger_pressed():
        print("\n |__ Finger is pressed")
        id, data, downloadstat = fp.enroll()
        print(f"\n |__ ID: {id} & is captured?", data is not None)
        print(f"\n |__ enrolled count:", fp.get_enrolled_cnt())

# 5. delete saved template from device (delete all / delete by id)
if task == 5:
    # status = fp.delete(idx=0)  # delete by id
    status = fp.delete()  # delete all
    print("\n |__ Delete status:", status)
    print(f"\n |__ enrolled count:", fp.get_enrolled_cnt())

# 6. identify / recognize fingerprint
if task == 6:
    id = fp.identify()
    print("\n |__ identified id:", id)

# 7. settemplate - set a template data to device
if task == 7:
    DATA = []  # a 502 length python list, that we get after running "task 3"
    fp.delete(idx=0)
    status = fp.setTemplate(idx=0, data=DATA)
    print("\n |__ set template status:", status)

# 8. GetTemplateByID
if task == 8:
    idx = int(input("Enter ID to get template: "))
    data, ok = fp.GetTemplate(idx=idx)
    if not ok:
        print(f"Failed to get template for ID {idx}.")
    else:
        print(f"Fetched template for ID {idx} — length: {len(data)} bytes.")
        img_arr = []
        data = bytearray(data)
        for ch in data:
            img_arr.append(ch)
        print("Fetched template data:", img_arr)

if task == 9:
    print(f"\n |__ enrolled count:", fp.get_enrolled_cnt())

    # 9. List all enrolled IDs
if task == 10:  
    idx = int(input("Enter ID to check enrollment"))
    print("\n |__ Check ID ", idx) 
    enrolled = fp.CheckEnrolled(idx)
    print("\n |__ Enrolled :", enrolled)
