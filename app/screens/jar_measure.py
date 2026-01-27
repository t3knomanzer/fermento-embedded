import asyncio
import gc

from app.utils.memory import print_mem
import config
from hardware_setup import tof_sensor
from app.services.log import LogServiceManager
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

# Create logger
logger = LogServiceManager.get_logger(name=__name__)


class MeasureScreen(Screen):
    def __init__(self, jar_name):
        super().__init__()
        self._jar_name = jar_name
        self._distance = 0
        self._db_service = DBService()
        self._tof_sensor = tof_sensor

        self._large_writer = Writer(ssd, large_font, verbose=False)
        self._small_writer = Writer(ssd, small_font, verbose=False)

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

    def after_open(self):
        asyncio.create_task(self.compute_distance())

    def save_callback(self, btn, arg):
        asyncio.create_task(self.save_async())

    def back_callback(self, button, arg):
        Screen.back()

    def average_sample(self, samples):
        distance = 0
        for i in range(samples):
            while not self._tof_sensor.data_ready:
                pass
            distance += self._tof_sensor.distance
        self._tof_sensor.clear_interrupt()
        result = (distance // samples) * 10
        return result

    async def compute_distance(self):
        logger.info("Previewing distance...")
        print_mem()
        self._tof_sensor.stop_ranging()
        self._tof_sensor.timing_budget = config.TOF_TIMING_PREVIEW
        self._tof_sensor.start_ranging()

        while type(Screen.current_screen) == MeasureScreen:
            self._distance = self.average_sample(config.TOF_SAMPLES_PREVIEW)
            self._distance_lbl.value(f"{self._distance} mm")
            logger.debug(f"Averaged distance: {self._distance} mm")
            await asyncio.sleep(config.PREVIEW_UPDATE_DELAY)

    async def save_async(self):
        logger.info("Saving distance...")
        print_mem()
        # Popup, since saving can take a while.
        await self.show_popup("Saving...")

        # We take 1 high quality sample for saving.
        self._tof_sensor.stop_ranging()
        self._tof_sensor.timing_budget = config.TOF_TIMING_RUNNING
        self._distance = self.average_sample(config.TOF_SAMPLES_RUNNING)
        self._tof_sensor.start_ranging()

        try:
            model = JarModel(self._jar_name, self._distance)
            self._db_service.create_jar(model)

            Screen.back()  # Close the popup
            Screen.back()  # Back to the main menu
        except Exception as e:
            logger.error(f"Error saving. {e}")
            Screen.back()  # Close the popup
            await self.show_popup("Error saving.", 1)

    async def show_popup(self, message, duration=None):
        # Popup
        Screen.change(
            MessageBox,
            kwargs={"writer": self._small_writer, "message": message},
        )
        if duration:
            await asyncio.sleep(duration)
            Screen.back()
        else:
            await asyncio.sleep(0.01)
