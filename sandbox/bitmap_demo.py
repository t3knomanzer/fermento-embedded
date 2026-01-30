import hardware_setup  # Create a display instance

from gui.core.ugui import Screen, ssd
from gui.core.writer import Writer
import gui.fonts.arial10 as arial10
from gui.widgets.bitmap import BitMap
from gui.core.colors import WHITE, BLACK


class BaseScreen(Screen):
    def __init__(self):
        writer = Writer(ssd, arial10, verbose=False)
        super().__init__(writer)

        bmp_size = (100, 60)
        col = ssd.width // 2 - bmp_size[0] // 2
        row = ssd.height // -+bmp_size[1] // 2
        try:
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
            self.graphic.value(path := "fermento_logo")
        except Exception as e:
            print(e)


print("Bitmap demo.")
Screen.change(BaseScreen)  # A class is passed here, not an instance.
