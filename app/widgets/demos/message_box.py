# dialog.py micro-gui demo of the DialogBox class

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2021 Peter Hinch

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, Window, ssd

from gui.widgets import Label, Button, CloseButton
from gui.core.writer import Writer

# Font for CWriter
import lib.gui.fonts.arial10 as arial10
from gui.core.colors import *

from app.widgets.widgets.message_box import MessageBox


class BaseScreen(Screen):

    def __init__(self):
        super().__init__()

        # Callback for Button
        def open_dialog(button, kwargs_):
            Screen.change(MessageBox, kwargs=kwargs_)

        writer = Writer(ssd, arial10)

        # DialogBox constructor arguments. Here we pass all as keyword wargs.
        kwargs = {"writer": writer, "message": "Test dialog!", "time": 3}
        Button(
            writer,
            ssd.width // 2 - 15,
            ssd.height // 2,
            text="Dialog",
            callback=open_dialog,
            args=(kwargs,),
        )
        CloseButton(writer)  # Quit the application

    # Refresh the label after DialogBox has closed (but not when
    # the screen first opens).
    def after_open(self):
        if (v := Window.value()) is not None:
            self.lbl.value("Result: {}".format(v))


def test():
    print("DialogBox demo.")
    Screen.change(BaseScreen)


test()
