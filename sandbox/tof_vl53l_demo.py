import time
from machine import I2C, Pin
from drivers.vl53l0x import VL53L0X

# from lib import busio

print("Creating I2C bus...")
i2c = I2C(0, sda=Pin(2), scl=Pin(4))

print("Creating sensor...")
sensor = VL53L0X(i2c)

DEFAULT_MODE = 30000
HIGH_ACCURACY = 200000
LONG_RANGE = 33000
HIGH_SPEED = 20000


def set_timing_budget(mode):
    sensor.measurement_timing_budget = mode
    print(f"Setting timing budget to {mode}...")


def read_single():
    return sensor.range


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


def run_median():
    print("--- Many HIGH_SPEED accuracy mode ---")
    set_timing_budget(HIGH_SPEED)
    result = read_median()
    print(f"Result: {result[1]} Spread:{max(result[0]) - min(result[0])}")

    print("--- Many HIGH_ACCURACY mode ---")
    set_timing_budget(HIGH_ACCURACY)
    result = read_median()
    print(f"Result: {result[1]} Spread:{max(result[0]) - min(result[0])}")


def run_average():
    print("--- Average High Speed accuracy mode ---")
    set_timing_budget(HIGH_SPEED)
    result = read_average()
    print(f"Result: {result[1]} Spread:{max(result[0]) - min(result[0])}")

    print("--- Average High accuracy mode ---")
    set_timing_budget(HIGH_ACCURACY)
    result = read_average()
    print(f"Result: {result[1] - 10} Spread:{max(result[0]) - min(result[0])}")
