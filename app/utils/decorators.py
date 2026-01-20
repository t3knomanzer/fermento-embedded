import time
import gc


def time_it(func):
    def wrapper(*args, **kwargs):
        print(f"[time it] Called {func.__name__}")
        start = time.ticks_ms()
        result = func(*args, **kwargs)
        end = time.ticks_ms()
        elapsed = time.ticks_diff(end, start)
        print(f"[time it] {func.__name__} took {elapsed:.6f}s")
        return result

    return wrapper


def track_mem(func):
    def wrapper(*args, **kwargs):
        print(f"[track mem] {func.__name__}")
        print(
            f"[track mem] Before - Free: {gc.mem_free() / 1000}Kb -- Allocated: {gc.mem_alloc() / 1000}Kb"
        )
        result = func(*args, **kwargs)
        print(
            f"[track mem] After - Free: {gc.mem_free() / 1000}Kb -- Allocated: {gc.mem_alloc() / 1000}Kb"
        )
        return result
