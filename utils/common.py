import functools
import time
from loguru import logger


def timing(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logger.info(f"[{func.__qualname__}] executed in {end - start:.6f} seconds")
        return result

    return wrapper
