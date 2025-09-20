#kinda chatgpt skidded ig

import usb.core
import usb.util
import sys
import time
from ps4_keyboard import start_keyboard_service
import multiprocessing

#change these
#vendor id for logitech devices is usually 0x046d
VENDOR_ID = 0x046d
PRODUCT_ID = #add your product id here

REPEAT_DELAY = 0.05

command_queue = None

ACTION_MAP = {
    "Button 1 (X)": "1",
    "Button 2 (A)": "ok",
    "Button 3 (B)": "3",
    "Button 4 (Y)": "4",
    "Button 5 (L1)": "5",
    "Button 6 (R1)": "6",
    "Button 7 (L2)": "7",
    "Button 8 (R2)": "8",
    "Button 9 (Select)": "9",
    "Button 10 (Start)": "osk",
    "D-Pad Up": "up",
    "D-Pad Down": "down",
    "D-Pad Left": "left",
    "D-Pad Right": "right",
    "D-Pad (as Analog Stick)": "!",
}

HOLDABLE_ACTIONS = {"up", "down", "left", "right", "ok"}

def press(button):
    if not command_queue:
        return
    if button == "up":
        command_queue.put("UP")
    if button == "down":
        command_queue.put("DOWN")
    if button == "left":
        command_queue.put("LEFT")
    if button == "right":
        command_queue.put("RIGHT")
    if button == "osk":
        command_queue.put("TOGGLE")
    if button == "ok":
        command_queue.put("INSERT")

#the below might not be the same for everyone

BUTTON_MAP = {
    (8, 0, 252): "Idle",
    (24, 0, 252): "Button 1 (X)",
    (40, 0, 252): "Button 2 (A)",
    (72, 0, 252): "Button 3 (B)",
    (136, 0, 252): "Button 4 (Y)",
    (8, 1, 252): "Button 5 (L1)",
    (8, 2, 252): "Button 6 (R1)",
    (8, 4, 252): "Button 7 (L2)",
    (8, 8, 252): "Button 8 (R2)",
    (8, 16, 252): "Button 9 (Select)",
    (8, 32, 252): "Button 10 (Start)",
    (0, 0, 252): "D-Pad Up",
    (4, 0, 252): "D-Pad Down",
    (2, 0, 252): "D-Pad Right",
    (6, 0, 252): "D-Pad Left"
}


def main():
    global command_queue
    command_queue = start_keyboard_service()

    dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
    if dev is None:
        print(f"Logitech Gamepad (VID={hex(VENDOR_ID)}, PID={hex(PRODUCT_ID)}) not found.")
        sys.exit(1)

    try:
        dev.set_configuration()
    except usb.core.USBError:
        pass

    cfg = dev.get_active_configuration()
    intf = cfg[(0, 0)]
    ep = usb.util.find_descriptor(intf, custom_match=lambda e: usb.util.endpoint_direction(
        e.bEndpointAddress) == usb.util.ENDPOINT_IN)
    assert ep is not None, "Could not find an IN endpoint."

    print("driver started")

    last_event = "Idle"
    try:
        while True:
            try:
                data = dev.read(ep.bEndpointAddress, ep.wMaxPacketSize, timeout=50)
                button_key = (data[4], data[5], data[7])
                button_event = BUTTON_MAP.get(button_key, "Unknown Button")
                final_event = button_event
                action = ACTION_MAP.get(final_event)

                if action is not None:
                    if action in HOLDABLE_ACTIONS:
                        press(action)
                    elif final_event != last_event:
                        press(action)

                last_event = final_event

            except usb.core.USBError as e:
                if 'time' in str(e).lower():
                    last_event = "Idle"
                    pass
                else:
                    print(f"A reading error occurred: {e}")
                    time.sleep(1)

            time.sleep(REPEAT_DELAY)

    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        if command_queue:
            print("Shutting down on-screen keyboard service...")
            command_queue.put("SHUTDOWN")
            time.sleep(1)
        usb.util.dispose_resources(dev)
        print("USB resources released.")


if __name__ == '__main__':
    multiprocessing.freeze_support()

    main()
