import asyncio
import gc
import time

from app.models.feeding_progress import FeedingProgressModel
from app.services.log import LogServiceManager
from app.utils import memory
from app.utils.filtering import TofDistanceFilter
from app.services.db import DBService
import config
from drivers import sht4x
from hardware_setup import tof_sensor, sdc41, sht40, bme680

import lib.gui.fonts.freesans20 as large_font
import lib.gui.fonts.arial10 as small_font
from lib.gui.core.colors import BLACK, WHITE
from lib.gui.core.ugui import Screen, ssd
from lib.gui.widgets.buttons import Button
from lib.gui.widgets.label import Label
from lib.gui.core.writer import Writer


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
        self._gas = 0
        self._state = TrackingGrowthScreen.STATE_STOPPED
        self._timer_state = TrackingGrowthScreen.STATE_STOPPED
        self._elapsed_seconds = 0
        self._elapsed_minutes = 0
        self._elapsed_hours = 0

        self._db_service = DBService()
        self._tof_sensor = tof_sensor
        self._scd41_sensor = sdc41
        self._sht40 = sht40
        self._bme680 = bme680

        self._tof_filter = TofDistanceFilter()

        self._large_writer = Writer(ssd, large_font, verbose=False)
        self._small_writer = Writer(ssd, small_font, verbose=False)
        super().__init__()

        # UI widgets
        # Bottom left (temperature)
        row = ssd.height - self._small_writer.height - 2
        width = ssd.width // 3
        self._temperature_lbl = Label(
            self._small_writer, row=row, col=2, text=width, justify=Label.LEFT
        )
        self._temperature_lbl.value("0C")

        # Bottom center (distance)
        col = ssd.width // 3
        # self._distance_lbl = Label(
        #     self._small_writer, row=row, col=col, text=width, justify=Label.CENTRE
        # )
        # self._distance_lbl.value("0mm")
        self._co2_lbl = Label(
            self._small_writer, row=row, col=col, text=width, justify=Label.CENTRE
        )
        self._co2_lbl.value("0ppm")

        # Bottom right (humidity)
        col = ssd.width // 3 * 2
        self._rh_lbl = Label(
            self._small_writer, row=row, col=col, text=width, justify=Label.RIGHT
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

        # Top left (starter name)
        width = ssd.width // 3
        row = 2
        self._starter_lbl = Label(
            self._small_writer, row=row, col=2, text=width, justify=Label.LEFT
        )
        self._starter_lbl.value(self._starter_name)

        # Top center  (time elapsed)
        col = ssd.width // 3
        self._time_lbl = Label(
            self._small_writer, row=row, col=col, text=width, justify=Label.CENTRE
        )
        self._time_lbl.value("00:00:00")

        # Top right (jar name)
        col = ssd.width // 3 * 2
        self._jar_lbl = Label(
            self._small_writer, row=row, col=col, text=width, justify=Label.RIGHT
        )
        self._jar_lbl.value(self._jar_name)

    def after_open(self):
        asyncio.create_task(self.run())

    def init_sensors(self):
        self._tof_sensor.stop_ranging()
        self._tof_samples = config.TOF_SAMPLES
        self._tof_sensor.timing_budget = config.TOF_TIMING_BUDGET
        self._tof_sensor.inter_measurement = 0
        self._tof_sensor.start_ranging()

        self._scd41_sensor.stop_periodic_measurement()
        self._scd41_sensor.mode = sht4x.Mode.NOHEAT_HIGHPRECISION
        self._scd41_sensor.start_low_periodic_measurement()

    async def run(self):
        logger.info("Tracking...")
        # Set sensor preview settings when we first start
        logger.debug("Initializing sensors...")
        self.init_sensors()

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
                await asyncio.sleep(config.LIVE_UPDATE_DELAY)

            elif self._state == TrackingGrowthScreen.STATE_STOPPED:
                self.compute_environment()
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

        elif self._state == TrackingGrowthScreen.STATE_RUNNING:
            logger.debug("Changing state to STOPPED")
            self._state = TrackingGrowthScreen.STATE_STOPPED
            logger.debug("Stopping sensors")
            self._scd41_sensor.stop_periodic_measurement()
            self._tof_sensor.stop_ranging()
            Screen.back()

    def compute_environment(self):
        if self._scd41_sensor.data_ready:
            logger.info("Gathering CO2 data...")
            self._co2 = self._scd41_sensor.CO2

        logger.info("Gathering gas data...")
        self._gas = self._bme680.gas

        logger.info("Gathering temp/rh data...")
        self._temperature, self._rh = self._sht40.measurements
        logger.info(
            f"T:{self._temperature:.1f}C RH:{self._rh:.1f}% CO2:{self._co2}ppm Gas:{self._gas}ohm"
        )

        self._temperature_lbl.value(f"{self._temperature:.1f}C")
        self._rh_lbl.value(f"{self._rh:.1f}%")
        self._co2_lbl.value(f"{self._co2}ppm")

    def sample_average(self, num_samples):
        distance = 0
        for i in range(num_samples):
            while (
                not self._tof_sensor.data_ready
                and not self._tof_sensor.range_status == 0
            ):
                logger.debug(
                    f"Ready: {self._tof_sensor.data_ready} Status: {self._tof_sensor.range_status}"
                )

            distance += self._tof_sensor.distance
            self._tof_sensor.clear_interrupt()

        result = distance // num_samples
        return result

    def compute_distance(self):
        raw_distance = self.sample_average(self._tof_samples)
        distance = self._tof_filter.update(raw_distance)

        # Once we are running, save the first sample as the starting distance.
        if self._state == TrackingGrowthScreen.STATE_RUNNING:
            if self._starting_distance is None:
                self._starting_distance = distance

        # Update the label.
        self._current_distance = distance
        # self._distance_lbl.value(f"{int(self._current_distance)} mm")

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
            self._gas,
            self._starting_distance,
            self._current_distance,
        )
        logger.info(
            f"Submitting data: feeding: {self._feeding_id} T: {self._temperature} RH: {self._rh}% "
        )
        logger.info(f"CO2: {self._co2}ppm {self._gas}ohm")
        logger.info(
            f"starting distance:{self._starting_distance} cur distance: {self._current_distance}"
        )

        memory.print_mem()
        self._db_service.create_feeding_progress(model)
