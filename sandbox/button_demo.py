from machine import Pin
import time

button = Pin(27, Pin.IN, Pin.PULL_UP)
nxt = Pin(21, Pin.IN, Pin.PULL_UP)  # Move to next control
sel = Pin(19, Pin.IN, Pin.PULL_UP)  # Operate current control
prev = Pin(18, Pin.IN, Pin.PULL_UP)  # Move to previous control

while True:
    if not nxt.value():
        print("Nxt pressed!")
    elif not sel.value():
        print("Sel pressed!")
    elif not prev.value():
        print("Prev pressed!")
    else:
        print("...")
    time.sleep(0.1)
