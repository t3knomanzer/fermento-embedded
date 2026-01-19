import asyncio
import gc

from app.models.feeding_progress import FeedingProgressModel
from hardware_setup import distance_sensor, ambient_sensor
import lib.gui.fonts.freesans20 as large_font
import lib.gui.fonts.arial10 as small_font
from lib.gui.core.colors import BLACK, WHITE
from lib.gui.core.ugui import Screen, ssd
from lib.gui.widgets.buttons import Button
from lib.gui.widgets.label import Label
from lib.gui.core.writer import Writer

from app.utils.utils import print_mem
from app.widgets.widgets.message_box import MessageBox
from app.models.jar import JarModel
from app.utils.decorators import timeit
from app.services.db import DBService


class TrackingGrowthScreen(Screen):
    def __init__(self, feeding_id, starter_name, jar_name, jar_distance):
        self._feeding_id = feeding_id
        self._starter_name = starter_name
        self._jar_name = jar_name
        self._jar_distance = jar_distance
        self._starting_distance = None
        self._current_distance = 0
        self._temperature = 0
        self._humidity = 0
        self._btn_state = True
        self._elapsed_seconds = 0
        self._elapsed_minutes = 0
        self._elapsed_hours = 0

        self._db_service = DBService()
        self._distance_sensor = distance_sensor
        self._temperature_sensor = ambient_sensor

        self._large_writer = Writer(ssd, large_font)
        self._small_writer = Writer(ssd, small_font)
        super().__init__()

        width = ssd.width // 3
        self._temperature_lbl = Label(
            self._small_writer, row=2, col=2, text=width, justify=Label.LEFT
        )
        self._temperature_lbl.value("0C")

        col = ssd.width // 3
        self._distance_lbl = Label(
            self._small_writer, row=2, col=col, text=width, justify=Label.CENTRE
        )
        self._distance_lbl.value("0C")

        col = ssd.width // 3 * 2
        self._humidity_lbl = Label(
            self._small_writer, row=2, col=col, text=width, justify=Label.RIGHT
        )
        self._humidity_lbl.value("0%")

        width = ssd.width // 2
        row = ssd.height // 2 - self._large_writer.height // 2
        self._growth_lbl = Label(
            self._large_writer, row=row, col=0, text=width, justify=Label.LEFT
        )
        self._growth_lbl.value("0%")

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
            callback=self.start_stop,
        )

        width = ssd.width // 3
        row = ssd.height - self._small_writer.height - 2
        self._starter_lbl = Label(
            self._small_writer, row=row, col=2, text=width, justify=Label.LEFT
        )
        self._starter_lbl.value(self._starter_name)

        col = ssd.width // 3
        self._time_lbl = Label(
            self._small_writer, row=row, col=col, text=width, justify=Label.CENTRE
        )
        self._time_lbl.value("00:00:00")

        col = ssd.width // 3 * 2
        self._jar_lbl = Label(
            self._small_writer, row=row, col=col, text=width, justify=Label.RIGHT
        )
        self._jar_lbl.value(self._jar_name)

    def start_stop(self, btn):
        asyncio.create_task(self.start_stop_async())

    async def start_stop_async(self):
        if self._btn_state:
            self._btn.text = "Starting..."
            self._btn.show()
            await asyncio.sleep(0.01)
            asyncio.create_task(self.compute_growth())
            asyncio.create_task(self.update_time())
            asyncio.create_task(self.submit_data())
        else:
            Screen.back()

        self._btn_state = not self._btn_state

    def after_open(self):
        asyncio.create_task(self.compute_distance())
        asyncio.create_task(self.compute_ambient())

    async def compute_ambient(self):
        while type(Screen.current_screen) == TrackingGrowthScreen:
            self._temperature_sensor.measure()
            self._temperature = self._temperature_sensor.temperature()
            self._humidity = self._temperature_sensor.humidity()
            print(f"Temp: {self._temperature} Humidity: {self._humidity}")

            self._temperature_lbl.value(f"{self._temperature}C")
            self._humidity_lbl.value(f"{self._humidity}%")
            await asyncio.sleep(3)

    async def compute_distance(self):
        while type(Screen.current_screen) == TrackingGrowthScreen:
            distance = self._distance_sensor.distance_cm()
            self._current_distance = int(distance * 10)
            self._distance_lbl.value(f"{self._current_distance} mm")
            await asyncio.sleep(0.1)

    async def compute_growth(self):
        while type(Screen.current_screen) == TrackingGrowthScreen:
            if self._starting_distance is None:
                self._starting_distance = int(self._distance_sensor.distance_cm()) * 10

            initial_size = self._jar_distance - self._starting_distance
            growth_size = self._starting_distance - self._current_distance
            growth_percent = max(0, growth_size / initial_size) * 100.0
            self._growth_lbl.value(f"{growth_percent:.1f}%")
            await asyncio.sleep(0.1)

    async def update_time(self):
        while type(Screen.current_screen) == TrackingGrowthScreen:
            await asyncio.sleep(1)
            self._elapsed_seconds += 1
            if self._elapsed_seconds == 60:
                self._elapsed_seconds = 0
                self._elapsed_minutes += 1
            if self._elapsed_minutes == 60:
                self._elapsed_minutes = 0
                self._elapsed_hours += 1
            self._time_lbl.value(
                f"{self._elapsed_hours:02d}:{self._elapsed_minutes:02d}:{self._elapsed_seconds:02d}"
            )

    @timeit
    async def submit_data(self):
        while type(Screen.current_screen) == TrackingGrowthScreen:
            gc.collect()
            print_mem()
            model = FeedingProgressModel(
                self._feeding_id,
                self._temperature,
                self._humidity / 100,
                self._starting_distance,
                self._current_distance,
            )
            self._db_service.create_feeding_progress(model)

            if self._btn.text != "Stop":
                self._btn.text = "Stop"
                self._btn.show()

            await asyncio.sleep(60)
