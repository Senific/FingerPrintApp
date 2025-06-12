from fingerprint import FingerprintScanner
import time

def main():
    scanner = FingerprintScanner('/dev/serial0', 9600)

    print("GT-521Fx2 Console Control")
    print("Available commands:")
    print(" open, close, led_on, led_off, capture, identify, enroll, delete, exit")

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
        elif cmd == "enroll":
            enroll_id = int(input(" Enter Enroll ID (0~2999): "))
            scanner.enroll_start(enroll_id)
            print(" Place finger for step 1")
            input(" Press Enter when ready...")
            scanner.enroll_step(0x0023)
            print(" Place finger for step 2")
            input(" Press Enter when ready...")
            scanner.enroll_step(0x0024)
            print(" Place finger for step 3")
            input(" Press Enter when ready...")
            scanner.enroll_step(0x0025)
            print(f" Enroll complete for ID {enroll_id}")
        elif cmd == "delete":
            enroll_id = int(input(" Enter Enroll ID to delete (0~2999): "))
            scanner.delete_id(enroll_id)
            print(f" Deleted ID {enroll_id}")
        elif cmd == "exit":
            print("Exiting...")
            break
        else:
            print("Unknown command. Please try again.")

    del scanner

if __name__ == "__main__":
    main()
