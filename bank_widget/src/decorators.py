"""
Модуль декораторов для логирования.
Содержит декоратор log для логирования работы функций.
"""

import datetime
import functools
from typing import Any, Callable, Optional


def log(filename: Optional[str] = None) -> Callable:
    """
    Декоратор для логирования работы функций.

    Args:
        filename: Имя файла для записи логов. Если None, логи выводятся в консоль.

    Returns:
        Декоратор функции.

    Examples:
        >>> @log()
        ... def add(a, b):
        ...     return a + b
        >>> add(1, 2)
        add ok

        >>> @log("mylog.txt")
        ... def divide(a, b):
        ...     return a / b
        >>> divide(10, 2)  # Запишет в файл: "divide ok"
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Формируем строку с входными параметрами
            args_str = ", ".join(repr(arg) for arg in args)
            kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())
            params_str = f"({args_str})" if not kwargs_str else f"({args_str}, {kwargs_str})"
            if args_str and kwargs_str:
                params_str = f"({args_str}, {kwargs_str})"
            elif not args_str and kwargs_str:
                params_str = f"({kwargs_str})"

            try:
                # Выполняем функцию
                result = func(*args, **kwargs)
                # Формируем сообщение об успехе
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                success_message = f"{timestamp} - {func.__name__} ok\n"

                # Логируем в файл или консоль
                if filename:
                    with open(filename, "a", encoding="utf-8") as f:
                        f.write(success_message)
                else:
                    print(success_message.strip())

                return result

            except Exception as e:
                # Формируем сообщение об ошибке
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                error_message = f"{timestamp} - {func.__name__} error: {type(e).__name__}. Inputs: {params_str}\n"

                # Логируем в файл или консоль
                if filename:
                    with open(filename, "a", encoding="utf-8") as f:
                        f.write(error_message)
                else:
                    print(error_message.strip())

                # Пробрасываем исключение дальше
                raise

        return wrapper

    return decorator
