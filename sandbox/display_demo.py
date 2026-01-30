from machine import Pin, I2C
from drivers import ssd1306

# using default address 0x3C
i2c = I2C(sda=Pin(2), scl=Pin(4))

try:
    display = ssd1306.SSD1306_I2C(128, 64, i2c)
    display.text("Hello, World!", 0, 0, 1)
    display.show()
except OSError:
    print("Display not found")
