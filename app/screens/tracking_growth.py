import asyncio
import gc

from app.models.feeding_progress import FeedingProgressModel
from hardware_setup import dist_sensor, temp_sensor
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

        self._db_service = DBService()
        self._distance_sensor = dist_sensor
        self._temperature_sensor = temp_sensor

        large_writer = Writer(ssd, large_font)
        small_writer = Writer(ssd, small_font)
        super().__init__()

        width = ssd.width // 2
        self._temperature_lbl = Label(
            small_writer, row=2, col=2, text=width, justify=Label.LEFT
        )
        self._temperature_lbl.value("0C")

        col = ssd.width // 2
        self._humidity_lbl = Label(
            small_writer, row=2, col=col, text=width, justify=Label.RIGHT
        )
        self._humidity_lbl.value("0%")

        width = ssd.width // 2
        col = width // 2
        self._distance_lbl = Label(
            small_writer, row=2, col=col, text=width, justify=Label.CENTRE
        )
        self._distance_lbl.value("0C")

        width = ssd.width
        row = ssd.height // 2 - large_writer.height // 2
        self._growth_lbl = Label(
            large_writer, row=row, col=0, text=width, justify=Label.CENTRE
        )
        self._growth_lbl.value("0%")

        width = ssd.width // 2
        row = ssd.height - small_writer.height - 2
        self._starter_lbl = Label(
            small_writer, row=row, col=2, text=width, justify=Label.LEFT
        )
        self._starter_lbl.value(self._starter_name)

        col = ssd.width // 2
        self._jar_lbl = Label(
            small_writer, row=row, col=col, text=width, justify=Label.RIGHT
        )
        self._jar_lbl.value(self._jar_name)

        width = 32
        height = small_writer.height + 8
        col = ssd.width // 2 - width // 2
        self._stop_btn = Button(
            small_writer,
            row=row,
            col=col,
            text="Stop",
            width=width,
            height=height,
            callback=self.stop,
        )

    def stop(self, btn):
        Screen.back()

    def after_open(self):
        asyncio.create_task(self.compute_distance())
        asyncio.create_task(self.compute_ambient())
        asyncio.create_task(self.compute_progress())
        asyncio.create_task(self.save())

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
            if self._starting_distance is None:
                self._starting_distance = self._current_distance

            self._distance_lbl.value(f"{self._current_distance} mm")
            await asyncio.sleep(0.1)

    async def compute_progress(self):
        while type(Screen.current_screen) == TrackingGrowthScreen:
            initial_size = self._jar_distance - self._starting_distance
            growth_distance = self._starting_distance - self._current_distance
            growth_percent = max(0, growth_distance / initial_size) * 100.0
            self._growth_lbl.value(f"{growth_percent:.2f}%")
            await asyncio.sleep(0.1)

    @timeit
    async def save(self):
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
            await asyncio.sleep(60 * 15)
