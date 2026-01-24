from app.utils.pathing import file_exists
from app.utils.time import now_str, ntp_is_set

DEBUG = 0
INFO = 10
WARNING = 20
ERROR = 30
CRITICAL = 40

LEVEL_NAMES = {
    DEBUG: "DEBUG",
    INFO: "INFO",
    WARNING: "WARNING",
    ERROR: "ERROR",
    CRITICAL: "CRITICAL",
}


class LogServiceManager:
    _filename = ""
    _services = {}
    _level = INFO

    def _generate_filename(
        root_name: str = "app", extension: str = ".log", max_files: int = 3
    ) -> str:
        for i in range(max_files):
            target_filename = f"{root_name}{i + 1}{extension}"
            if not file_exists(target_filename):
                filename = target_filename
                break

        if not target_filename:
            target_filename = f"{root_name}{1}{extension}"

        return target_filename

    @classmethod
    def _set_level(cls, level: int) -> None:
        cls._level = level

    @classmethod
    def _set_filename(
        cls,
        root_name: str = "app",
        extension: str = ".log",
        max_files: int = 3,
    ) -> None:
        cls._filename = cls._generate_filename(root_name, extension, max_files)

    @classmethod
    def initialize(
        cls, filename: str = "app", level: int = INFO, max_files: int = 3
    ) -> None:
        cls._set_filename(root_name=filename, max_files=max_files)
        cls._set_level(level)

    @classmethod
    def get_logger(cls, name: str | None = None) -> "LogService":
        if name not in cls._services:
            cls._services[name] = LogService(name, cls._filename, cls._level)
        return cls._services[name]


class LogService:
    def __init__(self, name: str, filename: str, level: int = INFO):
        self._name = name
        self._filename = filename
        self._level = level

    def set_level(self, level: str) -> None:
        self._level = level

    def set_filename(self, filename: str) -> None:
        self._filename = filename

    def _build_message(self, message: str, level: int, name: str | None = None) -> str:
        time = f"[{now_str()}]" if ntp_is_set() else ""
        return f"{time}[{LEVEL_NAMES[level]}][{name or self._name}] {message}"

    def _log_console(self, message: str, level: int, name: str | None = None):
        msg = self._build_message(message, level, name)
        print(msg)

    def _log_file(self, message: str, level: int, name: str | None = None):
        msg = self._build_message(message, level, name)
        try:
            with open(self._filename, "a+") as fh:
                fh.write(msg + "\n")
        except Exception as e:
            self._log_console(
                f"Error writing log to file: {self._filename}, {e}", ERROR
            )

    def log(self, message: str, level: int, name: str | None = None):
        if level >= self._level:
            self._log_console(message, level, name)
            self._log_file(message, level, name)

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
