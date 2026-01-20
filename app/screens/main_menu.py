import asyncio
from app.screens.feeding import FeedingScreen
from app.screens.jar_name import JarNameScreen
from app.screens.settings import SettingsScreen
from app.screens.tracking_select import TrackingSelectScreen
from app.services.db import DBService
from app.utils.decorators import time_it
from app.widgets.widgets.message_box import MessageBox
from lib.gui.core.ugui import Screen, ssd

from lib.gui.core.writer import Writer
import lib.gui.fonts.arial10 as arial10
from lib.gui.widgets.buttons import Button


class MainMenuScreen(Screen):
    NAV_JAR_NAME = "1"
    NAV_TRACKING_SELECT = "2"
    NAV_SETTINGS = "3"

    def __init__(self):
        super().__init__()
        self._db_service = DBService()
        self._writer = Writer(ssd, arial10)
        btn_width = int(ssd.width / 1.5)
        btn_height = self._writer.height + 4
        row = (ssd.height // 2) - btn_height // 2 - btn_height - 4
        col = ssd.width // 2 - btn_width // 2
        btn_01 = Button(
            self._writer,
            row=row,
            col=col,
            width=btn_width,
            height=btn_height,
            text="New Jar",
            callback=self.nav,
            args=(MainMenuScreen.NAV_JAR_NAME,),
        )

        row = ssd.height // 2 - btn_height // 2
        btn_02 = Button(
            self._writer,
            row=row,
            col=col,
            width=btn_width,
            height=btn_height,
            text="Start Tracking",
            callback=self.nav,
            args=(MainMenuScreen.NAV_TRACKING_SELECT,),
        )

        row = (ssd.height // 2) + btn_height // 2 + 4
        btn_03 = Button(
            self._writer,
            row=row,
            col=col,
            width=btn_width,
            height=btn_height,
            text="Settings",
            callback=self.nav,
            args=(MainMenuScreen.NAV_SETTINGS,),
        )

    async def go_to_tracking_select(self):
        Screen.change(
            MessageBox,
            kwargs={"writer": self._writer, "message": "Retrieving data..."},
        )
        await asyncio.sleep(0.01)
        feedings = self._db_service.get_feedings(2)
        Screen.back()
        Screen.change(TrackingSelectScreen, args=(feedings,))

    def nav(self, button, arg):
        if arg == MainMenuScreen.NAV_JAR_NAME:
            Screen.change(JarNameScreen)
        elif arg == MainMenuScreen.NAV_TRACKING_SELECT:
            asyncio.create_task(self.go_to_tracking_select())
        elif arg == MainMenuScreen.NAV_SETTINGS:
            Screen.change(SettingsScreen)
