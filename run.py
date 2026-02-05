#!/usr/bin/env python3
"""
Точка входа для запуска экспериментов.

Использование:
    python run.py status              # Статус всех экспериментов
    python run.py list                # Список пар и сценариев
    python run.py run pair_01         # Запустить эксперименты для pair_01
    python run.py run pair_01 --scenario colleague  # Другой сценарий
    python run.py run pair_01 --dry-run  # Проверка без запуска
"""

import sys
from pathlib import Path

# Добавляем src в path
sys.path.insert(0, str(Path(__file__).parent))

from src.experiment_runner import main

if __name__ == "__main__":
    main()
