import asyncio
from app.screens.jar_name import JarNameScreen
from app.screens.settings import SettingsScreen
from app.screens.tracking_select import TrackingSelectScreen
from app.services.db import DBService
from app.services.log import LogServiceManager
from app.utils import memory
from app.utils.decorators import time_it, track_mem
from app.widgets.widgets.message_box import MessageBox
import config
from lib.gui.core.ugui import Screen, ssd

from lib.gui.core.writer import Writer
import lib.gui.fonts.arial10 as arial10
from lib.gui.widgets.buttons import Button

memory.print_mem()

# Create logger
logger = LogServiceManager.get_logger(name=__name__)


class MainMenuScreen(Screen):
    NAV_JAR_NAME = "1"
    NAV_TRACKING_SELECT = "2"
    NAV_SETTINGS = "3"

    def __init__(self):
        super().__init__()
        self._db_service = DBService()
        self._writer = Writer(ssd, arial10, verbose=False)

        # UI widgets
        btn_width = int(ssd.width / 1.5)
        btn_height = self._writer.height + 4

        # Measure button
        row = (ssd.height // 2) - btn_height // 2 - btn_height - 4
        col = ssd.width // 2 - btn_width // 2
        btn_01 = Button(
            self._writer,
            row=row,
            col=col,
            width=btn_width,
            height=btn_height,
            text="Measure",
            callback=self.navigate,
            args=(MainMenuScreen.NAV_JAR_NAME,),
        )

        # Track button
        row = ssd.height // 2 - btn_height // 2
        btn_02 = Button(
            self._writer,
            row=row,
            col=col,
            width=btn_width,
            height=btn_height,
            text="Track",
            callback=self.navigate,
            args=(MainMenuScreen.NAV_TRACKING_SELECT,),
        )

        # Settings button
        row = (ssd.height // 2) + btn_height // 2 + 4
        btn_03 = Button(
            self._writer,
            row=row,
            col=col,
            width=btn_width,
            height=btn_height,
            text="Settings",
            callback=self.navigate,
            args=(MainMenuScreen.NAV_SETTINGS,),
        )

    async def navigate_tracking(self):
        # Popup
        Screen.change(
            MessageBox,
            kwargs={"writer": self._writer, "message": "Retrieving data..."},
        )
        await asyncio.sleep(0.01)
        # Retrieve feedings, this takes some time.
        feedings = self._db_service.get_feedings(config.MAX_FEEDINGS)

        # Close the popup
        Screen.back_callback()
        Screen.change(TrackingSelectScreen, args=(feedings,))

    def navigate(self, button, arg):
        if arg == MainMenuScreen.NAV_JAR_NAME:
            Screen.change(JarNameScreen)
        elif arg == MainMenuScreen.NAV_TRACKING_SELECT:
            # Tracking needs to load the feedings from the DB.
            # We run it async since we need to update the UI
            asyncio.create_task(self.navigate_tracking())
        elif arg == MainMenuScreen.NAV_SETTINGS:
            Screen.change(SettingsScreen)
