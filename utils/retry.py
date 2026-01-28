"""
Модуль с механизмов retry для асинхронных функций
"""

import asyncio
from functools import wraps
from logging import getLogger

logger = getLogger(__name__)


def retry(
        max_attempts: int = 3,
        delay: float = 1.0,
        return_value_on_fail=None
):
    """
    Декоратор для повторных попыток выполнения асинхронной функции
    :param max_attempts: максимальное число попыток
    :param delay: задержка между попытками в секундах
    :param return_value_on_fail: возвращаемое значение
     при исчерпании лимита
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):

            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)

                except Exception as last_exception:
                    logger.warning(
                        "%s ошибка на попытке %i/%i: %s",
                        func.__name__,
                        attempt,
                        max_attempts,
                        str(last_exception),
                    )

                    if attempt == max_attempts:
                        logger.error(
                            "Все %i попыток провалились: %s",
                            max_attempts,
                            str(last_exception)
                        )

                        if return_value_on_fail is not None:
                            return return_value_on_fail
                        raise last_exception

                    await asyncio.sleep(delay * attempt)

            raise RuntimeError("Retry механизм завершился некорректно")

        return wrapper

    return decorator
