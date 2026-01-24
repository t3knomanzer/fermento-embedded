import gc
import sys
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

memory.print_mem()

logger.info("Creating I2C bus...")
i2c_bus = I2C(0, sda=Pin(2), scl=Pin(4))

logger.info("Creating SSD...")
oled_width = 128
oled_height = 64
ssd = None
retries = 3
while not ssd and retries > 0:
    try:
        gc.collect()
        ssd = SSD(oled_width, oled_height, i2c_bus)
    except Exception as e:
        logger.error(f"({retries}) Error creating SSD. {e}")
        retries -= 1
        time.sleep(1)

if ssd is None:
    logger.critical("Couldn't create SSD.")
    sys.exit()

logger.info("Creating tof sensor...")
tof_sensor = None
retries = 3
while not tof_sensor and retries > 0:
    try:
        tof_sensor = VL53L0X(i2c_bus)
    except Exception as e:
        logger.error(f"({retries}) Error creating range sensor. {e}")
        retries -= 1
        time.sleep(1)

if tof_sensor is None:
    logger.critical("Couldn't create TOF sensor.")
    sys.exit()

logger.info("Creating ambient sensor...")
trh_sensor = None
retries = 3
while not trh_sensor and retries > 0:
    try:
        trh_sensor = dht.DHT22(Pin(5, Pin.IN))
    except Exception as e:
        logger.error(f"({retries}) Error creating TRH sensor. {e}")
        retries -= 1
        time.sleep(1)

if trh_sensor is None:
    logger.critical("Couldn't create TRH sensor.")
    sys.exit()

logger.info("Creating button pins...")
btn_nxt = Pin(18, Pin.IN, Pin.PULL_UP)
btn_sel = Pin(19, Pin.IN, Pin.PULL_UP)
btn_prev = None
btn_inc = None
btn_dec = None

logger.info("Creating Display object...")
display = Display(ssd, btn_nxt, btn_sel, btn_prev, btn_inc, btn_dec)
Screen.do_gc = False

memory.print_mem()
