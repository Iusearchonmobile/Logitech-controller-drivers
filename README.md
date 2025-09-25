## Logitech controller drivers
Made in python 3.11 (Windows 10)
## How to

To install the dependencies type into your console:
``
    pip3 install pyusb tkinter multiprocessing keyboard 
``

Now get the product id and vendor id of your logitech controller (vendor id is usually 0x046d), You can find tutorials on how to do that on youtube, Then put the product id and vendor id into the interpreter.py and test.py files, Now try to use the interpreter.py file, If you press the 10 button (the start button on other controllers) and a keyboard windows pops up then you dont have to do any reverse engineering!
But if that didnt work, run test.py and try to find the usb output data when you press a button (if you find a data output thing being output everytime you press any button then thats the idle data being sent) now that you have the usb output data now, Put the last 3 bytes in the BUTTON_MAP variable, and thats it

## For windows users
You need to use Zadig to actually replace the controller drivers from the regular system drivers to WinUsb

## What is this useful for?

This was made so you can make your old worthless logitech controller into a button bar! By opening the controller and replacing these coontroller buttons with regular buttons

## Troubleshooting

just use chatgpt dude
