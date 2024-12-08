

from datetime import datetime, timedelta
from typing import Optional, Dict
from functools import wraps
import bittensor as bt


def execute_periodically(period: timedelta):
    """
    Decorator to execute a coroutine function periodically based on the specified period.

    Args:
        period (timedelta): The time interval between each execution of the decorated function.

    Returns:
        Callable: Decorated coroutine function.
    """
    def decorator(func):
        last_operation_date: Optional[datetime] = None

        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal last_operation_date
            if (
                not last_operation_date
                or datetime.now() - last_operation_date > period
            ):
                result = await func(*args, **kwargs)
                last_operation_date = datetime.now()
                return result
            else:
                bt.logging.debug(
                    f"Skipping {func.__name__}, period has not yet passed."
                )
                return None

        return wrapper

    return decorator