import asyncio
import gc

from app.models.feeding_progress import FeedingProgressModel
from app.services.log import LogServiceManager
from app.utils import memory
from app.utils.filtering import TofDistanceFilter
import config
from hardware_setup import tof_sensor, ambient_sensor
import lib.gui.fonts.freesans20 as large_font
import lib.gui.fonts.arial10 as small_font
from lib.gui.core.colors import BLACK, WHITE
from lib.gui.core.ugui import Screen, ssd
from lib.gui.widgets.buttons import Button
from lib.gui.widgets.label import Label
from lib.gui.core.writer import Writer
from app.utils.decorators import time_it, track_mem
from app.services.db import DBService

memory.print_mem()

# Create logger
logger = LogServiceManager.get_logger(name=__name__)


class TrackingGrowthScreen(Screen):
    STATE_STOPPED = 0
    STATE_RUNNING = 1

    def __init__(self, feeding_id, starter_name, jar_name, jar_distance):
        self._feeding_id = feeding_id
        self._starter_name = starter_name
        self._jar_name = jar_name
        self._jar_distance = jar_distance
        self._starting_distance = None
        self._current_distance = 0
        self._temperature = 0
        self._humidity = 0
        self._state = True
        self._elapsed_seconds = 0
        self._elapsed_minutes = 0
        self._elapsed_hours = 0

        self._db_service = DBService()
        self._distance_sensor = tof_sensor
        self._temperature_sensor = ambient_sensor

        self._large_writer = Writer(ssd, large_font)
        self._small_writer = Writer(ssd, small_font)
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
        self._humidity_lbl = Label(
            self._small_writer, row=2, col=col, text=width, justify=Label.RIGHT
        )
        self._humidity_lbl.value("0%")

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
        row = 2
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

    def start_stop_callback(self, btn):
        asyncio.create_task(self.start_stop_async())

    async def start_stop_async(self):
        if self._state == TrackingGrowthScreen.STATE_STOPPED:
            self._state = TrackingGrowthScreen.STATE_RUNNING
            # Changing the text property doesn't force an update
            self._btn.text = "Starting..."
            self._btn.show()
            await asyncio.sleep(0.01)

            # At this point we start
            asyncio.create_task(self.compute_growth())
            asyncio.create_task(self.update_time())
            asyncio.create_task(self.submit_data())

            self._btn.text = "Stop"
            self._btn.show()
            await asyncio.sleep(0.01)

        elif self._state == TrackingGrowthScreen.STATE_RUNNING:
            self._state = TrackingGrowthScreen.STATE_STOPPED
            Screen.back_callback()

    def after_open(self):
        # We start tracking the distance, temperature and humidity right away
        # so that the user has some feedback.
        asyncio.create_task(self.compute_distance())
        asyncio.create_task(self.compute_temperature())

    @track_mem
    async def compute_temperature(self):
        while type(Screen.current_screen) == TrackingGrowthScreen:
            gc.collect()
            self._temperature_sensor.measure()
            self._temperature = self._temperature_sensor.temperature()
            self._humidity = self._temperature_sensor.humidity()
            print(f"Temp: {self._temperature} Humidity: {self._humidity}")

            self._temperature_lbl.value(f"{self._temperature}C")
            self._humidity_lbl.value(f"{self._humidity}%")

            logger.info(f"Temperature: {self._temperature} Humidity: {self._humidity}")
            await asyncio.sleep(config.TEMPERATURE_DELAY)

    @time_it
    @track_mem
    async def compute_distance(self):
        while type(Screen.current_screen) == TrackingGrowthScreen:
            distance = 0
            samples = 0
            # Change the number of samples depending on the current state
            # since sampling takes time.
            if self._state == TrackingGrowthScreen.STATE_STOPPED:
                samples = config.TOF_SAMPLES_STOPPED
                delay = config.DISTANCE_DELAY_STOPPED
            elif self._state == TrackingGrowthScreen.STATE_RUNNING:
                samples = config.TOF_SAMPLES_RUNNING
                delay = config.DISTANCE_DELAY_RUNNING

            # Take the samples and compute the average.
            gc.collect()
            for i in range(samples):
                distance += self._distance_sensor.range
            raw_avg_distance = distance // samples

            # If this the user pressed start, save the first sample as the
            # the starting distance.
            if (
                self._starting_distance is None
                and self._state == TrackingGrowthScreen.STATE_RUNNING
            ):
                self._starting_distance = raw_avg_distance

            # Update the label.
            self._current_distance = raw_avg_distance
            self._distance_lbl.value(f"{self._current_distance} mm")
            await asyncio.sleep(delay)

    async def compute_growth(self):
        while type(Screen.current_screen) == TrackingGrowthScreen:
            initial_size = self._jar_distance - self._starting_distance
            growth_size = self._starting_distance - self._current_distance
            growth_percent = max(0, growth_size / initial_size) * 100.0

            self._growth_lbl.value(f"{int(growth_percent)}%")

            await asyncio.sleep(config.GROWTH_DELAY)

    async def update_time(self):
        while type(Screen.current_screen) == TrackingGrowthScreen:
            await asyncio.sleep(1)

            elapsed_seconds += 1
            h, rem = divmod(elapsed_seconds, 3600)
            m, s = divmod(rem, 60)

            self._time_lbl.value(f"{h:02d}:{m:02d}:{s:02d}")

    @time_it
    @track_mem
    async def submit_data(self):
        while type(Screen.current_screen) == TrackingGrowthScreen:
            gc.collect()
            model = FeedingProgressModel(
                self._feeding_id,
                self._temperature,
                self._humidity / 100,
                self._starting_distance,
                self._current_distance,
            )
            self._db_service.create_feeding_progress(model)
            await asyncio.sleep(config.SUBMIT_DATA_DELAY)
