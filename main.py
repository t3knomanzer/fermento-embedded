import config
from app.services import log

# Setup logging
log.LogServiceManager.initialize(level=log.DEBUG, max_files=config.LOG_MAX_FILES)

import hardware_setup
from app.screens.splash import SplashScreen
from lib.gui.core.ugui import Screen

logger = log.LogServiceManager.get_logger(name=__name__)


def main():
    logger.info("Starting app...")
    Screen.change(SplashScreen)


main()
