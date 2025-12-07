import sys

import pytest

if __name__ == "__main__":
    # Запускаем тесты с coverage
    result = pytest.main(['tests/', '-v', '--cov=src', '--cov-report=term-missing'])
    sys.exit(result)
