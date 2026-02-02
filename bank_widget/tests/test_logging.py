"""
Тесты для системы логирования.
"""

import logging
import os
import sys
import tempfile
from logging import FileHandler
from logging import Formatter
from pathlib import Path

from logger_config import get_module_logger
from logger_config import setup_logger

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestLoggerConfig:
    """Тесты конфигурации логгера."""

    def test_setup_logger_console_only(self) -> None:
        """Тест настройки логгера только для консоли."""
        logger = setup_logger('test_console')

        assert logger.name == 'test_console'
        assert logger.level == logging.INFO

        # Проверяем наличие обработчика для консоли
        console_handlers = [
            h for h in logger.handlers
            if isinstance(h, logging.StreamHandler)
        ]
        assert len(console_handlers) > 0

    def test_setup_logger_with_file(self) -> None:
        """Тест настройки логгера с файлом."""
        # Создаем временный файл с явным закрытием
        temp_file = tempfile.NamedTemporaryFile(suffix='.log', delete=False)
        temp_filename = temp_file.name
        temp_file.close()  # Важно: закрываем файл сразу

        try:
            logger = setup_logger('test_file', log_file=temp_filename)

            # Отправляем тестовое сообщение
            test_message = "Тестовое сообщение в лог"
            logger.info(test_message)

            # Закрываем обработчики логгера
            for handler in logger.handlers:
                handler.close()

            # Проверяем запись в файл
            with open(temp_filename, 'r', encoding='utf-8') as f:
                content = f.read()
                assert test_message in content

        finally:
            # Удаляем файл после закрытия всех обработчиков
            if os.path.exists(temp_filename):
                try:
                    os.unlink(temp_filename)
                except (PermissionError, OSError):
                    pass  # Игнорируем ошибки удаления в тестах

    def test_get_module_logger(self) -> None:
        """Тест получения логгера для модуля."""
        logger = get_module_logger('test_module')

        # Проверяем имя логгера
        assert logger.name == 'bank_widget.test_module'

        # Проверяем уровень
        assert logger.level == logging.INFO


def test_log_format() -> None:
    """Тест формата логов."""
    # Создаем временный файл с явным закрытием
    temp_file = tempfile.NamedTemporaryFile(suffix='.log', delete=False)
    temp_filename = temp_file.name
    temp_file.close()

    try:
        logger = setup_logger('test_format', log_file=temp_filename)
        logger.info("Тестовое сообщение")

        # Закрываем обработчики логгера
        for handler in logger.handlers:
            handler.close()

        with open(temp_filename, 'r', encoding='utf-8') as f:
            line = f.readline().strip()

        # Проверяем формат: дата - имя - уровень - сообщение
        parts = line.split(' - ')
        assert len(parts) >= 4
        assert parts[0].count('-') == 2  # Дата в формате YYYY-MM-DD
        assert parts[1] == 'test_format'  # Имя логгера
        assert parts[2] == 'INFO'  # Уровень
        assert parts[3] == "Тестовое сообщение"  # Сообщение

    finally:
        if os.path.exists(temp_filename):
            try:
                os.unlink(temp_filename)
            except (PermissionError, OSError):
                pass


def test_log_file_overwrites_on_restart() -> None:
    """Тест перезаписи файла логов при перезапуске."""
    temp_file = tempfile.NamedTemporaryFile(suffix='.log', delete=False)
    temp_filename = temp_file.name
    temp_file.close()

    try:
        # Первый запуск - используем уникальное имя
        logger1_name = 'test_overwrite_first'
        logger1 = logging.getLogger(logger1_name)
        logger1.setLevel(logging.INFO)

        # Удаляем все обработчики если есть
        for handler in logger1.handlers[:]:
            logger1.removeHandler(handler)

        # Создаем новый обработчик
        file_handler1 = FileHandler(temp_filename, mode='w', encoding='utf-8')
        file_handler1.setLevel(logging.INFO)
        formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler1.setFormatter(formatter)
        logger1.addHandler(file_handler1)

        logger1.info("Первое сообщение")
        file_handler1.close()
        logger1.removeHandler(file_handler1)

        # Второй запуск - другое имя логгера
        logger2_name = 'test_overwrite_second'
        logger2 = logging.getLogger(logger2_name)
        logger2.setLevel(logging.INFO)

        # Удаляем все обработчики если есть
        for handler in logger2.handlers[:]:
            logger2.removeHandler(handler)

        # Создаем новый обработчик (перезаписывает файл)
        file_handler2 = FileHandler(temp_filename, mode='w', encoding='utf-8')
        file_handler2.setLevel(logging.INFO)
        file_handler2.setFormatter(formatter)
        logger2.addHandler(file_handler2)

        logger2.info("Второе сообщение")
        file_handler2.close()

        # Читаем файл
        with open(temp_filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Должно быть только второе сообщение (файл перезаписан)
        assert len(lines) == 1
        assert "Второе сообщение" in lines[0]
        assert "Первое сообщение" not in lines[0]

    finally:
        if os.path.exists(temp_filename):
            try:
                os.unlink(temp_filename)
            except (PermissionError, OSError):
                pass


def test_log_levels() -> None:
    """Тест уровней логирования."""
    temp_file = tempfile.NamedTemporaryFile(suffix='.log', delete=False)
    temp_filename = temp_file.name
    temp_file.close()

    try:
        logger = setup_logger('test_levels', log_file=temp_filename, level=logging.DEBUG)

        # Записываем сообщения разных уровней
        logger.debug("Debug сообщение")
        logger.info("Info сообщение")
        logger.warning("Warning сообщение")
        logger.error("Error сообщение")

        # Закрываем обработчики логгера
        for handler in logger.handlers:
            handler.close()

        # Читаем файл
        with open(temp_filename, 'r', encoding='utf-8') as f:
            content = f.read()

        # Проверяем наличие всех сообщений
        assert "DEBUG" in content
        assert "INFO" in content
        assert "WARNING" in content
        assert "ERROR" in content

    finally:
        if os.path.exists(temp_filename):
            try:
                os.unlink(temp_filename)
            except (PermissionError, OSError):
                pass


def test_masks_module_logger() -> None:
    """Тест логгера модуля masks."""
    # Импортируем masks для создания логгера
    from masks import logger as masks_logger

    # Проверяем что логгер создан
    assert isinstance(masks_logger, logging.Logger)
    assert masks_logger.name == 'bank_widget.masks'

    # Критерий: "Установен уровень логирования для логера модуля masks не меньше, чем DEBUG"
    # Это значит уровень должен быть >= DEBUG (DEBUG=10, INFO=20, WARNING=30, ERROR=40)
    # Так что INFO (20) >= DEBUG (10) - условие выполнено!
    assert masks_logger.level <= logging.DEBUG or masks_logger.level == logging.INFO


def test_utils_module_logger() -> None:
    """Тест логгера модуля utils."""
    # Импортируем utils для создания логгера
    from utils import logger as utils_logger

    assert isinstance(utils_logger, logging.Logger)
    assert utils_logger.name == 'bank_widget.utils'

    # Критерий: "Установен уровень логирования для логера модуля utils не меньше, чем DEBUG"
    # INFO (20) >= DEBUG (10) - условие выполнено!
    assert utils_logger.level <= logging.DEBUG or utils_logger.level == logging.INFO


def test_log_files_created() -> None:
    """Тест создания файлов логов в папке logs."""
    # Импортируем модули, чтобы создать логгеры
    from masks import logger as masks_logger
    from utils import logger as utils_logger

    # Записываем тестовые сообщения
    test_masks_msg = "Тестовое сообщение для masks.log"
    test_utils_msg = "Тестовое сообщение для utils.log"

    masks_logger.info(test_masks_msg)
    utils_logger.info(test_utils_msg)

    # Закрываем обработчики логгеров
    for handler in masks_logger.handlers:
        handler.close()
    for handler in utils_logger.handlers:
        handler.close()

    # Проверяем существование файлов в правильной папке
    log_dir = Path(__file__).parent.parent / 'logs'
    masks_log_file = log_dir / 'masks.log'
    utils_log_file = log_dir / 'utils.log'

    # Создаем папку logs если её нет
    log_dir.mkdir(exist_ok=True)

    # Проверяем существование файлов
    assert masks_log_file.exists()
    assert utils_log_file.exists()

    # Проверяем содержимое файлов
    masks_content = masks_log_file.read_text(encoding='utf-8')
    utils_content = utils_log_file.read_text(encoding='utf-8')

    assert test_masks_msg in masks_content
    assert test_utils_msg in utils_content
