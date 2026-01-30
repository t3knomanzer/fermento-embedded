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


def perform_reading(sensor, gas_buffer, t_buffer, rh_buffer, p_buffer):
    update_buffer(gas_buffer, sensor.gas)
    gas = average_buffer(gas_buffer)

    update_buffer(t_buffer, sensor.temperature)
    t = average_buffer(t_buffer)

    update_buffer(rh_buffer, sensor.relative_humidity)
    rh = average_buffer(rh_buffer)

    update_buffer(p_buffer, sensor.pressure)
    p = average_buffer(p_buffer)

    return (gas, t, rh, p)


def display_reading(display, gas, t, rh, p, msg=""):
    display.fill(0)
    display.text(msg, 0, 0, 1)
    display.text(f"T: {t:.1f}C", 0, 12, 1)
    display.text(f"RH:{rh:.1f}%", 0, 24, 1)
    display.text(f"P:{p:.1f} hPa", 0, 36, 1)
    display.text(f"Gas:{gas:.1f} ohm", 0, 48, 1)
    display.show()


def print_reading(gas, t, rh, p, msg=""):
    print(f"T: {t:.1f}C RH:{rh:.1f}% P:{p:.1f}hPa Gas:{gas:.1f}ohm - {msg} - ")


print("Creating sensor...")
sensor = bme680.Adafruit_BME680_I2C(i2c_bus)
sensor.humidity_oversample = 2
sensor.pressure_oversample = 4
sensor.temperature_oversample = 8
sensor.filter_size = 3
sensor.set_gas_heater(320, 150)

print("Start measuring")
warmup_period = 150_000  # 2.5 min
warmup_rate = 1_000  # 1s
maint_rate = 1_000  # keep warm (try 1s first)
log_interval = 60_000  # 5 min

gas = 0
gas_buffer = []
t_buffer = []
rh_buffer = []
p_buffer = []
max_samples = 3

start_ms = time.ticks_ms()
next_log_ms = time.ticks_add(start_ms, log_interval)

while True:
    now = time.ticks_ms()
    elapsed = time.ticks_diff(now, start_ms)

    # read once per loop cadence
    gas, t, rh, p = perform_reading(sensor, gas_buffer, t_buffer, rh_buffer, p_buffer)

    if elapsed < warmup_period:
        msg = f"Warming... {int((warmup_period - elapsed)/1000)}s"
        print_reading(gas, t, rh, p, msg)
        display_reading(display, gas, t, rh, p, msg)
        time.sleep_ms(warmup_rate)
        continue

    # RUNNING
    elif time.ticks_diff(now, next_log_ms) >= 0:
        next_log_ms = time.ticks_add(next_log_ms, log_interval)
        print_reading(gas, t, rh, p, "Logging")
        display_reading(display, gas, t, rh, p, "Logging")

    time.sleep_ms(maint_rate)
