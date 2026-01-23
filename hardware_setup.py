import gc
from machine import Pin, I2C
import time

from app.services.log import LogServiceManager
from app.utils import memory

# Create logger
logger = LogServiceManager.get_logger(name=__name__)

# We log a lot of information in this file since many things could go wrong
# while creating and initializing the hardware.
logger.info("Importing SSD1306 driver...")
from drivers.ssd1306 import SSD1306_I2C as SSD

logger.info("Importing VL53L0X driver...")
from drivers.vl53l0x import VL53L0X

logger.info("Importing DHT driver...")
import dht

logger.info("Importing gui...")
from lib.gui.core.ugui import Display, Screen

logger.info("Creating I2C bus...")
i2c_bus = I2C(0, sda=Pin(2), scl=Pin(4))

logger.info("Creating SSD...")
oled_width = 128
oled_height = 64
ssd = None
retries = 3
gc.collect()
while not ssd and retries > 0:
    try:
        ssd = SSD(oled_width, oled_height, i2c_bus)
    except Exception as e:
        logger.error(f"({retries}) Error creating SSD")
        retries -= 1
        time.sleep(1)

logger.info("Creating tof sensor...")
tof_sensor = None
retries = 3
while not tof_sensor and retries > 0:
    try:
        tof_sensor = VL53L0X(i2c_bus)
        tof_sensor.measurement_timing_budget = 200000  # High Accuracy

    except Exception as e:
        logger.error(f"({retries}) Error creating range sensor")
        retries -= 1
        time.sleep(1)

logger.info("Creating ambient sensor...")
ambient_sensor = dht.DHT22(Pin(5, Pin.IN))

logger.info("Creating button pins...")
btn_nxt = Pin(18, Pin.IN, Pin.PULL_UP)
btn_sel = Pin(19, Pin.IN, Pin.PULL_UP)
btn_prev = None
btn_inc = None
btn_dec = None

logger.info("Creating Display object...")
display = Display(ssd, btn_nxt, btn_sel, btn_prev, btn_inc, btn_dec)
Screen.do_gc = False
