import asyncio
import gc
import sys

from app.screens.main_menu import MainMenuScreen
from app.services.log import LogServiceManager
from app.services.network import NetworkService
from app.utils import memory
from app.utils.time import init_time
from lib.gui.core.colors import BLACK, WHITE
from lib.gui.core.ugui import Screen, ssd
from lib.gui.widgets.bitmap import BitMap
from lib.gui.widgets.label import Label
from lib.gui.core.writer import Writer
import lib.gui.fonts.arial10 as arial10
import config

# Create logger
logger = LogServiceManager.get_logger(name=__name__)


class SplashScreen(Screen):
    def __init__(self):
        writer = Writer(ssd, arial10, verbose=False)
        super().__init__(writer)

        self._next_screen = MainMenuScreen
        self._delay = config.SPLASH_DELAY
        self._net_service = NetworkService()

        # UI widgets
        # Logo
        screen_center_v = ssd.height // 2 - writer.height // 2
        bmp_size = (100, 60)
        col = ssd.width // 2 - bmp_size[0] // 2
        row = ssd.height // +bmp_size[1] // 2
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

        # Progress messages
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
        logger.info("Initializing WiFi...")

        # Connect ti wifi or start the web server for the
        # user to connect to and enter credentials.
        gc.collect()
        memory.print_mem()

        connected = None
        await self.display_message_async("Connecting")
        try:
            connected = self._net_service.connect()
        except Exception as e:
            logger.critical(f"Error connecting to WiFi. {e}")
            sys.exit()

        if connected:
            logger.info("Setting up...")
            await self.display_message_async("Setting up")
            await asyncio.sleep(1)  # Give WiFi some time to initialize
            init_time()
            await self.display_message_async("Welcome")
            await asyncio.sleep(self._delay)
            Screen.change(self._next_screen)
        else:
            await self.display_message_async("Configure WiFi")
            logger.info("Starting web server...")
            try:
                self._net_service.start_server()
            except Exception as e:
                logger.critical(f"Error starting web server. {e}")
                sys.exit()

    async def display_message_async(self, msg):
        self._lbl_msg.value(msg)
        # Give the UI a chance to refresh.
        await asyncio.sleep(0.1)
