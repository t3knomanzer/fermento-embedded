import asyncio
import random

from app.screens.jar_measure import MeasureScreen
from app.screens.tracking_growth import TrackingGrowthScreen
from app.utils.decorators import time_it
from app.widgets.widgets.message_box import MessageBox
from lib.gui.core.ugui import Screen, ssd
from lib.gui.widgets.buttons import Button
from lib.gui.core.writer import Writer
import lib.gui.fonts.arial10 as small_font

from app.resources.names import NAMES
from lib.gui.widgets.label import Label
from lib.gui.widgets.listbox import Listbox


class TrackingSelectScreen(Screen):
    def __init__(self, feedings):
        super().__init__()
        self._writer = Writer(ssd, small_font)

        row = 6
        col = 0
        lbl = Label(
            self._writer,
            row=row,
            col=col,
            text=ssd.width,
            justify=Label.CENTRE,
        )
        lbl.value("Select a feeding")

        width = ssd.width - 24
        height = self._writer.height + 8
        row = row + self._writer.height + 6
        col = 12

        for i, item in enumerate(feedings):
            Button(
                self._writer,
                row=row,
                col=col,
                width=width,
                height=height,
                text=item.date,
                callback=self.select_feeding,
                args=(item,),
            )
            row += height + 2

    def select_feeding(self, btn, arg):
        print(
            f"Selected id:{arg.id} date:{arg.date} starter:{arg.starter_name}  jar:{arg.jar_name} distance:{arg.jar_distance}"
        )
        Screen.change(
            TrackingGrowthScreen,
            mode=Screen.REPLACE,
            args=[arg.id, arg.starter_name, arg.jar_name, arg.jar_distance],
        )
