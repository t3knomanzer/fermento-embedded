import gc
import sys
from machine import Pin, I2C
import time
import neopixel


from app.services.log import LogServiceManager
from app.utils import memory

# Create logger
logger = LogServiceManager.get_logger(name=__name__)

# Turn off onboard LED
led = neopixel.NeoPixel(Pin(48), 1)
led.fill((0, 0, 0))
led.write()


# We log a lot of information in this file since many things could go wrong
# while creating and initializing the hardware.
logger.info("Importing SSD1306 driver...")
from drivers.ssd1306 import SSD1306_I2C as SSD

logger.info("Importing VL53L4CD driver...")
from drivers.vl53l4cd import VL53L4CD

logger.info("Importing SCD4X driver...")
from drivers.scd4x import SCD4X

logger.info("Importing SHT40 driver...")
from drivers.sht4x import SHT4x

logger.info("Importing gui...")
from lib.gui.core.ugui import Display, Screen

memory.print_mem()

logger.info("Creating I2C bus...")
i2c_bus = I2C(0, sda=Pin(45), scl=Pin(47))

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

logger.info("Creating TOF sensor...")
tof_sensor = None
retries = 3
while not tof_sensor and retries > 0:
    try:
        tof_sensor = VL53L4CD(i2c_bus)
    except Exception as e:
        logger.error(f"({retries}) Error creating TOF sensor. {e}")
        retries -= 1
        time.sleep(1)

if tof_sensor is None:
    logger.critical("Couldn't create TOF sensor.")
    sys.exit()

logger.info("Creating SCD41 sensor...")
sdc41 = SCD4X(i2c_bus)

logger.info("Creating SHT40 sensor...")
sht40 = SHT4x(i2c_bus)

logger.info("Creating button pins...")
btn_nxt = Pin(41, Pin.IN, Pin.PULL_UP)
btn_sel = Pin(42, Pin.IN, Pin.PULL_UP)
btn_prev = None
btn_inc = None
btn_dec = None

logger.info("Creating Display object...")
display = Display(ssd, btn_nxt, btn_sel, btn_prev, btn_inc, btn_dec)
Screen.do_gc = False

memory.print_mem()
