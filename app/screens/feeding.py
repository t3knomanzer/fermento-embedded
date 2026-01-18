from lib.gui.core.ugui import Screen, ssd
from lib.gui.widgets.buttons import CloseButton
from lib.gui.widgets.label import Label
from lib.gui.core.writer import Writer
import lib.gui.fonts.arial10 as arial10


class FeedingScreen(Screen):
    def __init__(self, next_screen=None, delay=3):
        writer = Writer(ssd, arial10)

        # We pass the writer to the constructor since there aren't any active objects this screen.
        # https://github.com/peterhinch/micropython-micro-gui/blob/main/README.md#42-constructor
        super().__init__(writer)
        self._next_screen = next_screen
        self._delay = delay

        screen_center_v = ssd.height // 2 - writer.height // 2
        lbl = Label(writer, screen_center_v, 64, 128, justify=Label.CENTRE)
        lbl.value("New Feeding")
        CloseButton(writer)
