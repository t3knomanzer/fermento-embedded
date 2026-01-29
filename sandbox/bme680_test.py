import time
from machine import Pin, I2C, reset
from drivers import ssd1306
from drivers import bme680

print("Setting up buttons")
btn_set = Pin(42, Pin.IN, Pin.PULL_UP)
btn_save = Pin(41, Pin.IN, Pin.PULL_UP)

print("Creating I2C bus...")
i2c_bus = I2C(0, sda=Pin(45), scl=Pin(47))

print("Creating display...")
display = ssd1306.SSD1306_I2C(128, 64, i2c_bus)


def update_buffer(buffer, value, max_items=3):
    buffer.append(value)
    if len(buffer) > max_items:
        buffer.pop(0)


def average_buffer(buffer):
    result = sum(buffer) / len(buffer)
    return result


gas = 0
gas_buffer = []
max_samples = 3
sensor = bme680.Adafruit_BME680_I2C(i2c_bus)


print("Start measuring")
while True:
    if btn_set.value() == 0:
        pass

    if btn_save.value() == 0:
        pass

    update_buffer(gas_buffer, sensor.gas)
    print(f"Gaas Samples: {gas_buffer}")
    gas = average_buffer(gas_buffer)
    print(f"Average gas: {gas} ohm")

    display.fill(0)
    display.text(f"Gas:{gas:.1f}ohm ", 0, 24, 1)
    display.show()
    time.sleep(1)
