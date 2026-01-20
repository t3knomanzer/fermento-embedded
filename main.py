from pathlib import Path

import hardware_setup
from lib.gui.core.ugui import Screen
from app.screens.splash import SplashScreen

# from app.utils import log

# log_path = (Path(__file__).parent / ".." / "logs").resolve()
# log.setup_logging(log_path, log.INFO)


def main():
    Screen.change(SplashScreen)


main()
