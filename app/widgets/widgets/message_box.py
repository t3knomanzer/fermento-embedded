# dialog.py Extension to ugui providing the DialogBox class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

import asyncio
from gui.core.ugui import display, Window, Screen, ssd
from gui.core.colors import *
from gui.widgets.label import Label
from gui.widgets.buttons import Button, CloseButton

dolittle = lambda *_: None


class MessageBox(Window):
    def __init__(
        self,
        writer,
        row=20,
        col=20,
        *,
        message="Placeholder",
        closebutton=False,
        time=None
    ):

        height = ssd.height // 2 - 4
        width = ssd.width - 4
        row = height // 2
        col = 2
        super().__init__(row, col, height, width, writer=writer)

        row = ssd.height // 2 - writer.height
        col = ssd.width // 2 - writer.stringlen(message) // 2
        Label(writer, row, col, message)

        if closebutton:
            CloseButton(writer, callback=self.back)

        if time:
            asyncio.create_task(self.countdown(time))

    async def countdown(self, time):
        await asyncio.sleep(time)
        self.back(None)

    def back(self, button):
        Screen.back()
