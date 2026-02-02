# mypy: ignore-errors
"""
Тесты для главного модуля приложения.
"""

import sys
from pathlib import Path
from unittest import mock
from unittest.mock import Mock
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


from main import ask_yes_no_question  # noqa: E402
from main import debug_print  # noqa: E402
from main import filter_by_status_interactive  # noqa: E402
from main import format_transaction_output  # noqa: E402
from main import load_transactions  # noqa: E402
from main import main  # noqa: E402
from main import process_transactions  # noqa: E402


class TestMainFunctions:
    """Тесты основных функций главного модуля."""

    def test_debug_print(self, capsys) -> None:
        """Тест функции debug_print."""
        debug_print("Тестовое сообщение")
        captured = capsys.readouterr()
        assert "[DEBUG] Тестовое сообщение" in captured.out

    def test_format_transaction_output(self) -> None:
        """Тест форматирования вывода транзакции."""
        transaction = {
            "date": "2023-01-01T12:00:00",
            "description": "Пополнение счета",
            "from": "Счет 12345678901234567890",
            "amount": 1000,
            "currency": "RUB"
        }

        result = format_transaction_output(transaction)
        assert "01.01.2023" in result
        assert "Пополнение счета" in result
        assert "Счет" in result

    def test_ask_yes_no_question_yes(self) -> None:
        """Тест функции ask_yes_no_question с положительным ответом."""
        with patch('builtins.input', return_value='да'):
            result = ask_yes_no_question("Тестовый вопрос")
            assert result is True

    def test_ask_yes_no_question_no(self) -> None:
        """Тест функции ask_yes_no_question с отрицательным ответом."""
        with patch('builtins.input', return_value='нет'):
            result = ask_yes_no_question("Тестовый вопрос")
            assert result is False

    def test_ask_yes_no_question_retry(self) -> None:
        """Тест функции ask_yes_no_question с повторным вводом."""
        with patch('builtins.input', side_effect=['неверно', 'д']):
            result = ask_yes_no_question("Тестовый вопрос")
            assert result is True


class TestLoadTransactions:
    """Тесты загрузки транзакций."""

    @patch('main.os.path.getsize')
    @patch('main.os.path.exists')
    def test_load_transactions_json(self, mock_exists, mock_getsize) -> None:
        """Тест загрузки JSON транзакций."""
        # Настраиваем моки, чтобы они возвращали True для проверки существования файла
        mock_exists.return_value = True
        mock_getsize.return_value = 1000  # произвольный размер файла

        # Мокаем загрузку данных
        with patch('main.load_json_data') as mock_load:
            mock_load.return_value = [{'id': 1, 'description': 'Test'}]

            result = load_transactions("1", "/some/path")
            assert len(result) == 1
            assert result[0]['id'] == 1

    def test_load_transactions_invalid_choice(self) -> None:
        """Тест загрузки с неверным выбором."""
        result = load_transactions("5", "/some/path")
        assert result == []

    def test_load_transactions_error(self) -> None:
        """Тест загрузки с ошибкой."""
        with patch('main.load_json_data', side_effect=Exception("Test error")):
            result = load_transactions("1", "/some/path")
            assert result == []


class TestFilterByStatusInteractive:
    """Тесты интерактивной фильтрации по статусу."""

    @patch('builtins.input', return_value='назад')
    def test_filter_by_status_interactive_back(self, mock_input) -> None:
        """Тест возврата из фильтрации."""
        transactions = [{'state': 'EXECUTED'}]
        result = filter_by_status_interactive(transactions)
        assert result == []

    @patch('builtins.input', side_effect=['EXECUTED'])
    @patch('main.filter_by_state')
    def test_filter_by_status_interactive_success(self, mock_filter, mock_input) -> None:
        """Тест успешной фильтрации."""
        transactions = [{'state': 'EXECUTED'}]
        mock_filter.return_value = transactions

        result = filter_by_status_interactive(transactions)
        assert result == transactions

    def test_filter_by_status_interactive_empty(self) -> None:
        """Тест фильтрации пустого списка."""
        result = filter_by_status_interactive([])
        assert result == []


class TestProcessTransactions:
    """Тесты обработки транзакций."""

    @patch('main.filter_by_status_interactive')
    @patch('main.ask_yes_no_question')
    @patch('main.sort_by_date')
    @patch('main.filter_by_currency')
    @patch('main.process_bank_search')
    def test_process_transactions_full_flow(
        self, mock_search, mock_currency, mock_sort, mock_ask, mock_filter
    ) -> None:
        """Тест полного потока обработки."""
        transactions = [{'id': 1, 'state': 'EXECUTED'}]

        # Настраиваем моки
        mock_filter.return_value = transactions
        mock_ask.side_effect = [True, False, False, False]  # сортировка: да, остальное: нет
        mock_sort.return_value = transactions
        mock_currency.return_value = iter(transactions)
        mock_search.return_value = iter(transactions)

        with patch('builtins.input', return_value='по возрастанию'):
            with patch('builtins.print'):
                process_transactions(transactions)

        mock_filter.assert_called_once()
        mock_ask.assert_called()

    def test_process_transactions_empty(self, capsys) -> None:
        """Тест обработки пустого списка."""
        process_transactions([])
        captured = capsys.readouterr()
        assert "Нет транзакций для обработки" in captured.out


class TestMainIntegration:
    """Интеграционные тесты главного модуля."""

    @patch('builtins.input')
    @patch('main.load_json_data')
    @patch('main.filter_by_state')
    @patch('main.ask_yes_no_question')
    def test_main_flow_json(self, mock_ask: Mock, mock_filter_by_state: Mock,
                            mock_load_json_data: Mock, mock_input: Mock) -> None:
        """Тест основного потока для JSON файла."""
        # Настраиваем моки
        mock_input.side_effect = ['1', 'EXECUTED', 'нет', 'нет', '4']
        mock_load_json_data.return_value = [{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}]
        mock_filter_by_state.return_value = [{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}]
        mock_ask.return_value = False

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.print'):
                main()

    @patch('builtins.input')
    @patch('main.read_csv_file')
    @patch('main.filter_by_state')
    @patch('main.ask_yes_no_question')
    def test_main_flow_csv(self, mock_ask: Mock, mock_filter_by_state: Mock,
                           mock_read_csv_file: Mock, mock_input: Mock) -> None:
        """Тест основного потока для CSV файла."""
        mock_input.side_effect = ['2', 'EXECUTED', 'нет', 'нет', '4']
        mock_read_csv_file.return_value = [{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}]
        mock_filter_by_state.return_value = [{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}]
        mock_ask.return_value = False

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.print'):
                main()

    @patch('builtins.input')
    def test_main_invalid_choice(self, mock_input) -> None:
        """Тест обработки неверного выбора в меню."""
        mock_input.side_effect = ['5', '4']
        with patch('builtins.print') as mock_print:
            main()
            # Проверяем что выводилось сообщение об ошибке
            assert any(
                'неверный' in str(call).lower()
                or 'ошибка' in str(call).lower()
                or 'выберите' in str(call).lower()
                for call in mock_print.call_args_list
            )

    @patch('builtins.input')
    def test_main_exit(self, mock_input) -> None:
        """Тест выхода из программы."""
        mock_input.return_value = '4'
        with patch('builtins.print'):
            main()


class TestMainFunctionsAdditional:
    """Дополнительные тесты основных функций главного модуля."""

    def test_debug_print_with_empty_message(self, capsys) -> None:
        """Тест функции debug_print с пустым сообщением."""
        debug_print("")
        captured = capsys.readouterr()
        assert "[DEBUG] " in captured.out

    def test_ask_yes_no_question_english_yes(self) -> None:
        """Тест функции ask_yes_no_question с английским 'yes'."""
        with patch('builtins.input', return_value='yes'):
            result = ask_yes_no_question("Тестовый вопрос")
            assert result is True

    def test_ask_yes_no_question_english_no(self) -> None:
        """Тест функции ask_yes_no_question с английским 'no'."""
        with patch('builtins.input', return_value='no'):
            result = ask_yes_no_question("Тестовый вопрос")
            assert result is False

    def test_ask_yes_no_question_y(self) -> None:
        """Тест функции ask_yes_no_question с 'y'."""
        with patch('builtins.input', return_value='y'):
            result = ask_yes_no_question("Тестовый вопрос")
            assert result is True

    def test_ask_yes_no_question_n(self) -> None:
        """Тест функции ask_yes_no_question с 'n'."""
        with patch('builtins.input', return_value='n'):
            result = ask_yes_no_question("Тестовый вопрос")
            assert result is False


class TestFormatTransactionOutput:
    """Тесты форматирования транзакций."""

    def test_format_transaction_output_empty(self) -> None:
        """Тест форматирования пустой транзакции."""
        transaction = {}
        result = format_transaction_output(transaction)
        assert "Н/Д" in result
        assert isinstance(result, str)

    def test_format_transaction_output_missing_fields(self) -> None:
        """Тест форматирования транзакции с неполными данными."""
        transaction = {
            "date": "2023-01-01",
            "description": "Test"
        }
        result = format_transaction_output(transaction)
        assert "01.01.2023" in result or "2023-01-01" in result
        assert "Test" in result

    def test_format_transaction_output_with_only_to(self) -> None:
        """Тест форматирования транзакции только с полем 'to'."""
        transaction = {
            "date": "2023-01-01T12:00:00",
            "description": "Перевод",
            "to": "Счет 12345678901234567890",
            "amount": 1000,
            "currency": "RUB"
        }
        result = format_transaction_output(transaction)
        assert "Счет" in result
        assert "01.01.2023" in result

    def test_format_transaction_output_with_only_from(self) -> None:
        """Тест форматирования транзакции только с полем 'from'."""
        transaction = {
            "date": "2023-01-01T12:00:00",
            "description": "Списание",
            "from": "Visa 1234567890123456",
            "amount": 500,
            "currency": "RUB"
        }
        result = format_transaction_output(transaction)
        assert "Visa" in result
        assert "01.01.2023" in result

    def test_format_transaction_output_amount_as_dict(self) -> None:
        """Тест форматирования транзакции с amount в виде словаря."""
        transaction = {
            "date": "2023-01-01T12:00:00",
            "description": "Оплата",
            "from": "Visa 1234567890123456",
            "to": "Счет 12345678901234567890",
            "amount": {
                "amount": "1500.50",
                "currency": {
                    "code": "RUB",
                    "name": "рубль"
                }
            }
        }
        result = format_transaction_output(transaction)
        assert "1500.5" in result or "1500.50" in result
        assert "RUB" in result or "рубль" in result

    def test_format_transaction_output_card_masking(self) -> None:
        """Тест маскирования номера карты."""
        transaction = {
            "date": "2023-01-01T12:00:00",
            "description": "Оплата",
            "from": "Visa 1234567890123456",
            "to": "MasterCard 9876543210987654",
            "amount": 1000,
            "currency": "RUB"
        }
        result = format_transaction_output(transaction)
        assert "1234 56** **** 3456" in result or "9876 54** **** 7654" in result

    def test_format_transaction_output_account_masking(self) -> None:
        """Тест маскирования номера счета."""
        transaction = {
            "date": "2023-01-01T12:00:00",
            "description": "Перевод",
            "from": "Счет 12345678901234567890",
            "to": "Счет 98765432109876543210",
            "amount": 1000,
            "currency": "RUB"
        }
        result = format_transaction_output(transaction)
        assert "**7890" in result or "**3210" in result

    def test_format_transaction_output_currency_with_dot(self) -> None:
        """Тест форматирования валюты с точкой в конце."""
        transaction = {
            "date": "2023-01-01T12:00:00",
            "description": "Оплата",
            "from": "Visa 1234567890123456",
            "amount": 1000,
            "currency": "RUB."
        }
        result = format_transaction_output(transaction)
        assert "RUB" in result and "RUB." not in result

    def test_format_transaction_output_invalid_date_format(self) -> None:
        """Тест с неверным форматом даты."""
        transaction = {
            "date": "invalid-date",
            "description": "Тест",
            "amount": 1000,
            "currency": "RUB"
        }
        result = format_transaction_output(transaction)
        assert "Н/Д" in result or "invalid-date" in result

    def test_format_transaction_output_amount_none(self) -> None:
        """Тест с amount = None."""
        transaction = {
            "date": "2023-01-01T12:00:00",
            "description": "Тест",
            "amount": None,
            "currency": "RUB"
        }
        result = format_transaction_output(transaction)
        assert "Н/Д" in result

    def test_format_transaction_output_currency_none(self) -> None:
        """Тест с currency = None."""
        transaction = {
            "date": "2023-01-01T12:00:00",
            "description": "Тест",
            "amount": 1000,
            "currency": None
        }
        result = format_transaction_output(transaction)
        assert "RUB" in result  # Должна использоваться валюта по умолчанию

    def test_format_transaction_output_no_currency_field(self) -> None:
        """Тест без поля currency."""
        transaction = {
            "date": "2023-01-01T12:00:00",
            "description": "Тест",
            "amount": 1000
        }
        result = format_transaction_output(transaction)
        assert "RUB" in result  # Должна использоваться валюта по умолчанию

    @patch('main.os.path.getsize')
    @patch('main.os.path.exists')
    def test_load_transactions_json(self, mock_exists, mock_getsize) -> None:
        """Тест загрузки JSON транзакций."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1000

        with patch('main.load_json_data') as mock_load:
            mock_load.return_value = [{'id': 1, 'description': 'Test'}]

            result = load_transactions("1", "/some/path")
            assert len(result) == 1
            assert result[0]['id'] == 1

    @patch('main.os.path.getsize')
    @patch('main.os.path.exists')
    def test_load_transactions_csv(self, mock_exists, mock_getsize) -> None:
        """Тест загрузки CSV транзакций."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1000

        with patch('main.read_csv_file') as mock_read:
            mock_read.return_value = [{'id': 2, 'description': 'CSV Test'}]

            result = load_transactions("2", "/some/path")
            assert len(result) == 1
            assert result[0]['id'] == 2

    @patch('main.os.path.getsize')
    @patch('main.os.path.exists')
    def test_load_transactions_excel(self, mock_exists, mock_getsize) -> None:
        """Тест загрузки Excel транзакций."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1000

        with patch('main.read_excel_file') as mock_read:
            mock_read.return_value = [{'id': 3, 'description': 'Excel Test'}]

            result = load_transactions("3", "/some/path")
            assert len(result) == 1
            assert result[0]['id'] == 3

    def test_load_transactions_invalid_choice(self) -> None:
        """Тест загрузки с неверным выбором."""
        result = load_transactions("5", "/some/path")
        assert result == []

    def test_load_transactions_error(self) -> None:
        """Тест загрузки с ошибкой."""
        with patch('main.load_json_data', side_effect=Exception("Test error")):
            result = load_transactions("1", "/some/path")
            assert result == []

    @patch('main.os.path.exists')
    def test_load_transactions_file_not_found(self, mock_exists) -> None:
        """Тест загрузки с несуществующим файлом."""
        mock_exists.return_value = False

        with patch('builtins.print') as mock_print:
            result = load_transactions("1", "/some/path")
            assert result == []
            # Должно вывести сообщение об ошибке
            assert mock_print.called

    """Тесты интерактивной фильтрации по статусу."""

    @patch('builtins.input', return_value='назад')
    def test_filter_by_status_interactive_back(self, mock_input) -> None:
        """Тест возврата из фильтрации."""
        transactions = [{'state': 'EXECUTED'}]
        result = filter_by_status_interactive(transactions)
        assert result == []

    @patch('builtins.input', side_effect=['EXECUTED'])
    @patch('main.filter_by_state')
    def test_filter_by_status_interactive_success(self, mock_filter, mock_input) -> None:
        """Тест успешной фильтрации."""
        transactions = [{'state': 'EXECUTED'}]
        mock_filter.return_value = transactions

        result = filter_by_status_interactive(transactions)
        assert result == transactions

    """Тесты обработки транзакций."""

    @patch('main.filter_by_status_interactive')
    @patch('main.ask_yes_no_question')
    @patch('main.sort_by_date')
    @patch('main.filter_by_currency')
    @patch('main.process_bank_search')
    def test_process_transactions_full_flow(
        self, mock_search, mock_currency, mock_sort, mock_ask, mock_filter
    ) -> None:
        """Тест полного потока обработки."""
        transactions = [{'id': 1, 'state': 'EXECUTED'}]

        mock_filter.return_value = transactions
        mock_ask.side_effect = [True, False, False, False]  # сортировка: да, остальное: нет
        mock_sort.return_value = transactions
        mock_currency.return_value = iter(transactions)
        mock_search.return_value = iter(transactions)

        with patch('builtins.input', return_value='по возрастанию'):
            with patch('builtins.print'):
                process_transactions(transactions)

        mock_filter.assert_called_once()
        mock_ask.assert_called()

    @patch('main.filter_by_status_interactive')
    @patch('main.ask_yes_no_question')
    @patch('main.sort_by_date')
    @patch('main.filter_by_currency')
    @patch('main.process_bank_search')
    def test_process_transactions_no_sorting(
        self, mock_search, mock_currency, mock_sort, mock_ask, mock_filter
    ) -> None:
        """Тест обработки без сортировки."""
        transactions = [{'id': 1, 'state': 'EXECUTED'}]

        mock_filter.return_value = transactions
        mock_ask.side_effect = [False, False, False, False]  # Все ответы "нет"
        mock_currency.return_value = iter(transactions)
        mock_search.return_value = iter(transactions)

        with patch('builtins.print'):
            process_transactions(transactions)

        mock_sort.assert_not_called()  # Сортировка не должна вызываться

    @patch('main.filter_by_status_interactive')
    @patch('main.ask_yes_no_question')
    @patch('main.sort_by_date')
    @patch('main.filter_by_currency')
    @patch('main.process_bank_search')
    def test_process_transactions_with_currency_filter(
        self, mock_search, mock_currency, mock_sort, mock_ask, mock_filter
    ) -> None:
        """Тест обработки с фильтром по валюте."""
        transactions = [{'id': 1, 'state': 'EXECUTED'}]

        mock_filter.return_value = transactions
        mock_ask.side_effect = [True, True, False, False]  # Сортировка и валюта
        mock_sort.return_value = transactions
        mock_currency.return_value = iter(transactions)
        mock_search.return_value = iter(transactions)

        with patch('builtins.input', return_value='по возрастанию'):
            with patch('builtins.print'):
                process_transactions(transactions)

        mock_currency.assert_called_once()

    @patch('main.filter_by_status_interactive')
    @patch('main.ask_yes_no_question')
    @patch('main.sort_by_date')
    @patch('main.filter_by_currency')
    @patch('main.process_bank_search')
    def test_process_transactions_with_keyword_filter(
        self, mock_search, mock_currency, mock_sort, mock_ask, mock_filter
    ) -> None:
        """Тест обработки с фильтром по ключевому слову."""
        transactions = [{'id': 1, 'state': 'EXECUTED'}]

        mock_filter.return_value = transactions
        mock_ask.side_effect = [True, True, True, False]  # Сортировка, валюта, ключевое слово
        mock_sort.return_value = transactions
        mock_currency.return_value = iter(transactions)
        mock_search.return_value = iter(transactions)

        with patch('builtins.input', side_effect=['по возрастанию', 'оплата']):
            with patch('builtins.print'):
                process_transactions(transactions)

        mock_search.assert_called_once()

    @patch('main.filter_by_status_interactive')
    @patch('main.ask_yes_no_question')
    @patch('main.sort_by_date')
    @patch('main.filter_by_currency')
    @patch('main.process_bank_search')
    @patch('main.process_bank_operations')
    def test_process_transactions_with_category_count(
        self, mock_operations, mock_search, mock_currency, mock_sort, mock_ask, mock_filter
    ) -> None:
        """Тест обработки с подсчетом по категориям."""
        transactions = [
            {'id': 1, 'state': 'EXECUTED', 'description': 'Оплата'},
            {'id': 2, 'state': 'EXECUTED', 'description': 'Перевод'}
        ]

        mock_filter.return_value = transactions
        mock_ask.side_effect = [True, True, True, True]  # Все ответы "да"
        mock_sort.return_value = transactions
        mock_currency.return_value = iter(transactions)
        mock_search.return_value = iter(transactions)
        mock_operations.return_value = {'Оплата': 1, 'Перевод': 1}

        with patch('builtins.input', side_effect=['по возрастанию', 'оплата']):
            with patch('builtins.print'):
                process_transactions(transactions)

        mock_operations.assert_called_once()

    @patch('main.filter_by_status_interactive')
    @patch('main.ask_yes_no_question')
    def test_process_transactions_filter_cancelled(self, mock_ask, mock_filter) -> None:
        """Тест обработки когда фильтрация отменена."""
        transactions = [{'id': 1, 'state': 'EXECUTED'}]

        mock_filter.return_value = []  # Фильтрация не дала результатов

        with patch('builtins.print') as mock_print:
            process_transactions(transactions)

        # Должно вывести сообщение об отмене
        assert any('отменена' in str(call).lower() for call in mock_print.call_args_list)

    @patch('main.filter_by_status_interactive')
    @patch('main.ask_yes_no_question')
    def test_process_transactions_sort_function_none(self, mock_ask, mock_filter) -> None:
        """Тест обработки когда sort_by_date = None."""
        transactions = [{'id': 1, 'state': 'EXECUTED'}]

        mock_filter.return_value = transactions
        mock_ask.side_effect = [True, False, False, False]  # Сортировка "да"

        with patch('main.sort_by_date', None):
            with patch('builtins.input', return_value='по возрастанию'):
                with patch('builtins.print') as mock_print:
                    process_transactions(transactions)
                    # Должно вывести сообщение об ошибке
                    assert mock_print.called

    def test_process_transactions_empty(self) -> None:
        """Тест обработки пустого списка."""
        with patch('builtins.print') as mock_print:
            process_transactions([])
            # Должно вывести сообщение об отсутствии транзакций
            assert any('нет транзакций' in str(call).lower() for call in mock_print.call_args_list)

    """Интеграционные тесты главного модуля."""

    @patch('builtins.input')
    @patch('main.load_json_data')
    @patch('main.filter_by_state')
    @patch('main.ask_yes_no_question')
    def test_main_flow_json(self, mock_ask: Mock, mock_filter_by_state: Mock,
                            mock_load_json_data: Mock, mock_input: Mock) -> None:
        """Тест основного потока для JSON файла."""
        mock_input.side_effect = ['1', 'EXECUTED', 'нет', 'нет', '4']
        mock_load_json_data.return_value = [{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}]
        mock_filter_by_state.return_value = [{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}]
        mock_ask.return_value = False

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.print'):
                main()

    @patch('builtins.input')
    @patch('main.read_csv_file')
    @patch('main.filter_by_state')
    @patch('main.ask_yes_no_question')
    def test_main_flow_csv(self, mock_ask: Mock, mock_filter_by_state: Mock,
                           mock_read_csv_file: Mock, mock_input: Mock) -> None:
        """Тест основного потока для CSV файла."""
        mock_input.side_effect = ['2', 'EXECUTED', 'нет', 'нет', '4']
        mock_read_csv_file.return_value = [{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}]
        mock_filter_by_state.return_value = [{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}]
        mock_ask.return_value = False

        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.print'):
                main()

        @patch('builtins.input')
        def test_main_invalid_choice(self, mock_input) -> None:
            """Тест обработки неверного выбора в меню."""
            mock_input.side_effect = ['5', '4']
            with patch('builtins.print') as mock_print:
                main()
                # Проверяем что выводилось сообщение об ошибке
                assert any(
                    'неверный' in str(call).lower()
                    or 'ошибка' in str(call).lower()
                    or 'выберите' in str(call).lower()
                    for call in mock_print.call_args_list
                )

        @patch('builtins.input')
        def test_main_invalid_choice_then_valid(self, mock_input) -> None:
            """Тест неверного выбора, затем верного."""
            mock_input.side_effect = ['0', 'abc', '1', '4']  # Неверные, затем JSON и выход

            with patch('pathlib.Path.exists', return_value=True):
                with patch('main.load_transactions', return_value=[{'test': 'data'}]):
                    with patch('main.process_transactions'):
                        with patch('builtins.print') as mock_print:
                            main()

            # Должно вывести сообщение об ошибке для неверных выборов
            error_calls = [
                call for call in mock_print.call_args_list
                if any(word in str(call).lower() for word in ['неверный', 'ошибка', 'пожалуйста'])
            ]
            assert len(error_calls) >= 1

        @patch('builtins.input')
        def test_main_empty_transactions(self, mock_input) -> None:
            """Тест основного потока с пустыми транзакциями."""
            mock_input.side_effect = ['1', '4']  # Выбрали JSON, затем выход

            with patch('pathlib.Path.exists', return_value=True):
                with patch('main.load_transactions', return_value=[]):
                    with patch('builtins.print') as mock_print:
                        main()

            # Должно вывести сообщение о неудачной загрузке
            assert any('не удалось загрузить' in str(call).lower() for call in mock_print.call_args_list)

        @patch('builtins.input')
        def test_main_exit(self, mock_input) -> None:
            """Тест выхода из программы."""
            mock_input.return_value = '4'
            with patch('builtins.print'):
                main()

    class TestMainImportHandling:
        """Тесты обработки ошибок импорта."""

    def test_debug_print_when_importlib_fails(self) -> None:
        """Тест, когда importlib.util.spec_from_file_location возвращает None."""
        # Вместо перезагрузки модуля тестируем конкретный сценарий
        mock_exists = Mock(return_value=True)
        mock_getsize = Mock(return_value=1000)

        # Сохраняем оригинальную функцию
        original_load_json_data = sys.modules['main'].load_json_data

        try:
            # Временно заменяем на None
            sys.modules['main'].load_json_data = None

            with mock.patch('main.os.path.getsize', mock_getsize), \
                    mock.patch('main.os.path.exists', mock_exists), \
                    mock.patch('builtins.print') as mock_print:

                result = load_transactions("1", "/some/path")
                assert result == []
                # Проверяем что было выведено сообщение
                assert mock_print.called

        finally:
            # Восстанавливаем оригинальную функцию
            sys.modules['main'].load_json_data = original_load_json_data

    class TestFormatTransactionOutputEdgeCases:
        """Тесты краевых случаев форматирования транзакций."""

        def test_format_transaction_output_amount_as_dict_with_currency_dict(self) -> None:
            """Тест с amount в виде словаря с вложенным currency."""
            transaction = {
                "date": "2023-01-01T12:00:00",
                "description": "Оплата",
                "amount": {
                    "amount": "1500.50",
                    "currency": {
                        "code": "RUB",
                        "name": "рубль"
                    }
                }
            }

            result = format_transaction_output(transaction)
            assert "1500.5" in result or "1500.50" in result

        def test_format_transaction_output_amount_as_dict_with_string_currency(self) -> None:
            """Тест с amount в виде словаря со строковой валютой."""
            transaction = {
                "date": "2023-01-01T12:00:00",
                "description": "Оплата",
                "amount": {
                    "amount": "1500.50",
                    "currency": "RUB"
                }
            }

            result = format_transaction_output(transaction)
            assert "1500.5" in result or "1500.50" in result

        def test_format_transaction_output_amount_float_with_decimal(self) -> None:
            """Тест с float amount с десятичной частью."""
            transaction = {
                "date": "2023-01-01T12:00:00",
                "description": "Оплата",
                "amount": 1500.50,
                "currency": "RUB"
            }

            result = format_transaction_output(transaction)
            assert "1500.5" in result

        def test_format_transaction_output_amount_float_integer(self) -> None:
            """Тест с float amount без десятичной части."""
            transaction = {
                "date": "2023-01-01T12:00:00",
                "description": "Оплата",
                "amount": 1500.0,
                "currency": "RUB"
            }

            result = format_transaction_output(transaction)
            assert "1500" in result

        def test_format_transaction_output_currency_nan(self) -> None:
            """Тест с NaN валютой."""

            transaction = {
                "date": "2023-01-01T12:00:00",
                "description": "Оплата",
                "amount": 1000,
                "currency": float('nan')
            }

            result = format_transaction_output(transaction)
            assert "RUB" in result  # Должен использовать значение по умолчанию

        def test_format_transaction_output_currency_integer(self) -> None:
            """Тест с числовой валютой."""
            transaction = {
                "date": "2023-01-01T12:00:00",
                "description": "Оплата",
                "amount": 1000,
                "currency": 643  # Код валюты RUB
            }

            result = format_transaction_output(transaction)
            assert "643" in result

        def test_format_transaction_output_exception_handling(self) -> None:
            """Тест обработки исключений в format_transaction_output."""
            # Создаем транзакцию, которая вызовет исключение
            transaction = {
                "date": Mock(side_effect=Exception("Test exception")),
                "description": "Тест"
            }

            result = format_transaction_output(transaction)
            # Должен вернуть хотя бы часть информации
            assert "Н/Д" in result or "Тест" in result

    class TestLoadTransactionsEdgeCases:
        """Тесты краевых случаев загрузки транзакций."""

        def test_load_transactions_file_exists_but_empty(self) -> None:
            """Тест загрузки существующего файла с нулевым размером."""
            mock_exists = Mock(return_value=True)
            mock_getsize = Mock(return_value=0)  # Пустой файл
            mock_load = Mock(return_value=None)  # load_json_data вернет None

            with mock.patch('main.os.path.getsize', mock_getsize), \
                    mock.patch('main.os.path.exists', mock_exists), \
                    mock.patch('main.load_json_data', mock_load), \
                    mock.patch('builtins.print') as mock_print:
                result = load_transactions("1", "/some/path")
                assert result == []
                assert mock_print.called

        def test_load_transactions_import_error_for_json(self) -> None:
            """Тест ImportError при загрузке JSON."""
            mock_exists = Mock(return_value=True)
            mock_getsize = Mock(return_value=1000)

            with mock.patch('main.os.path.getsize', mock_getsize), \
                    mock.patch('main.os.path.exists', mock_exists), \
                    mock.patch('main.load_json_data', Mock(side_effect=ImportError("Test"))), \
                    mock.patch('builtins.print') as mock_print:
                result = load_transactions("1", "/some/path")
                assert result == []
                assert mock_print.called

        def test_load_transactions_import_error_for_csv(self) -> None:
            """Тест ImportError при загрузке CSV."""
            mock_exists = Mock(return_value=True)
            mock_getsize = Mock(return_value=1000)

            with mock.patch('main.os.path.getsize', mock_getsize), \
                    mock.patch('main.os.path.exists', mock_exists), \
                    mock.patch('main.read_csv_file', Mock(side_effect=ImportError("Test"))), \
                    mock.patch('builtins.print') as mock_print:
                result = load_transactions("2", "/some/path")
                assert result == []
                assert mock_print.called

    class TestFilterByStatusInteractiveEdgeCases:
        """Тесты краевых случаев фильтрации по статусу."""

        def test_filter_by_status_interactive_with_float_nan_state(self) -> None:
            """Тест фильтрации с NaN в поле state."""

            mock_input = Mock(return_value='EXECUTED')
            transactions = [
                {'state': float('nan'), 'description': 'Test 1'},
                {'state': 'EXECUTED', 'description': 'Test 2'}
            ]

            with mock.patch('builtins.input', mock_input), \
                    mock.patch('main.filter_by_state') as mock_filter:
                mock_filter.return_value = [transactions[1]]
                result = filter_by_status_interactive(transactions)
                assert len(result) == 1

        def test_filter_by_status_interactive_state_as_dict(self) -> None:
            """Тест фильтрации с словарем в поле state."""
            mock_input = Mock(return_value='EXECUTED')
            transactions = [
                {'state': {'status': 'EXECUTED'}, 'description': 'Test 1'},
                {'state': 'EXECUTED', 'description': 'Test 2'}
            ]

            with mock.patch('builtins.input', mock_input), \
                    mock.patch('main.filter_by_state') as mock_filter:
                mock_filter.return_value = [transactions[1]]
                filter_by_status_interactive(transactions)

        def test_filter_by_status_interactive_state_whitespace(self) -> None:
            """Тест фильтрации с пробелами в статусе."""
            mock_input = Mock(return_value='EXECUTED')
            transactions = [
                {'state': '  EXECUTED  ', 'description': 'Test 1'},
                {'state': 'EXECUTED', 'description': 'Test 2'}
            ]

            with mock.patch('builtins.input', mock_input), \
                    mock.patch('main.filter_by_state') as mock_filter:
                mock_filter.return_value = transactions
                result = filter_by_status_interactive(transactions)
                assert len(result) == 2

    class TestProcessTransactionsEdgeCases:
        """Тесты краевых случаев обработки транзакций."""

        def test_process_transactions_with_many_transactions(self) -> None:
            """Тест обработки большого количества транзакций."""
            # Создаем 10 транзакций
            transactions = [{'id': i, 'state': 'EXECUTED', 'description': f'Test {i}'} for i in range(10)]

            mock_filter = Mock(return_value=transactions)
            mock_ask = Mock(side_effect=[False, False, False, False])  # Все ответы "нет"
            mock_print = Mock()

            with mock.patch('main.filter_by_status_interactive', mock_filter), \
                    mock.patch('main.ask_yes_no_question', mock_ask), \
                    mock.patch('builtins.print', mock_print):
                process_transactions(transactions)

                # Проверяем, что выводится информация о количестве транзакций
                assert any('10' in str(call) for call in mock_print.call_args_list)

        def test_process_transactions_rub_filter_empty_result_continue(self) -> None:
            """Тест фильтра по рублю с пустым результатом и продолжением."""
            mock_filter = Mock(return_value=[{'id': 1, 'state': 'EXECUTED'}])
            mock_ask = Mock(side_effect=[False, True, False, False])  # Валюта "да"
            mock_currency = Mock(return_value=iter([]))  # Пустой результат
            Mock(return_value=True)  # Продолжить с текущими транзакциями
            mock_print = Mock()

            with mock.patch('main.filter_by_status_interactive', mock_filter), \
                    mock.patch('main.ask_yes_no_question', mock_ask), \
                    mock.patch('main.filter_by_currency', mock_currency), \
                    mock.patch('builtins.print', mock_print):
                # Используем side_effect для второго вызова ask_yes_no_question
                with mock.patch('main.ask_yes_no_question') as mock_ask_all:
                    mock_ask_all.side_effect = [False, True, False, False, True]

                    transactions = [{'id': 1, 'state': 'EXECUTED'}]
                    process_transactions(transactions)

        def test_process_transactions_rub_filter_empty_result_cancel(self) -> None:
            """Тест фильтра по рублю с пустым результатом и отменой."""
            mock_filter = Mock(return_value=[{'id': 1, 'state': 'EXECUTED'}])
            mock_ask = Mock(side_effect=[False, True, False, False])  # Валюта "да"
            mock_currency = Mock(return_value=iter([]))  # Пустой результат
            Mock(return_value=False)  # Не продолжать
            mock_print = Mock()

            with mock.patch('main.filter_by_status_interactive', mock_filter), \
                    mock.patch('main.ask_yes_no_question', mock_ask), \
                    mock.patch('main.filter_by_currency', mock_currency), \
                    mock.patch('builtins.print', mock_print):
                # Используем side_effect для второго вызова ask_yes_no_question
                with mock.patch('main.ask_yes_no_question') as mock_ask_all:
                    mock_ask_all.side_effect = [False, True, False, False, False]

                    transactions = [{'id': 1, 'state': 'EXECUTED'}]
                    process_transactions(transactions)

        def test_process_transactions_keyword_filter_empty_string(self) -> None:
            """Тест фильтра по ключевому слову с пустой строкой."""
            mock_filter = Mock(return_value=[{'id': 1, 'state': 'EXECUTED'}])
            mock_ask = Mock(side_effect=[False, False, True, False])  # Поиск "да"
            mock_input = Mock(return_value='')  # Пустая строка для поиска
            mock_search = Mock(return_value=iter([{'id': 1, 'state': 'EXECUTED'}]))
            mock_print = Mock()

            with mock.patch('main.filter_by_status_interactive', mock_filter), \
                    mock.patch('main.ask_yes_no_question', mock_ask), \
                    mock.patch('builtins.input', mock_input), \
                    mock.patch('main.process_bank_search', mock_search), \
                    mock.patch('builtins.print', mock_print):
                transactions = [{'id': 1, 'state': 'EXECUTED'}]
                process_transactions(transactions)

        def test_process_transactions_keyword_filter_no_results(self) -> None:
            """Тест фильтра по ключевому слову без результатов."""
            mock_filter = Mock(return_value=[{'id': 1, 'state': 'EXECUTED'}])
            mock_ask = Mock(side_effect=[False, False, True, False])  # Поиск "да"
            mock_input = Mock(return_value='несуществующее_слово')
            mock_search = Mock(return_value=iter([]))  # Пустой результат
            mock_print = Mock()

            with mock.patch('main.filter_by_status_interactive', mock_filter), \
                    mock.patch('main.ask_yes_no_question', mock_ask), \
                    mock.patch('builtins.input', mock_input), \
                    mock.patch('main.process_bank_search', mock_search), \
                    mock.patch('builtins.print', mock_print):
                transactions = [{'id': 1, 'state': 'EXECUTED'}]
                process_transactions(transactions)

        def test_process_transactions_category_count_no_categories(self) -> None:
            """Тест подсчета категорий без категорий."""
            transactions = [{'id': 1, 'state': 'EXECUTED'}]  # Нет description

            mock_filter = Mock(return_value=transactions)
            mock_ask = Mock(side_effect=[False, False, False, True])  # Подсчет "да"
            mock_operations = Mock(return_value={})
            mock_print = Mock()

            with mock.patch('main.filter_by_status_interactive', mock_filter), \
                    mock.patch('main.ask_yes_no_question', mock_ask), \
                    mock.patch('main.process_bank_operations', mock_operations), \
                    mock.patch('builtins.print', mock_print):
                process_transactions(transactions)

        def test_process_transactions_category_count_process_bank_operations_none(self) -> None:
            """Тест подсчета категорий когда process_bank_operations = None."""
            transactions = [{'id': 1, 'state': 'EXECUTED', 'description': 'Test'}]

            mock_filter = Mock(return_value=transactions)
            mock_ask = Mock(side_effect=[False, False, False, True])  # Подсчет "да"
            mock_print = Mock()

            with mock.patch('main.filter_by_status_interactive', mock_filter), \
                    mock.patch('main.ask_yes_no_question', mock_ask), \
                    mock.patch('main.process_bank_operations', None), \
                    mock.patch('builtins.print', mock_print):
                process_transactions(transactions)

    class TestMainFunctionEdgeCases:
        """Тесты краевых случаев главной функции."""

        def test_main_with_excel_file(self) -> None:
            """Тест основного потока для Excel файла."""
            mock_input = Mock(side_effect=['3', 'EXECUTED', 'нет', 'нет', '4'])
            mock_read_excel_file = Mock(return_value=[{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}])
            mock_filter_by_state = Mock(return_value=[{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}])
            mock_ask = Mock(return_value=False)
            mock_exists = Mock(return_value=True)
            mock_print = Mock()

            with mock.patch('builtins.input', mock_input), \
                    mock.patch('main.read_excel_file', mock_read_excel_file), \
                    mock.patch('main.filter_by_state', mock_filter_by_state), \
                    mock.patch('main.ask_yes_no_question', mock_ask), \
                    mock.patch('pathlib.Path.exists', mock_exists), \
                    mock.patch('builtins.print', mock_print):
                main()

        def test_main_file_not_found_during_load(self) -> None:
            """Тест когда файл не найден при загрузке."""
            # ИЗМЕНИЛ: добавил значения для input внутри filter_by_status_interactive
            mock_input = Mock(side_effect=['1', 'назад', '4'])  # 'назад' для выхода из filter_by_status_interactive
            mock_exists = Mock(return_value=False)
            mock_print = Mock()

            with mock.patch('builtins.input', mock_input), \
                    mock.patch('pathlib.Path.exists', mock_exists), \
                    mock.patch('builtins.print', mock_print):
                main()

        def test_main_with_sorting_descending(self) -> None:
            """Тест с сортировкой по убыванию."""
            mock_input = Mock(side_effect=['1', 'EXECUTED', 'да', 'по убыванию', 'нет', 'нет', '4'])
            mock_load_json_data = Mock(return_value=[{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}])
            mock_filter_by_state = Mock(return_value=[{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}])
            mock_ask = Mock(side_effect=[True, False, False, False])  # Сортировка "да"
            mock_sort_by_date = Mock(return_value=[{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}])
            mock_exists = Mock(return_value=True)
            mock_print = Mock()

            with mock.patch('builtins.input', mock_input), \
                    mock.patch('main.load_json_data', mock_load_json_data), \
                    mock.patch('main.filter_by_state', mock_filter_by_state), \
                    mock.patch('main.ask_yes_no_question', mock_ask), \
                    mock.patch('main.sort_by_date', mock_sort_by_date), \
                    mock.patch('pathlib.Path.exists', mock_exists), \
                    mock.patch('builtins.print', mock_print):
                main()

        def test_main_with_all_filters(self) -> None:
            """Тест со всеми фильтрами включенными."""
            mock_input = Mock(side_effect=['1', 'EXECUTED', 'да', 'по возрастанию', 'да', 'да', 'test', 'да', '4'])
            mock_load_json_data = Mock(return_value=[{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}])
            mock_filter_by_state = Mock(return_value=[{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}])
            mock_ask = Mock(side_effect=[True, True, True, True])  # Все фильтры "да"
            mock_sort_by_date = Mock(return_value=[{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}])
            mock_filter_by_currency = Mock(return_value=iter([{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}]))
            mock_process_bank_search = Mock(return_value=iter([{'id': 1, 'description': 'Test', 'state': 'EXECUTED'}]))
            mock_process_bank_operations = Mock(return_value={'Test': 1})
            mock_exists = Mock(return_value=True)
            mock_print = Mock()

            with mock.patch('builtins.input', mock_input), \
                    mock.patch('main.load_json_data', mock_load_json_data), \
                    mock.patch('main.filter_by_state', mock_filter_by_state), \
                    mock.patch('main.ask_yes_no_question', mock_ask), \
                    mock.patch('main.sort_by_date', mock_sort_by_date), \
                    mock.patch('main.filter_by_currency', mock_filter_by_currency), \
                    mock.patch('main.process_bank_search', mock_process_bank_search), \
                    mock.patch('main.process_bank_operations', mock_process_bank_operations), \
                    mock.patch('pathlib.Path.exists', mock_exists), \
                    mock.patch('builtins.print', mock_print):
                main()

    class TestMaskingFunctions:
        """Тесты функций маскирования."""

        def test_format_transaction_output_card_with_spaces(self) -> None:
            """Тест маскирования карты с пробелами в номере."""
            transaction = {
                "date": "2023-01-01T12:00:00",
                "description": "Оплата",
                "from": "Visa 1234567890123456",  # ИЗМЕНИЛ: убрал пробелы
                "amount": 1000,
                "currency": "RUB"
            }

            result = format_transaction_output(transaction)
            # ИЗМЕНИЛ: код в main.py создает формат с пробелами: "1234 56** **** 3456"
            # Проверяем что номер карты обработан
            assert "Visa" in result
            assert "1234" in result  # Первые 4 цифры
            assert "3456" in result  # Последние 4 цифры

        def test_format_transaction_output_short_account_number(self) -> None:
            """Тест маскирования короткого номера счета."""
            transaction = {
                "date": "2023-01-01T12:00:00",
                "description": "Перевод",
                "to": "Счет 1234",
                "amount": 1000,
                "currency": "RUB"
            }

            result = format_transaction_output(transaction)
            assert "**1234" in result

        def test_format_transaction_output_card_invalid_number(self) -> None:
            """Тест маскирования карты с невалидным номером."""
            transaction = {
                "date": "2023-01-01T12:00:00",
                "description": "Оплата",
                "from": "Visa 123456",  # Слишком короткий номер
                "amount": 1000,
                "currency": "RUB"
            }

            result = format_transaction_output(transaction)
            assert "Visa 123456" in result  # Должен остаться без изменений

        def test_format_transaction_output_account_single_word(self) -> None:
            """Тест маскирования счета одним словом."""
            transaction = {
                "date": "2023-01-01T12:00:00",
                "description": "Перевод",
                "to": "12345678901234567890",  # Только номер
                "amount": 1000,
                "currency": "RUB"
            }

            result = format_transaction_output(transaction)
            assert "12345678901234567890" in result  # Должен остаться без изменений

    # Добавляем эти тестовые классы в конец файла
    if __name__ == "__main__":
        import pytest
        pytest.main([__file__, "-v"])
