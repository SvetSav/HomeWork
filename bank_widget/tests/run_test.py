import sys

import pytest

if __name__ == "__main__":
    # Запускаем тесты без проблемных опций
    result = pytest.main(['tests/', '-v', '--tb=short'])
    sys.exit(result)
