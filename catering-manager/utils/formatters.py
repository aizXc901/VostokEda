"""
Форматирование данных
"""

from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional, Union
from config import Config

class Formatters:
    """Класс для форматирования данных"""

    @staticmethod
    def format_date(d: date) -> str:
        """Форматировать дату в строку дд.мм.гггг"""
        if not d:
            return ""
        return d.strftime("%d.%m.%Y")

    @staticmethod
    def format_time(t: Union[time, str], format_str: str = "%H:%M") -> str:
        """Форматирование времени"""
        if isinstance(t, str):
            try:
                if ':' in t:
                    hours, minutes = map(int, t.split(':'))
                    t = time(hours, minutes)
            except ValueError:
                return t

        if isinstance(t, time):
            return t.strftime(format_str)
        return str(t)

    @staticmethod
    def format_datetime(dt: datetime, format_str: str = "%d.%m.%Y %H:%M") -> str:
        """Форматирование даты и времени"""
        return dt.strftime(format_str)

    @staticmethod
    def format_currency(amount: Union[Decimal, float, int, str],
                        show_symbol: bool = True) -> str:
        """Форматирование денежной суммы"""
        if isinstance(amount, str):
            try:
                amount = Decimal(amount.replace(',', '.'))
            except:
                return amount

        if isinstance(amount, (int, float)):
            amount = Decimal(str(amount))

        # Форматируем с разделителями тысяч
        formatted = f"{amount:,.{Config.DECIMAL_PLACES}f}"

        if show_symbol:
            return f"{formatted} {Config.CURRENCY_SYMBOL}"
        return formatted

    @staticmethod
    def format_percentage(value: float, decimals: int = 1) -> str:
        """Форматирование процента"""
        return f"{value:.{decimals}f}%"

    @staticmethod
    def format_quantity(quantity: Union[Decimal, float], unit: str = "") -> str:
        """Форматирование количества"""
        if isinstance(quantity, float):
            quantity = Decimal(str(quantity))

        # Убираем лишние нули после запятой
        if quantity == quantity.to_integral():
            formatted = f"{int(quantity)}"
        else:
            formatted = f"{quantity:.3f}".rstrip('0').rstrip('.')

        if unit:
            return f"{formatted} {unit}"
        return formatted

    @staticmethod
    def truncate_text(text: str, max_length: int) -> str:
        """Обрезать текст до максимальной длины"""
        if not text:
            return ""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
