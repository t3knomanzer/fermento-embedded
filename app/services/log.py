import os
import logging

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


class LogServiceManager:
    _name = "Fermento"
    _filepath = ""
    _services = {}
    _level = INFO

    @classmethod
    def set_level(cls, level: int) -> None:
        cls._level = level
        for k, v in enumerate(cls._services):
            v.set_level(level)

    @classmethod
    def set_name(cls, name: str) -> None:
        cls._name = name

    @classmethod
    def set_filepath(cls, filepath: str) -> None:
        # Remove the log file if it exists
        if os.path.exists(filepath):
            os.remove(filepath)
        cls._filepath = filepath

        # Create the log output folder
        cls._filepath.parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_logger(cls, name: str | None = None) -> "LogService":
        name_ = name if name else cls._name
        if name_ not in cls._services:
            cls._services[name_] = LogService(name_, cls._filepath, cls._level)
        return cls._services[name_]


class LogService:
    def __init__(self, name: str, filepath: str, level: int = INFO):
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s][%(name)s] %(message)s",
            datefmt="%m/%d/%y %H:%M:%S",
        )

        self._logger = logging.getLogger(name)
        self._logger.setLevel(level)

        file_handler = logging.FileHandler(filepath)
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

    def log(self, message: str, level: int, name: str | None = None):
        self._logger.log(level, message)

    def info(self, message: str):
        self.log(message, INFO)

    def warning(self, message: str):
        self.log(message, WARNING)

    def error(self, message: str):
        self.log(message, ERROR)

    def critical(self, message: str):
        self.log(message, CRITICAL)

    def debug(self, message: str):
        self.log(message, DEBUG)
