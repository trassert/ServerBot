"Модуль для получения из value телеграма список выпавших предметов"

mapping = {"0": "Бар", "1": "Ягода", "2": "Лимон", "3": "7"}


def get(value: int) -> int:
    return [
        str((value - 1) & 3),
        str(((value - 1) >> 2) & 3),
        str(((value - 1) >> 4) & 3),
    ]
