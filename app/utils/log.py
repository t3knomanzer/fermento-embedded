import os
import logging
import inspect
from pathlib import Path

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL


def setup_logging(filepath: str, level: int, name: str = None) -> logging.Logger:
    # Get the file path of the calling module
    caller_filepath = inspect.stack()[1].filename

    # Extract the file name without extension to be used as the logger name
    if name:
        caller_name = name
    else:
        caller_name = Path(caller_filepath).stem

    # Create the log output folder
    Path(filepath).mkdir(parents=True, exist_ok=True)

    # Remove the log file if it exists
    log_path = Path(filepath) / f"{caller_name}.log"
    log_path.unlink(missing_ok=True)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s][%(name)s] %(message)s",
        datefmt="%m/%d/%y %H:%M:%S",
    )
    logger = logging.getLogger(caller_name)
    logger.setLevel(level)

    file_handler = logging.FileHandler(log_path.as_posix())
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
