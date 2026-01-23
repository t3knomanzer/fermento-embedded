import time
import gc

from app.services.log import LogServiceManager

logger = LogServiceManager.get_logger(name=__name__)


def time_it(func):
    def wrapper(*args, **kwargs):
        logger.debug(f"Time: Called {func.__name__}")
        start = time.ticks_ms()
        result = func(*args, **kwargs)
        end = time.ticks_ms()
        elapsed = time.ticks_diff(end, start)
        logger.debug(f"Time: {func.__name__} took {elapsed:.6f}s")
        return result

    return wrapper


def track_mem(func):
    def wrapper(*args, **kwargs):
        logger.debug(
            f"Mem: {func.__name__} Before - Free: {gc.mem_free() / 1000}Kb -- Allocated: {gc.mem_alloc() / 1000}Kb"
        )
        result = func(*args, **kwargs)
        logger.debug(
            f"Mem: {func.__name__} After - Free: {gc.mem_free() / 1000}Kb -- Allocated: {gc.mem_alloc() / 1000}Kb"
        )
        return result

    return wrapper
