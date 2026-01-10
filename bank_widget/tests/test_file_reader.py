"""
Тесты для модуля file_reader.
"""

import logging
import os
import tempfile
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.file_reader import (
    detect_file_type,
    read_csv_file,
    read_excel_file,
    read_financial_data,
)


class TestFileReader:
    """Тесты модуля file_reader."""

    def test_detect_file_type(self) -> None:
        """Тест определения типа файла."""
        assert detect_file_type("transactions.csv") == "csv"
        assert detect_file_type("data.xlsx") == "excel"
        assert detect_file_type("data.xls") == "excel"
        assert detect_file_type("operations.json") == "json"
        assert detect_file_type("unknown.txt") == "unknown"

    @patch("pathlib.Path.exists")
    @patch("pandas.read_csv")
    def test_read_csv_file_success(self, mock_read_csv: Mock, mock_exists: Mock) -> None:
        """Тест успешного чтения CSV файла."""
        # Мокаем проверку существования файла
        mock_exists.return_value = True

        # Мокаем DataFrame
        mock_df = pd.DataFrame(
            {
                "id": [1, 2],
                "amount": [100.0, 200.0],
                "currency": ["RUB", "USD"],
            }
        )
        mock_read_csv.return_value = mock_df

        result = read_csv_file("test.csv")

        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["currency"] == "USD"
        mock_read_csv.assert_called_once()

    @patch("pathlib.Path.exists")
    @patch("pandas.read_csv")
    def test_read_csv_file_empty(self, mock_read_csv: Mock, mock_exists: Mock) -> None:
        """Тест чтения пустого CSV файла."""
        mock_exists.return_value = True
        mock_df = pd.DataFrame()
        mock_read_csv.return_value = mock_df

        result = read_csv_file("test.csv")

        assert result == []

    @patch("pathlib.Path.exists")
    @patch("pandas.read_csv")
    def test_read_csv_file_encoding_fallback(self, mock_read_csv: Mock, mock_exists: Mock) -> None:
        """Тест чтения CSV с различными кодировками."""
        mock_exists.return_value = True

        # Первый вызов с utf-8 вызывает UnicodeDecodeError
        mock_read_csv.side_effect = [
            UnicodeDecodeError("utf-8", b"", 0, 1, "invalid start byte"),
            pd.DataFrame({"id": [1], "amount": [100.0]}),
        ]

        result = read_csv_file("test.csv")

        assert len(result) == 1
        assert result[0]["id"] == 1
        assert mock_read_csv.call_count == 2
        # Проверяем что второй вызов был с cp1251
        assert "encoding='cp1251'" in str(mock_read_csv.call_args_list[1])

    @patch("pathlib.Path.exists")
    @patch("pandas.read_excel")
    def test_read_excel_file_success(self, mock_read_excel: Mock, mock_exists: Mock) -> None:
        """Тест успешного чтения Excel файла."""
        mock_exists.return_value = True
        mock_df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "amount": [100.0, 200.0, 300.0],
                "currency": ["RUB", "USD", "EUR"],
            }
        )
        mock_read_excel.return_value = mock_df

        result = read_excel_file("test.xlsx")

        assert len(result) == 3
        assert result[2]["amount"] == 300.0
        mock_read_excel.assert_called_once_with("test.xlsx")

    @patch("pathlib.Path.exists")
    @patch("pandas.read_excel")
    def test_read_excel_file_with_sheet_name(self, mock_read_excel: Mock, mock_exists: Mock) -> None:
        """Тест чтения Excel файла с указанием листа."""
        mock_exists.return_value = True
        mock_df = pd.DataFrame({"id": [1], "amount": [100.0]})
        mock_read_excel.return_value = mock_df

        result = read_excel_file("test.xlsx", sheet_name="Лист1")

        assert len(result) == 1
        mock_read_excel.assert_called_once_with("test.xlsx", sheet_name="Лист1")

    @patch("pathlib.Path.exists")
    @patch("pandas.read_excel")
    def test_read_excel_file_sheet_not_found(self, mock_read_excel: Mock, mock_exists: Mock) -> None:
        """Тест чтения Excel с несуществующим листом."""
        mock_exists.return_value = True
        mock_read_excel.side_effect = ValueError("Worksheet Лист2 not found")

        with pytest.raises(ValueError, match="Лист 'Лист2' не найден"):
            read_excel_file("test.xlsx", sheet_name="Лист2")

    @patch("pathlib.Path.exists")
    def test_read_csv_file_not_found(self, mock_exists: Mock) -> None:
        """Тест чтения несуществующего CSV файла."""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError):
            read_csv_file("nonexistent.csv")

    @patch("pathlib.Path.exists")
    def test_read_excel_file_not_found(self, mock_exists: Mock) -> None:
        """Тест чтения несуществующего Excel файла."""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError):
            read_excel_file("nonexistent.xlsx")

    @patch("pathlib.Path.exists")
    @patch("src.file_reader.read_csv_file")
    def test_read_financial_data_csv(self, mock_read_csv: Mock, mock_exists: Mock) -> None:
        """Тест универсальной функции для CSV."""
        mock_exists.return_value = True
        mock_read_csv.return_value = [{"id": 1, "amount": 100.0}]

        result = read_financial_data("test.csv")

        assert len(result) == 1
        mock_read_csv.assert_called_once_with("test.csv")

    @patch("pathlib.Path.exists")
    @patch("src.file_reader.read_excel_file")
    def test_read_financial_data_excel(self, mock_read_excel: Mock, mock_exists: Mock) -> None:
        """Тест универсальной функции для Excel."""
        mock_exists.return_value = True
        mock_read_excel.return_value = [{"id": 2, "amount": 200.0}]

        result = read_financial_data("test.xlsx")

        assert len(result) == 1
        mock_read_excel.assert_called_once_with("test.xlsx", None)

    @patch("pathlib.Path.exists")
    def test_read_financial_data_json(self, mock_exists: Mock) -> None:
        """Тест универсальной функции для JSON."""
        mock_exists.return_value = True

        # Создаем временный JSON файл
        import json
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode='w') as tmp:
            tmp_path = tmp.name
            json.dump([{"id": 3, "amount": 300.0}], tmp)

        try:
            result = read_financial_data(tmp_path)
            assert len(result) == 1
            assert result[0]["id"] == 3
            assert result[0]["amount"] == 300.0
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


def test_read_financial_data_unknown_format() -> None:
    """Тест универсальной функции с неизвестным форматом."""
    with pytest.raises(ValueError, match="Неподдерживаемый формат"):
        read_financial_data("test.txt")


class TestFileReaderIntegration:
    """Интеграционные тесты с реальными файлами."""

    def test_create_and_read_csv(self) -> None:
        """Тест создания и чтения реального CSV файла."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            tmp_path = tmp.name

            # Создаем тестовый CSV
            df = pd.DataFrame(
                {
                    "id": [1, 2],
                    "date": ["2024-01-01", "2024-01-02"],
                    "amount": [100.50, 200.75],
                    "currency": ["RUB", "USD"],
                    "description": ["Покупка", "Перевод"],
                }
            )
            df.to_csv(tmp_path, index=False, encoding="utf-8")

        try:
            result = read_csv_file(tmp_path)

            assert len(result) == 2
            assert result[0]["id"] == 1
            assert result[1]["currency"] == "USD"
        finally:
            os.unlink(tmp_path)

    def test_create_and_read_excel(self) -> None:
        """Тест создания и чтения реального Excel файла."""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name

            # Создаем тестовый Excel
            df = pd.DataFrame(
                {
                    "id": [1, 2, 3],
                    "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
                    "amount": [100.0, 200.0, 300.0],
                    "currency": ["RUB", "USD", "EUR"],
                }
            )
            df.to_excel(tmp_path, index=False)

        try:
            result = read_excel_file(tmp_path)

            assert len(result) == 3
            assert result[2]["amount"] == 300.0
            assert result[0]["currency"] == "RUB"
        finally:
            os.unlink(tmp_path)


def test_logger_created() -> None:
    """Тест создания логгера для модуля file_reader."""
    from src.file_reader import logger

    assert logger.name == "bank_widget.file_reader"
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) > 0
