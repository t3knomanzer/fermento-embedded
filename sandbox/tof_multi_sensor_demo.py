import time
from machine import I2C, Pin
from drivers import vl6180x, vl53l0x

VL53_ID = 0
VL618_ID = 1
VL53_XSHUT = 13
VL618_SHDN = 12

VL53_DEFAULT_MODE = 30000
VL53_HIGH_ACCURACY = 200000
VL53_LONG_RANGE = 33000
VL53_HIGH_SPEED = 20000

print("Setting up shutdown pins...")
vl53_enable = Pin(VL53_XSHUT, Pin.OUT)
vl618_enable = Pin(VL618_SHDN, Pin.OUT)

print("Creating I2C bus...")
i2c = I2C(0, sda=Pin(2), scl=Pin(4))


def enable_sensor(id):
    if id == VL53_ID:
        vl618_enable.value(0)
        vl53_enable.value(1)
        return vl53l0x.VL53L0X(i2c)
    elif id == VL618_ID:
        vl618_enable.value(1)
        vl53_enable.value(0)
        return vl6180x.VL6180X(i2c)


def set_timing_budget(sensor, value):
    sensor.measurement_timing_budget = value
    print(f"Setting timing budget to {value}...")


def read_single(sensor):
    return sensor.range


def read_median(sensor):
    count = 9
    result = []
    for i in range(count):
        sample = read_single(sensor)
        result.append(sample)
    median = sorted(result)[5]
    return result, median


def run_median():
    sensor = enable_sensor(VL53_ID)
    set_timing_budget(sensor, VL53_HIGH_ACCURACY)
    result = read_median(sensor)
    print(f"VL53 result: {result[1]} Spread:{max(result[0]) - min(result[0])}")

    sensor = enable_sensor(VL618_ID)
    result = read_median(sensor)
    print(f"VL618 result: {result[1]} Spread:{max(result[0]) - min(result[0])}")


print("Reading sensors...")
result = run_median()
