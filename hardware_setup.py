import time

print("importing SSD1306 driver...")
from drivers.ssd1306 import SSD1306_I2C as SSD

print("importing VL53L0X driver...")
from drivers.VL53L0X import VL53L0X

print("importing DHT driver...")
import dht

import gc
from machine import Pin, I2C

from lib.gui.core.ugui import Display, Screen

print("Creating I2C bus...")
i2c_bus = I2C(0, sda=Pin(2), scl=Pin(4))

oled_width = 128
oled_height = 64

print("Creating SSD...")
ssd = None
while not ssd:
    try:
        gc.collect()  # Precaution before instantiating framebuf
        ssd = SSD(oled_width, oled_height, i2c_bus)
    except Exception as e:
        print(f"Error {e}")
        time.sleep(1)

print("Creating tof sensor...")
Pin(15, Pin.IN, Pin.PULL_UP)
distance_sensor = None
while not distance_sensor:
    try:
        distance_sensor = VL53L0X(i2c_bus)
    except Exception as e:
        print(f"Error {e}")
        time.sleep(1)

print("Creating ambient sensor...")
ambient_sensor = dht.DHT11(Pin(5, Pin.IN))

print("Creating button pins...")
btn_nxt = Pin(18, Pin.IN, Pin.PULL_UP)
btn_sel = Pin(19, Pin.IN, Pin.PULL_UP)
btn_prev = None
btn_inc = None
btn_dec = None

print("Creating Display object...")
display = Display(ssd, btn_nxt, btn_sel, btn_prev, btn_inc, btn_dec)
Screen.do_gc = False
