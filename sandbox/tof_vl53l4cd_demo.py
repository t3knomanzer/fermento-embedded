import time
from machine import I2C, Pin
from drivers.vl53l4cd import VL53L4CD

# from lib import busio

print("Creating I2C bus...")
i2c_bus = I2C(0, sda=Pin(45), scl=Pin(47))

print("Creating sensor...")
sensor = VL53L4CD(i2c_bus)

HIGH_ACCURACY = 200
LONG_RANGE = 33
HIGH_SPEED = 20


def set_timing_budget(mode):
    sensor.stop_ranging()
    sensor.timing_budget = mode
    sensor.start_ranging()
    print(f"Setting timing budget to {mode}...")


def read_single():
    result = sensor.distance
    sensor.clear_interrupt()
    return result


def read_median():
    count = 9
    result = []
    for i in range(count):
        sample = read_single()
        result.append(sample)
    median = sorted(result)[5]
    return result, median


def read_average():
    count = 9
    results = []
    for i in range(count):
        sample = read_single()
        results.append(sample)
    average = sum(results) / count
    return results, average


def run(time_s=10, method=read_median, accuracy=HIGH_ACCURACY):
    set_timing_budget(accuracy)
    start_ticks = time.ticks_ms()
    results = []
    while time.ticks_diff(time.ticks_ms(), start_ticks) < time_s * 1000:
        result = method()
        results.append(result[1])
        print(f"Result: {result[1]} Spread:{max(result[0]) - min(result[0])}")
        time.sleep(0.1)

    print(
        f"Total max: {max(results)} min: {min(results)} spread: {max(results) - min(results)} "
    )
