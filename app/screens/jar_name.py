import random

from app.screens.jar_measure import MeasureScreen
from app.services.log import LogServiceManager
from app.utils import memory
import config
from lib.gui.core.ugui import Screen, ssd
from lib.gui.widgets.buttons import Button
from lib.gui.core.writer import Writer
import lib.gui.fonts.arial10 as small_font

from app.resources.names import NAMES
from lib.gui.widgets.label import Label

# Create logger
logger = LogServiceManager.get_logger(name=__name__)


class JarNameScreen(Screen):
    def __init__(self):
        super().__init__()
        writer = Writer(ssd, small_font, verbose=False)

        # UI Widgets
        # Title
        margin = 6
        row = ssd.height // 2 - writer.height - margin
        col = 0
        lbl = Label(
            writer,
            row=row,
            col=0,
            text=ssd.width,
            justify=Label.CENTRE,
        )
        lbl.value("Select a name")

        # Generate choices
        num_choices = config.JAR_NAME_CHOICES
        btn_width = ssd.width // num_choices - margin
        btn_names = self.generate_name_choices(num_choices)

        # Choice buttons
        for i, name in enumerate(btn_names):
            col = (btn_width * i) + (margin * (i + 1))
            Button(
                writer,
                row=ssd.height // 2,
                col=col,
                width=btn_width,
                text=name,
                callback=self.select_name,
                args=(name,),
            )

    def generate_name_choices(self, num_choices=3):
        logger.info("Generating name choices...")
        btn_names = set()
        while len(btn_names) < num_choices:
            index = random.randint(0, len(NAMES) - 1)
            name = NAMES[index]
            btn_names.add(name)

        return btn_names

    def select_name(self, button, arg):
        logger.info(f"Name selected: {arg}")
        Screen.change(MeasureScreen, mode=Screen.REPLACE, args=[arg])
