import asyncio
import gc

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


class MeasureScreen(Screen):
    def __init__(self, jar_name):
        super().__init__()
        self._jar_name = jar_name
        self._distance = 0
        self._db_service = DBService()
        self._dist_sensor = dist_sensor
        self._temp_sensor = temp_sensor

        large_writer = Writer(ssd, large_font)
        small_writer = Writer(ssd, small_font)

        lbl_width = ssd.width
        name_lbl = Label(
            small_writer, row=4, col=0, text=lbl_width, justify=Label.CENTRE
        )
        name_lbl.value(self._jar_name)

        lbl_row = ssd.height // 2 - int(large_writer.height / 1.5)
        self._distance_lbl = Label(
            large_writer, row=lbl_row, col=0, text=lbl_width, justify=Label.CENTRE
        )
        self._distance_lbl.value("")

        btn_width = 48
        btn_margin = 4
        screen_center_h = ssd.width // 2
        btn_save = Button(
            small_writer,
            0,
            0,
            width=btn_width,
            text="save",
            callback=self.save,
            args=("."),
        )
        btn_cancel = Button(
            small_writer,
            0,
            0,
            width=btn_width,
            text="cancel",
            callback=self.back,
            args=("."),
        )
        btn_save.row = ssd.height - btn_save.height - btn_margin // 2
        btn_cancel.row = btn_save.row
        btn_save.col = screen_center_h - btn_width - btn_margin // 2
        btn_cancel.col = screen_center_h + btn_margin // 2

    @timeit
    def save(self, button, arg):
        gc.collect()
        print_mem()
        model = JarModel(self._jar_name, self._distance)
        self._db_service.create_jar(model)
        Screen.back()

    def back(self, button, arg):
        Screen.back()

    def after_open(self):
        asyncio.create_task(self.compute_distance())
        asyncio.create_task(self.compute_temp())

    async def compute_temp(self):
        while type(Screen.current_screen) == MeasureScreen:
            self._temp_sensor.measure()
            temp = self._temp_sensor.temperature()
            humidity = self._temp_sensor.humidity()
            print(f"Temp: {temp} Humidity: {humidity}")
            await asyncio.sleep(3)

    async def compute_distance(self):
        while type(Screen.current_screen) == MeasureScreen:
            distance = self._dist_sensor.distance_cm()
            self._distance = int(distance * 10)
            self._distance_lbl.value(f"{self._distance} mm")
            await asyncio.sleep(0.1)
