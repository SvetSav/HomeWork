# Банковский виджет
Простой инструмент для работы с банковскими операциями: маскировка данных, форматирование дат, фильтрация и сортировка операций.

Что умеет проект?
1. Маскировка данных:
Скрывает номера банковских карт и номера счетов: 
- **Карты:** `7000 79** **** 6361`
- **Счета:** `**4305`

2. Конвертирует даты:

`2024-03-11T02:26:18.671407` → `11.03.2024`

3. Обработка операций:

- **Фильтрация:** по статусу (EXECUTED, CANCELED)
- **Сортировка:** по дате

# Установка:

1. Клонируйте репозиторий:
```
git clone https://github.com/SvetSav/HomeWork.git
```
2. Установите зависимости:
```
pip install -r requirements.txt
```
# Использование:

1. Откройте приложение в вашем PyCharm.
2. Создайте новый проект и начните добавлять задачи.

# Примеры работы виджета

### Пример 1: Маскировка данных:
### Карта
card = "Visa Platinum 7000792289606361"
print(mask_account_card(card))
#### Результат: Visa Platinum 7000 79** **** 6361

### Счет
account = "Счет 73654108430135874305"
#### Результат: Счет **4305

### Пример 2: Форматирование даты:

date_str = "2024-03-11T02:26:18.671407"
#### Результат: 11.03.2024

# Модуль generators

Модуль содержит генераторы для работы с банковскими транзакциями.

## Функции

### `filter_by_currency(transactions, currency)`
Фильтрует транзакции по заданной валюте.

from src.generators import filter_by_currency

usd_transactions = filter_by_currency(transactions, "USD")
for transaction in usd_transactions:
    print(transaction["id"], transaction["operationAmount"]["amount"])

### `transaction_descriptions(transactions)`
Возвращает описания транзакций.

from src.generators import transaction_descriptions

descriptions = transaction_descriptions(transactions)
for description in descriptions:
    print(description)

### `card_number_generator(start, end)`
Генерирует номера банковских карт в заданном диапазоне.

from src.generators import card_number_generator

for card_number in card_number_generator(1, 5):
    print(card_number)
#### Вывод:
#### 0000 0000 0000 0001
#### 0000 0000 0000 0002
#### 0000 0000 0000 0003
#### 0000 0000 0000 0004
#### 0000 0000 0000 0005

# Тестирование

## Запустите все тесты!
python -m pytest tests/ -v

# Или конкретный тест (например):
### Тесты для маскировки данных
python -m pytest tests/test_masks.py -v

### Тесты для обработки операций
python -m pytest tests/test_processing.py -v

### Тесты для основного виджета
python -m pytest tests/test_widget.py -v

### Тесты для generators
pytest tests/test_generators.py -v

# Проверьте покрытие
pytest --cov=src tests/ --cov-report=html

Откройте отчет о покрытии
start htmlcov/index.html

# Особенности тестирования
* Параметризация тестов - множественные тест-кейсы в одном тесте
* Фикстуры - предопределённые тестовые данные в conftest.py
* Покрытие кода > 80% - автоматическая проверка покрытия
* Отчёт в HTML формате - визуализация результатов тестирования

# Документация:

Для получения дополнительной информации обратитесь к [документации](docs/README.md).

# Лицензия:
Этот проект лицензирован по [лицензии MIT](LICENSE).
