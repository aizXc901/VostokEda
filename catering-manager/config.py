"""
Конфигурация приложения
"""

import os
from pathlib import Path

# Базовые пути
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = BASE_DIR / "images"
REPORTS_DIR = BASE_DIR / "reports"

# Создание директорий если их нет
for directory in [DATA_DIR, IMAGES_DIR, REPORTS_DIR]:
    directory.mkdir(exist_ok=True)

class Config:
    """Класс конфигурации"""

    # Настройки базы данных
    DATABASE_PATH = "catering.db"
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

    # Настройки приложения
    APP_NAME = "Catering Manager"
    APP_VERSION = "1.0.0"
    APP_COMPANY = "АО 'ТехноХолдинг 'Восток'"

    # Настройки интерфейса
    THEME = "dark"  # "dark" или "light"
    PRIMARY_COLOR = "#2FA572"  # Основной цвет
    SECONDARY_COLOR = "#3A7CA5"  # Вторичный цвет

    # Настройки валюты
    CURRENCY = "RUB"
    CURRENCY_SYMBOL = "₽"
    DECIMAL_PLACES = 2

    # Настройки бюджета
    BUDGET_WARNING_THRESHOLD = 0.8  # 80% - предупреждение (желтый)
    BUDGET_ALERT_THRESHOLD = 0.9    # 90% - опасность (оранжевый)
    BUDGET_CRITICAL_THRESHOLD = 1.0 # 100% - критично (красный)

    # Настройки заказов
    MIN_ORDER_DAYS_BEFORE_EVENT = 1  # Минимальное количество дней до мероприятия для заказа
    DEFAULT_VAT_RATE = 0.2  # НДС по умолчанию (20%)

    # Цвета для категорий (по умолчанию)
    CATEGORY_COLORS = {
        "Продукты/готовые блюда": "#FF6B6B",
        "Напитки": "#4ECDC4",
        "Оборудование": "#FFD166",
        "Персонал": "#06D6A0",
        "Транспорт": "#118AB2",
        "Прочие расходы": "#9D4EDD"
    }

    # Логирование
    LOG_LEVEL = "INFO"
    LOG_FILE = DATA_DIR / "app.log"

    @staticmethod
    def get_database_path() -> Path:
        """Получить путь к базе данных"""
        return Config.DATABASE_PATH

    @staticmethod
    def get_currency_symbol() -> str:
        """Получить символ валюты"""
        return Config.CURRENCY_SYMBOL

    @staticmethod
    def format_currency(amount: float) -> str:
        """Форматировать сумму валюты"""
        return f"{amount:,.{Config.DECIMAL_PLACES}f} {Config.CURRENCY_SYMBOL}"

    @staticmethod
    def get_category_color(category_name: str) -> str:
        """Получить цвет для категории"""
        return Config.CATEGORY_COLORS.get(category_name, "#808080")

    @staticmethod
    def get_log_level() -> str:
        """Получить уровень логирования"""
        return Config.LOG_LEVEL

    @staticmethod
    def get_log_file() -> Path:
        """Получить путь к файлу лога"""
        return Config.LOG_FILE
