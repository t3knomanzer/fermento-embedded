import asyncio
import gc
from sys import exit

from app.screens.main_menu import MainMenuScreen
from app.services.network import NetworkService
from app.utils.utils import print_mem
from lib.gui.core.colors import BLACK, WHITE
from lib.gui.core.ugui import Screen, ssd
from lib.gui.widgets.bitmap import BitMap
from lib.gui.widgets.label import Label
from lib.gui.core.writer import Writer
import lib.gui.fonts.arial10 as arial10

import config


class SplashScreen(Screen):
    def __init__(self):
        writer = Writer(ssd, arial10)

        # We pass the writer to the constructor since there aren't any active objects this screen.
        # https://github.com/peterhinch/micropython-micro-gui/blob/main/README.md#42-constructor
        super().__init__(writer)
        self._next_screen = MainMenuScreen
        self._delay = config.SPLASH_DELAY

        screen_center_v = ssd.height // 2 - writer.height // 2
        bmp_size = (100, 60)
        col = ssd.width // 2 - bmp_size[0] // 2
        row = ssd.height // -+bmp_size[1] // 2
        print_mem()
        self.graphic = BitMap(
            writer,
            row,
            col,
            bmp_size[1],
            bmp_size[0],
            fgcolor=BLACK,
            bgcolor=WHITE,
            bdcolor=None,
        )
        self.graphic.value(path := "fermento_logo.xbm")

        self._lbl_msg = Label(
            writer,
            screen_center_v + self.graphic.height + 4,
            64,
            128,
            justify=Label.CENTRE,
        )

    def after_open(self):
        asyncio.create_task(self.initialize())

    async def initialize(self):
        # Wifi
        gc.collect()
        await self.display_message_async("Connecting")
        self.connect_wifi()
        print_mem()

        await self.display_message_async("Welcome")
        await asyncio.sleep(self._delay)

        # Navigate to next screen
        if self._next_screen:
            Screen.change(self._next_screen)

    async def display_message_async(self, msg):
        self._lbl_msg.value(msg)
        await asyncio.sleep(0.1)

    def connect_wifi(self):
        try:
            net_service = NetworkService()
            net_service.connect()
        except OSError as e:
            self.display_message_async("Connection error")
            print(f"Connection error: {e}")
            exit()
