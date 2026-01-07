import json
import os
from typing import Any
from typing import Dict
from typing import List


def load_json_data(file_path: str) -> List[Dict[str, Any]]:
    """
    Загружает данные из JSON файла и возвращает список словарей.

    Args:
        file_path: Путь до JSON файла

    Returns:
        Список словарей с данными о финансовых транзакциях.
        Если файл пустой, содержит не список или не найден - пустой список.
    """
    try:
        # Проверяем существует ли файл
        if not os.path.exists(file_path):
            return []

        # Проверяем размер файла
        if os.path.getsize(file_path) == 0:
            return []

        # Читаем и парсим JSON
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        # Проверяем, что data - это список
        if not isinstance(data, list):
            return []

        return data

    except (json.JSONDecodeError, IOError, OSError) as e:
        # Логируем ошибку (в реальном проекте используйте logging)
        print(f"Error loading JSON file {file_path}: {e}")
        return []
    except Exception as e:
        # На всякий случай ловим все остальные исключения
        print(f"Unexpected error loading JSON file {file_path}: {e}")
        return []
