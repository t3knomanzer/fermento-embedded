import gc
from app.services.log import LogServiceManager

logger = LogServiceManager.get_logger(name=__name__)


def print_mem():
    logger.debug(
        f"Free: {gc.mem_free() / 1000}Kb -- Allocated: {gc.mem_alloc() / 1000}Kb"
    )
