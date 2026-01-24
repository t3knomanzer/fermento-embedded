import os
import machine
from app.services.log import LogServiceManager
from lib.gui.core.ugui import Screen, ssd

from lib.gui.core.writer import Writer
import lib.gui.fonts.arial10 as arial10
from lib.gui.widgets.buttons import Button

# Create logger
logger = LogServiceManager.get_logger(name=__name__)


class SettingsScreen(Screen):
    def __init__(self):
        writer = Writer(ssd, arial10)
        super().__init__()

        btn_width = int(ssd.width / 1.5)
        btn_height = writer.height + 4
        row = ssd.height // 2 - btn_height - 2
        col = ssd.width // 2 - btn_width // 2
        Button(
            writer,
            row=row,
            col=col,
            width=btn_width,
            height=btn_height,
            text="Reset Settings",
            callback=self.reset_settings,
        )

        row = ssd.height // 2 + 2
        Button(
            writer,
            row=row,
            col=col,
            width=btn_width,
            height=btn_height,
            text="Back",
            callback=self.back_callback,
        )

    def back_callback(self, btn):
        Screen.back()

    def reset_settings(self, btn):
        logger.info("Reset settings...")
        try:
            os.remove("/wifi.dat")
            machine.reset()
        except OSError as e:
            logger.error("Delete failed:", e)
