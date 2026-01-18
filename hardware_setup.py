from drivers.ssd1306.ssd1306 import SSD1306_I2C as SSD

import gc
from machine import Pin, I2C

from lib.gui.core.ugui import Display, Screen

import dht
from lib.hcsr04 import HCSR04


# ESP32 Pin assignment
screen_i2c = I2C(sda=Pin(2), scl=Pin(4))

oled_width = 128
oled_height = 64
gc.collect()  # Precaution before instantiating framebuf
ssd = SSD(oled_width, oled_height, screen_i2c)

# Create and export a Display instance
# Define control buttons
btn_nxt = Pin(21, Pin.IN, Pin.PULL_UP)  # Move to next control
btn_sel = Pin(19, Pin.IN, Pin.PULL_UP)  # Operate current control
btn_prev = Pin(18, Pin.IN, Pin.PULL_UP)  # Move to previous control
btn_inc = None
btn_dec = None
display = Display(ssd, btn_nxt, btn_sel, btn_prev, btn_inc, btn_dec)
Screen.do_gc = False

dist_sensor = HCSR04(trigger_pin=22, echo_pin=23, echo_timeout_us=10000)
temp_sensor = dht.DHT11(Pin(5, Pin.IN))
