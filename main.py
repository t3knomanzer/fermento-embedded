from pathlib import Path
from app.services import log

# Setup logging
log_path = Path(".").parent.resolve()
log_filepath = Path(log_path) / "app.log"
log.LogServiceManager.set_name("Fermento")
log.LogServiceManager.set_level(log.DEBUG)
log.LogServiceManager.set_filepath(log_filepath)

import hardware_setup
from app.screens.splash import SplashScreen
from lib.gui.core.ugui import Screen

logger = log.LogServiceManager.get_logger(name=__name__)

def main():
    logger.info("Starting app...")
    Screen.change(SplashScreen)

main()
