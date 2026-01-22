import asyncio
import gc

from app.services.log import LogServiceManager
from app.utils import memory
import config
from hardware_setup import tof_sensor
import lib.gui.fonts.freesans20 as large_font
import lib.gui.fonts.arial10 as small_font
from lib.gui.core.ugui import Screen, ssd
from lib.gui.widgets.buttons import Button
from lib.gui.widgets.label import Label
from lib.gui.core.writer import Writer

from app.widgets.widgets.message_box import MessageBox
from app.models.jar import JarModel
from app.utils.decorators import time_it, track_mem
from app.services.db import DBService
from app.utils.filtering import TofDistanceFilter

memory.print_mem()

# Create logger
logger = LogServiceManager.get_logger(name=__name__)


class MeasureScreen(Screen):
    def __init__(self, jar_name):
        super().__init__()
        self._jar_name = jar_name
        self._distance = 0
        self._db_service = DBService()
        self._distance_sensor = tof_sensor
        self._distance_filter = TofDistanceFilter(max_jump_mm=30, alpha_shift=3)

        self._large_writer = Writer(ssd, large_font)
        self._small_writer = Writer(ssd, small_font)

        # UI Widgets
        # Jar name
        lbl_width = ssd.width
        name_lbl = Label(
            self._small_writer, row=4, col=0, text=lbl_width, justify=Label.CENTRE
        )
        name_lbl.value(self._jar_name)

        # Distance
        lbl_row = ssd.height // 2 - int(self._large_writer.height / 1.5)
        self._distance_lbl = Label(
            self._large_writer, row=lbl_row, col=0, text=lbl_width, justify=Label.CENTRE
        )
        self._distance_lbl.value("")

        # Save button
        btn_width = 48
        btn_margin = 4
        screen_center_h = ssd.width // 2
        btn_save = Button(
            self._small_writer,
            0,
            0,
            width=btn_width,
            text="save",
            callback=self.save_callback,
            args=("."),
        )

        # Cancel button
        btn_cancel = Button(
            self._small_writer,
            0,
            0,
            width=btn_width,
            text="cancel",
            callback=self.back_callback,
            args=("."),
        )
        btn_save.row = ssd.height - btn_save.height - btn_margin // 2
        btn_cancel.row = btn_save.row
        btn_save.col = screen_center_h - btn_width - btn_margin // 2
        btn_cancel.col = screen_center_h + btn_margin // 2

    def save_callback(self, btn, arg):
        asyncio.create_task(self.save_async())

    @time_it
    @track_mem
    async def save_async(self):
        gc.collect()
        # Popup, since saving can take a while.
        Screen.change(
            MessageBox, kwargs={"writer": self._small_writer, "message": "Saving..."}
        )
        await asyncio.sleep(0.01)

        model = JarModel(self._jar_name, self._distance)
        self._db_service.create_jar(model)

        # Back from the popup and back to the main menu.
        Screen.back()
        Screen.back()

    def back_callback(self, button, arg):
        Screen.back()

    def after_open(self):
        asyncio.create_task(self.compute_distance())

    async def compute_distance(self):
        while type(Screen.current_screen) == MeasureScreen:
            distance = 0
            samples = config.TOF_SAMPLES_MEASURE
            for i in range(samples):
                distance += self._distance_sensor.range
            raw_avg_distance = distance // samples

            self._distance = raw_avg_distance
            self._distance_lbl.value(f"{self._distance} mm")
            await asyncio.sleep(config.MEASURE_DELAY)
