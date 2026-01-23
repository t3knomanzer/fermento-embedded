from app.services.log import LogServiceManager
from app.services.web.wifi_manager import WifiManager

import config

# Create logger
logger = LogServiceManager.get_logger(name=__name__)


class NetworkService:
    def __init__(self):
        self._wm = WifiManager(
            ssid=config.WIFI_SSID, password=config.WIFI_PASS, reboot=True
        )

    def start_server(self):
        self._wm.web_server()

    def connect(self):
        return self._wm.connect()
