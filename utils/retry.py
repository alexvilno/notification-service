import asyncio
from functools import wraps
from logging import getLogger

logger = getLogger(__name__)


def retry(max_attempts: int = 3, delay: float = 1.0):
    """
    Декоратор для повторных попыток выполнения асинхронной функции
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    result = await func(*args, **kwargs)

                    if result is not False:
                        logger.info(
                            "%s успешно выполнено на попытке %i/%i",
                            func.__name__,
                            attempt,
                            max_attempts,
                        )
                        return result

                except Exception as e:
                    logger.warning(
                        "%s ошибка на попытке %i/%i: %s",
                        func.__name__,
                        attempt,
                        max_attempts,
                        e,
                    )

                    if attempt == max_attempts:
                        logger.error("все %i попыток провалились", max_attempts)
                        return False

                    await asyncio.sleep(delay * attempt)

            return False

        return wrapper

    return decorator
