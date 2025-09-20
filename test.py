import usb.core
import usb.util
import sys

#change these
#vendor id for logitech devices is usually 0x046d

VENDOR_ID = 0x046D
PRODUCT_ID = 0xC216

# Find the device
dev = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)

if dev is None:
    raise ValueError(
        "Device not found. Make sure it's connected, the IDs are correct, and the Zadig driver is installed.")

try:
    dev.set_configuration()
except usb.core.USBError as e:
    if e.errno == 13:
        print("config already set")
    else:
        sys.exit(f"couldnt set configuration: {e}")

cfg = dev.get_active_configuration()
intf = cfg[(0, 0)]

ep = usb.util.find_descriptor(
    intf,
    # match the first IN endpoint
    custom_match= \
        lambda e: \
            usb.util.endpoint_direction(e.bEndpointAddress) == \
            usb.util.ENDPOINT_IN)

assert ep is not None, "Input endpoint not found. The device may not have one."

print("Reading data from controller...")
print("Press some buttons or move the sticks.")
print("Press Ctrl+C to stop.")

try:
    while True:
        try:
            data = dev.read(ep.bEndpointAddress, ep.wMaxPacketSize, timeout=5000)

            hex_data = ' '.join([f'{byte:02x}' for byte in data])
            print(f"Raw: {data} | Hex: {hex_data}")

        except usb.core.USBError as e:
            if e.args == ('Operation timed out',):
                print("Timeout: No data received. Press a button.")
                continue

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    # release the device
    usb.util.dispose_resources(dev)