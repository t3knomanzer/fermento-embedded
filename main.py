import gc
from sys import exit

import hardware_setup
from lib.gui.core.ugui import Screen
from lib.gui.core.ugui import ssd
from app.screens.splash import SplashScreen
from app.screens.main_menu import MainMenuScreen

from app.utils.utils import print_mem
from app.services.network import NetworkService


def display_error(error):
    ssd.text(error, 4, ssd.height // 2, 1)
    ssd.show()


def main():
    Screen.change(SplashScreen)


main()
