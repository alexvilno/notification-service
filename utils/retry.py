"""
Модуль с механизмов retry для асинхронных функций
"""

import asyncio
from functools import wraps
from logging import getLogger

from service.notifications.exceptions import MaxRetriesExceeded

logger = getLogger(__name__)


def retry(max_attempts: int = 3, delay: float = 1.0):
    """
    Декоратор для повторных попыток выполнения асинхронной функции
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(1, max_attempts + 1):
                try:
                    result = await func(*args, **kwargs)

                    logger.info(
                        "%s успешно выполнено на попытке %i/%i",
                        func.__name__,
                        attempt,
                        max_attempts,
                    )
                    return result

                except Exception as e:
                    last_exception = e
                    logger.warning(
                        "%s ошибка на попытке %i/%i: %s",
                        func.__name__,
                        attempt,
                        max_attempts,
                        str(e),
                    )

                    if attempt == max_attempts:
                        logger.error(
                            "Все %i попыток провалились: %s",
                            max_attempts,
                            str(last_exception)
                        )
                        raise MaxRetriesExceeded()  # Пробрасываем исключение дальше!

                    await asyncio.sleep(delay * attempt)

            raise RuntimeError("Retry механизм завершился некорректно")

        return wrapper

    return decorator
