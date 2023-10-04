import os
import time
from functools import wraps

try:
    from loguru import logger
except:
    os.system(f"pip install loguru")
    from loguru import logger


def yommi_timeit(func):
    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        total_time = end_time - start_time
        # print(f"Function {func.__name__}{args} {kwargs} Took {total_time:.4f} secs")
        logger.opt(colors=True).debug(
            f"<red>{func.__name__}{args} {kwargs}</red> function took <green>{total_time:.4f}</green>secs"
        )
        return result

    return timeit_wrapper


def yommi_async_timeit(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            return await func(*args, **kwargs)
        finally:
            total_time = time.perf_counter() - start_time
            logger.opt(colors=True).debug(
                f"<red>{func.__name__}{args} {kwargs}</red> function took <green>{total_time:.4f}</green>secs"
            )

    return wrapper
