from machine import Pin, I2C
from drivers import ssd1306
from drivers import sht4x
from drivers import scd4x

print("Creating I2C bus...")
i2c_bus = I2C(0, sda=Pin(45), scl=Pin(47))

print("Creating display...")
display = ssd1306.SSD1306_I2C(128, 64, i2c_bus)

print("Creating sensors...")
s_sht41 = sht4x.SHT4x(i2c_bus)
s_sht41.mode = sht4x.Mode.NOHEAT_HIGHPRECISION
s_scd4x = scd4x.SCD4X(i2c_bus)

while True:
    temperature, relative_humidity = s_sht41.measurements
    s_scd4x.measure_single_shot()
    display.fill(0)
    display.text(f"T:{temperature:.1f}C RH:{relative_humidity:.1f}%", 0, 28, 1)
    display.text(f"CO2:{s_scd4x.CO2:.1f}ppm", 0, 40, 1)
    display.show()
