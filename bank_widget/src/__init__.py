"""
Пакет банковского виджета.
"""

from .decorators import log
from .file_reader import detect_file_type
from .file_reader import read_csv_file
from .file_reader import read_excel_file
from .file_reader import read_financial_data
from .generators import card_number_generator
from .generators import filter_by_currency
from .generators import transaction_descriptions
from .main import main
from .masks import get_mask_account
from .masks import get_mask_card_number
from .operations import count_transactions_by_category
from .operations import filter_transactions_by_currency
from .operations import search_transactions_by_description
from .processing import filter_by_state
from .processing import sort_by_date
from .widget import get_date
from .widget import mask_account_card
from .widget import mask_account_number
from .widget import mask_card_number

__all__ = [
    'get_mask_card_number',
    'get_mask_account',
    'mask_account_card',
    'get_date',
    'mask_card_number',
    'mask_account_number',
    'filter_by_state',
    'sort_by_date',
    'filter_by_currency',
    'transaction_descriptions',
    'card_number_generator',
    'log',
    # Новые функции для работы с файлами
    'read_csv_file',
    'read_excel_file',
    'read_financial_data',
    'detect_file_type',
    # Новые функции для операций
    'search_transactions_by_description',
    'count_transactions_by_category',
    'filter_transactions_by_currency',
    # Главная функция
    'main',
]
