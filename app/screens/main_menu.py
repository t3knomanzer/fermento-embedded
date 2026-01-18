from app.screens.feeding import FeedingScreen
from app.screens.jar_name import JarNameScreen
from app.screens.tracking_select import TrackingSelectScreen
from lib.gui.core.ugui import Screen, ssd

from lib.gui.core.writer import Writer
import lib.gui.fonts.arial10 as arial10
from lib.gui.widgets.buttons import Button


class MainMenuScreen(Screen):
    NAV_JAR_NAME = "1"
    NAV_TRACKING_SELECT = "2"

    def __init__(self):
        writer = Writer(ssd, arial10)
        super().__init__()
        btn_width = int(ssd.width / 1.5)
        btn_height = writer.height + 4
        row = ssd.height // 2 - btn_height // 2 - 2
        col = ssd.width // 2 - btn_width // 2
        btn_01 = Button(
            writer,
            row=row,
            col=col,
            width=btn_width,
            height=btn_height,
            text="New Jar",
            callback=self.nav,
            args=(MainMenuScreen.NAV_JAR_NAME,),
        )

        row = ssd.height // 2 + btn_height // 2 + 2
        btn_02 = Button(
            writer,
            row=row,
            col=col,
            width=btn_width,
            height=btn_height,
            text="Start Tracking",
            callback=self.nav,
            args=(MainMenuScreen.NAV_TRACKING_SELECT,),
        )

    def nav(self, button, arg):
        if arg == MainMenuScreen.NAV_JAR_NAME:
            Screen.change(JarNameScreen)
        elif arg == MainMenuScreen.NAV_TRACKING_SELECT:
            Screen.change(TrackingSelectScreen)
