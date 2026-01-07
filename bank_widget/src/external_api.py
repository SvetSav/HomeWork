import os
from decimal import ROUND_HALF_UP
from decimal import Decimal
from decimal import InvalidOperation
from typing import Any
from typing import Dict
from typing import Optional

import requests
# Импортируем из .env
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Константы
API_URL = "https://api.apilayer.com/exchangerates_data/latest"
BASE_CURRENCY = "RUB"  # Базовая валюта - рубли


def get_exchange_rate(currency: str) -> Optional[float]:
    """
    Получает текущий курс валюты к рублю.

    Args:
        currency: Код валюты (USD, EUR и т.д.)

    Returns:
        Курс валюты к рублю или None в случае ошибки.
    """
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")

    if not api_key:
        print("API key not found in environment variables")
        return None

    if currency.upper() == "RUB":
        return 1.0

    try:
        headers = {"apikey": api_key}
        params = {"base": currency.upper(), "symbols": BASE_CURRENCY}

        response = requests.get(API_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()  # Проверяем на ошибки HTTP

        data = response.json()

        if data.get("success", False):
            rates = data.get("rates", {})
            return rates.get(BASE_CURRENCY)
        else:
            print(f"API error: {data.get('error', {}).get('info', 'Unknown error')}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except (KeyError, ValueError) as e:
        print(f"Data parsing error: {e}")
        return None


def convert_amount_to_rub(transaction: Dict[str, Any]) -> Optional[float]:
    """
    Конвертирует сумму транзакции в рубли.

    Args:
        transaction: Словарь с данными о транзакции

    Returns:
        Сумма в рублях (float) или None в случае ошибки.
    """
    try:
        # Получаем сумму и валюту
        amount = transaction.get("amount")
        currency = transaction.get("currency", "RUB").upper()

        if amount is None:
            return None

        # Преобразуем сумму в Decimal для точности
        try:
            amount_decimal = Decimal(str(amount))
        except (ValueError, TypeError, InvalidOperation):
            return None

        print(f"DEBUG: amount_decimal = {amount_decimal}")  # Отладка
        print(f"DEBUG: currency = {currency}")  # Отладка

        # Если валюта уже рубли
        if currency == "RUB":
            return float(amount_decimal)

        # Получаем курс
        rate = get_exchange_rate(currency)
        print(f"DEBUG: rate = {rate}")  # Отладка

        if rate is None:
            return None

        # Конвертируем
        rate_decimal = Decimal(str(rate))
        converted = amount_decimal * rate_decimal
        print(f"DEBUG: converted = {converted}")  # Отладка

        # Округляем до 2 знаков после запятой
        rounded = converted.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        print(f"DEBUG: rounded = {rounded}")  # Отладка

        return float(rounded)

    except (ValueError, TypeError, AttributeError, InvalidOperation) as e:
        print(f"Error converting amount: {e}")
        return None
