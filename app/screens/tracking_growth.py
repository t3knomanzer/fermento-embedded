import asyncio
import gc
import time

from app.models.feeding_progress import FeedingProgressModel
from app.services.log import LogServiceManager
from app.utils import memory
from app.utils.filtering import TofDistanceFilter
import config
from drivers import sht4x
from hardware_setup import tof_sensor, sdc41, bme680, sht40
import lib.gui.fonts.freesans20 as large_font
import lib.gui.fonts.arial10 as small_font
from lib.gui.core.colors import BLACK, WHITE
from lib.gui.core.ugui import Screen, ssd
from lib.gui.widgets.buttons import Button
from lib.gui.widgets.label import Label
from lib.gui.core.writer import Writer
from app.services.db import DBService

# Create logger
logger = LogServiceManager.get_logger(name=__name__)


class TrackingGrowthScreen(Screen):
    STATE_STOPPED = 0
    STATE_RUNNING = 1

    def __init__(self, feeding_id, starter_name, jar_name, jar_distance):
        logger.debug(
            f"Received feeding:{feeding_id} starter:{starter_name} jar:{jar_name} jar height:{jar_distance}"
        )
        self._feeding_id = feeding_id
        self._starter_name = starter_name
        self._jar_name = jar_name
        self._jar_distance = jar_distance
        self._starting_distance = None
        self._current_distance = 0
        self._temperature = 0
        self._rh = 0
        self._co2 = 0
        self._state = TrackingGrowthScreen.STATE_STOPPED
        self._timer_state = TrackingGrowthScreen.STATE_STOPPED
        self._elapsed_seconds = 0
        self._elapsed_minutes = 0
        self._elapsed_hours = 0

        self._db_service = DBService()
        self._tof_sensor = tof_sensor
        self._scd41_sensor = sdc41
        self._bme680_sensor = bme680
        self._sht40 = sht40

        self._large_writer = Writer(ssd, large_font, verbose=False)
        self._small_writer = Writer(ssd, small_font, verbose=False)
        super().__init__()

        # UI widgets
        # Top left (temperature)
        width = ssd.width // 3
        self._temperature_lbl = Label(
            self._small_writer, row=2, col=2, text=width, justify=Label.LEFT
        )
        self._temperature_lbl.value("0C")

        # Top center (distance)
        row = ssd.height - self._small_writer.height - 2
        col = ssd.width // 3
        self._distance_lbl = Label(
            self._small_writer, row=2, col=col, text=width, justify=Label.CENTRE
        )
        self._distance_lbl.value("0mm")

        # Top right (humidity)
        row = 2
        col = ssd.width // 3 * 2
        self._rh_lbl = Label(
            self._small_writer, row=2, col=col, text=width, justify=Label.RIGHT
        )
        self._rh_lbl.value("0%")

        # Center left (growth)
        width = ssd.width // 2
        row = ssd.height // 2 - self._large_writer.height // 2
        self._growth_lbl = Label(
            self._large_writer, row=row, col=0, text=width, justify=Label.LEFT
        )
        self._growth_lbl.value("0%")

        # Center right (start/stop)
        width = ssd.width // 2 - 8
        height = self._small_writer.height + 8
        col = ssd.width // 2 + 4
        self._btn = Button(
            self._small_writer,
            row=row,
            col=col,
            text="Start",
            width=width,
            height=height,
            callback=self.start_stop_callback,
        )

        # Bottom left (starter name)
        width = ssd.width // 3
        row = ssd.height - self._small_writer.height - 2
        self._starter_lbl = Label(
            self._small_writer, row=row, col=2, text=width, justify=Label.LEFT
        )
        self._starter_lbl.value(self._starter_name)

        # Bottom center  (time elapsed)
        col = ssd.width // 3
        self._time_lbl = Label(
            self._small_writer, row=row, col=col, text=width, justify=Label.CENTRE
        )
        self._time_lbl.value("00:00:00")

        # Bottom right (jar name)
        col = ssd.width // 3 * 2
        self._jar_lbl = Label(
            self._small_writer, row=row, col=col, text=width, justify=Label.RIGHT
        )
        self._jar_lbl.value(self._jar_name)

    def after_open(self):
        asyncio.create_task(self.run())

    def set_sensor_preview_settings(self):
        self._tof_samples = config.TOF_SAMPLES_PREVIEW
        self._tof_sensor.measurement_timing_budget = config.TOF_TIMING_PREVIEW
        self._scd41_sensor.stop_periodic_measurement()
        self._scd41_sensor.start_periodic_measurement()

    def set_sensor_running_settings(self):
        self._tof_samples = config.TOF_SAMPLES_RUNNING
        self._tof_sensor.measurement_timing_budget = config.TOF_TIMING_RUNNING
        self._scd41_sensor.stop_periodic_measurement()
        self._scd41_sensor.start_low_periodic_measurement()

    async def run(self):
        logger.info("Tracking...")
        # Set sensor preview settings when we first start
        logger.debug("Setting sensor settings to PREVIEW")
        self.set_sensor_preview_settings()
        self._scd41_sensor.mode = sht4x.Mode.NOHEAT_HIGHPRECISION
        # change this to match the location's pressure (hPa) at sea level
        self._bme680_sensor.sea_level_pressure = 1013.25

        # Compute environment only once at the beginning if we are not running.
        self.compute_environment()

        # Main loop
        while type(Screen.current_screen) == TrackingGrowthScreen:
            if self._state == TrackingGrowthScreen.STATE_RUNNING:
                # We start the timer async since it updates at a different interval.
                if self._timer_state == TrackingGrowthScreen.STATE_STOPPED:
                    self._timer_state = TrackingGrowthScreen.STATE_RUNNING
                    asyncio.create_task(self.update_time())

                logger.info("Gathering sensor data...")
                self.compute_environment()
                self.compute_distance()
                self.compute_growth()

                logger.info("Submitting data...")
                gc.collect()
                self.submit_data()
                await asyncio.sleep(config.RUNNING_UPDATE_DELAY)

            elif self._state == TrackingGrowthScreen.STATE_STOPPED:
                self.compute_distance()
                await asyncio.sleep(config.PREVIEW_UPDATE_DELAY)

    def start_stop_callback(self, btn):
        asyncio.create_task(self.start_stop_async())

    async def start_stop_async(self):
        if self._state == TrackingGrowthScreen.STATE_STOPPED:
            logger.debug("Changing state to RUNNING")
            # Changing the text property doesn't force an update
            self._btn.text = "Stop"
            self._btn.show()
            await asyncio.sleep(0.1)
            self._state = TrackingGrowthScreen.STATE_RUNNING

            logger.debug("Setting sensor settings to RUNNING")
            self.set_sensor_running_settings()

        elif self._state == TrackingGrowthScreen.STATE_RUNNING:
            logger.debug("Changing state to STOPPED")
            self._state = TrackingGrowthScreen.STATE_STOPPED
            logger.debug("Stopping sensors")
            self._scd41_sensor.stop_periodic_measurement()
            Screen.back()

    def compute_environment(self):
        logger.info("Gathering SCD41 data...")
        while not self._scd41_sensor.data_ready:
            time.sleep(0.1)

        self._temperature = self._scd41_sensor.temperature
        self._rh = self._scd41_sensor.relative_humidity
        self._co2 = self._scd41_sensor.CO2
        logger.info(
            f"SCD41 - T:{self._temperature:.1f}C RH: {self._rh:.1f}% CO2: {self._co2}ppm"
        )

        logger.info("Gathering BME680 data...")
        logger.info(
            f"BME680 - T:{self._bme680_sensor.temperature:.1f}C RH: {self._bme680_sensor.humidity:.1f}% Gas: {self._bme680_sensor.gas} Ohm"
        )
        logger.info(
            f"BME680 - Altitude:{self._bme680_sensor.altitude:.1f} Pressure: {self._bme680_sensor.pressure:.1f} Si"
        )

        logger.info("Gathering SHT40 data...")
        t, rh = self._sht40.measurements
        logger.info(f"SHT40 - T:{t:.1f}C RH: {rh:.1f}%")

        self._temperature_lbl.value(f"{self._temperature:.1f}C")
        self._rh_lbl.value(f"{self._rh:.1f}%")

    def compute_distance(self):
        distance = 0

        # Take the samples and compute the average.
        for i in range(self._tof_samples):
            distance += self._tof_sensor.range

        # Just in case, in the case where distance = 0
        try:
            raw_avg_distance = distance // self._tof_samples
        except ZeroDivisionError:
            raw_avg_distance = 0

        # Once we are running, save the first sample as the starting distance.
        if self._state == TrackingGrowthScreen.STATE_RUNNING:
            if self._starting_distance is None:
                self._starting_distance = raw_avg_distance

        # Update the label.
        self._current_distance = raw_avg_distance
        self._distance_lbl.value(f"{self._current_distance} mm")

    def compute_growth(self):
        initial_size = self._jar_distance - self._starting_distance
        growth_size = self._starting_distance - self._current_distance
        print(f"initial size {initial_size} growth size {growth_size}")
        try:
            growth_percent = growth_size / initial_size * 100.0
        except ZeroDivisionError:
            growth_percent = 0

        self._growth_lbl.value(f"{int(growth_percent)}%")
        logger.info(f"Growth: {growth_percent}")

    async def update_time(self):
        elapsed_seconds = 0
        while type(Screen.current_screen) == TrackingGrowthScreen:
            await asyncio.sleep(1)
            elapsed_seconds += 1
            h, rem = divmod(elapsed_seconds, 3600)
            m, s = divmod(rem, 60)
            self._time_lbl.value(f"{h:02d}:{m:02d}:{s:02d}")

    def submit_data(self):
        model = FeedingProgressModel(
            self._feeding_id,
            self._temperature,
            self._rh / 100,
            self._co2,
            self._starting_distance,
            self._current_distance,
        )
        logger.info(
            f"Submitting data: feeding: {self._feeding_id} T: {self._temperature} RH: {self._rh}% CO2: {self._co2}ppm starting distance:{self._starting_distance} cur distance: {self._current_distance}"
        )
        memory.print_mem()
        self._db_service.create_feeding_progress(model)
