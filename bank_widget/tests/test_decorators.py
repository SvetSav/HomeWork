"""
Тесты для модуля decorators.
"""

import os
import sys
import tempfile
from typing import Any
from typing import Callable

import pytest
from decorators import log

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestLogDecorator:
    """Тесты для декоратора log."""

    def test_log_to_console_success(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Тест логирования успешного выполнения в консоль."""
        @log()  # type: ignore
        def add(a: int, b: int) -> int:
            return a + b

        result = add(2, 3)

        # Проверяем результат функции
        assert result == 5

        # Проверяем вывод в консоль
        captured = capsys.readouterr()
        assert "add ok" in captured.out

    def test_log_to_console_error(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Тест логирования ошибки в консоль."""
        @log()  # type: ignore
        def divide(a: int, b: int) -> float:
            return a / b

        # Вызываем функцию с ошибкой
        with pytest.raises(ZeroDivisionError):
            divide(10, 0)

        # Проверяем вывод в консоль
        captured = capsys.readouterr()
        assert "divide error: ZeroDivisionError" in captured.out
        assert "Inputs: (10, 0)" in captured.out or "Inputs: (10, 0, )" in captured.out

    def test_log_to_file_success(self) -> None:
        """Тест логирования успешного выполнения в файл."""
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmp:
            tmp_filename = tmp.name

        try:
            @log(filename=tmp_filename)  # type: ignore
            def multiply(a: int, b: int) -> int:
                return a * b

            result = multiply(4, 5)

            # Проверяем результат функции
            assert result == 20

            # Проверяем запись в файл
            with open(tmp_filename, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "multiply ok" in content

        finally:
            # Удаляем временный файл
            if os.path.exists(tmp_filename):
                os.unlink(tmp_filename)

    def test_log_to_file_error(self) -> None:
        """Тест логирования ошибки в файл."""
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as tmp:
            tmp_filename = tmp.name

        try:
            @log(filename=tmp_filename)  # type: ignore
            def get_item(lst: list, index: int) -> Any:
                return lst[index]

            # Вызываем функцию с ошибкой
            with pytest.raises(IndexError):
                get_item([], 5)

            # Проверяем запись в файл
            with open(tmp_filename, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "get_item error: IndexError" in content
                assert "Inputs: ([], 5)" in content or "Inputs: ([], 5, )" in content

        finally:
            # Удаляем временный файл
            if os.path.exists(tmp_filename):
                os.unlink(tmp_filename)

    def test_log_with_keyword_arguments(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Тест логирования функции с keyword arguments."""
        @log()  # type: ignore
        def greet(name: str, greeting: str = "Hello") -> str:
            return f"{greeting}, {name}!"

        result = greet("Alice", greeting="Hi")

        # Проверяем результат функции
        assert result == "Hi, Alice!"

        # Проверяем вывод в консоль
        captured = capsys.readouterr()
        assert "greet ok" in captured.out

    def test_log_with_no_arguments(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Тест логирования функции без аргументов."""
        @log()  # type: ignore
        def get_pi() -> float:
            return 3.14159

        result = get_pi()

        # Проверяем результат функции
        assert result == 3.14159

        # Проверяем вывод в консоль
        captured = capsys.readouterr()
        assert "get_pi ok" in captured.out

    def test_log_preserves_function_metadata(self) -> None:
        """Тест, что декоратор сохраняет метаданные функции."""
        @log()  # type: ignore
        def example_func(x: int, y: int) -> int:
            """Пример функции для теста."""
            return x + y

        # Проверяем сохранение имени
        assert example_func.__name__ == "example_func"

        # Проверяем сохранение документации
        assert "Пример функции для теста" in example_func.__doc__

    def test_multiple_calls_logging(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Тест логирования нескольких вызовов функции."""
        @log()  # type: ignore
        def increment(x: int) -> int:
            return x + 1

        # Вызываем функцию несколько раз
        assert increment(1) == 2
        assert increment(5) == 6
        assert increment(10) == 11

        # Проверяем что все вызовы залогированы
        captured = capsys.readouterr()
        lines = captured.out.strip().split('\n')
        assert len(lines) == 3
        assert all("increment ok" in line for line in lines)

    def test_log_with_custom_exception(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Тест логирования пользовательского исключения."""
        class CustomError(Exception):
            pass

        @log()  # type: ignore
        def raise_custom_error() -> None:
            raise CustomError("Что-то пошло не так")

        # Вызываем функцию с пользовательским исключением
        with pytest.raises(CustomError):
            raise_custom_error()

        # Проверяем вывод в консоль
        captured = capsys.readouterr()
        assert "raise_custom_error error: CustomError" in captured.out

    @pytest.mark.parametrize("func,args,kwargs,expected_result,should_fail", [
        (lambda x, y: x + y, (1, 2), {}, 3, False),  # Успех
        (lambda x, y: x / y, (10, 0), {}, None, True),  # Ошибка деления на 0
        (lambda s: s.upper(), ("hello",), {}, "HELLO", False),  # Успех
        (lambda lst, i: lst[i], ([], 5), {}, None, True),  # Ошибка индекса
    ])
    def test_log_parametrized(self, capsys: pytest.CaptureFixture[str],
                              func: Callable[..., Any], args: tuple, kwargs: dict,
                              expected_result: Any, should_fail: bool) -> None:
        """Параметризованный тест декоратора log."""
        decorated_func = log()(func)

        if should_fail:
            with pytest.raises(Exception):
                decorated_func(*args, **kwargs)
        else:
            result = decorated_func(*args, **kwargs)
            assert result == expected_result

        # Проверяем что что-то было выведено
        captured = capsys.readouterr()
        assert captured.out != ""
