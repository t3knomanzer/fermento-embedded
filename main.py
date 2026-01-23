import config
from app.services import log

# Setup logging
log.LogServiceManager.set_name("Fermento")
log.LogServiceManager.set_level(log.DEBUG)
log.LogServiceManager.set_filepath(config.LOG_FILEPATH)

import hardware_setup
from app.screens.splash import SplashScreen
from lib.gui.core.ugui import Screen

logger = log.LogServiceManager.get_logger(name=__name__)


def main():
    logger.info("Starting app...")
    Screen.change(SplashScreen)


main()
