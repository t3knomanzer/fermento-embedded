# qrcode.py Minimal micro-gui demo.

# Released under the MIT License (MIT). See LICENSE.
# Copyright (c) 2022 Peter Hinch

# hardware_setup must be imported before other modules because of RAM use.
import hardware_setup  # Create a display instance
from lib.gui.core.ugui import Screen, ssd
from lib.gui.widgets import Label, Button, CloseButton, QRMap

scale = 2  # Magnification of graphic
version = 4
# qr_buf = QRMap.make_buffer(version, scale)
from lib.gui.core.writer import CWriter
import lib.gui.fonts.arial10 as arial10
from lib.gui.core.colors import *


class BaseScreen(Screen):

    def __init__(self):

        def my_callback(button, graphic):
            graphic("https://en.wikipedia.org/wiki/QR_code")

        super().__init__()
        wri = CWriter(ssd, arial10, GREEN, BLACK)
        col = 2
        row = 2
        Label(wri, row, col, "QR code Demo.")
        row = 25
        graphic = QRMap(wri, row, col, version, scale)
        graphic("uQR rocks!")
        col = 120
        Button(wri, row, col, text="URL", callback=my_callback, args=(graphic,))
        CloseButton(wri)  # Quit the application


def test():
    print("QR code demo.")
    Screen.change(BaseScreen)  # A class is passed here, not an instance.


test()
