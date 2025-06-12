from fingerprint import FingerprintScanner
import time

def main():
    scanner = FingerprintScanner('/dev/serial0', 9600)

    print("GT-521Fx2 Console Control - FULL")
    print("Available commands:")
    print("""
 open, close, led_on, led_off
 capture, identify, verify, verify_template, identify_template
 is_press_finger, wait_for_finger_press, wait_for_finger_release
 get_image, get_raw_image, cancel
 get_user_count, delete_id, delete_all
 get_template, set_template
 set_security, get_security
 module_info
 enroll, exit
""")

    while True:
        cmd = input("Command> ").strip().lower()

        if cmd == "open":
            scanner.open()
        elif cmd == "close":
            scanner.close()
        elif cmd == "led_on":
            scanner.led_on()
        elif cmd == "led_off":
            scanner.led_off()
        elif cmd == "capture":
            scanner.capture()
        elif cmd == "identify":
            scanner.identify()
        elif cmd == "verify":
            enroll_id = int(input(" Enter Enroll ID to verify (0~2999): "))
            scanner.verify(enroll_id)
        elif cmd == "verify_template":
            scanner.verify_template()
        elif cmd == "identify_template":
            scanner.identify_template()
        elif cmd == "is_press_finger":
            scanner.is_press_finger()
        elif cmd == "wait_for_finger_press":
            scanner.wait_for_finger_press()
        elif cmd == "wait_for_finger_release":
            scanner.wait_for_finger_release()
        elif cmd == "get_image":
            scanner.get_image()
        elif cmd == "get_raw_image":
            scanner.get_raw_image()
        elif cmd == "cancel":
            scanner.cancel()
        elif cmd == "get_user_count":
            scanner.get_template_count()
        elif cmd == "delete_id":
            enroll_id = int(input(" Enter Enroll ID to delete (0~2999): "))
            scanner.delete_id(enroll_id)
            print(f"Deleted ID {enroll_id}")
        elif cmd == "delete_all":
            scanner.delete_all()
        elif cmd == "get_template":
            scanner.get_template()
        elif cmd == "set_template":
            scanner.set_template()
        elif cmd == "set_security":
            level = int(input(" Enter Security Level (1~5): "))
            scanner.set_security_level(level)
        elif cmd == "get_security":
            scanner.get_security_level()
        elif cmd == "module_info":
            scanner.get_device_info()
        elif cmd == "enroll":
            enroll_id = int(input(" Enter Enroll ID (0~2999): "))
            scanner.enroll_start(enroll_id)
            print(" Place finger for step 1")
            scanner.wait_for_finger_press()
            scanner.enroll_step(0x0023)
            scanner.wait_for_finger_release()
            print(" Place finger for step 2")
            scanner.wait_for_finger_press()
            scanner.enroll_step(0x0024)
            scanner.wait_for_finger_release()
            print(" Place finger for step 3")
            scanner.wait_for_finger_press()
            scanner.enroll_step(0x0025)
            scanner.wait_for_finger_release()
            print(f" Enroll complete for ID {enroll_id}")
        elif cmd == "exit":
            print("Exiting...")
            break
        else:
            print("Unknown command. Please try again.")

    del scanner

if __name__ == "__main__":
    main()
