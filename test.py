from gt521f52_helper import GT521F52Helper
import time

gt = GT521F52Helper(port="/dev/serial0", baudrate=115200 )

# Step 1: Open
gt.open()

# Step 2: Set Serial Param (can repeat if needed)
gt.set_serial_param()
time.sleep(0.2)
gt.set_serial_param()
time.sleep(0.2)

# Step 3: Open again
gt.open()

# Step 4: Get Device Info
gt.get_device_info()

# Step 5: LED ON test
gt.led_on()

# Wait to see LED ON
time.sleep(3)

# Step 6: LED OFF
gt.led_off()

# Close port
gt.close()
