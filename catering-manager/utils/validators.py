"""
Валидация данных
"""

from datetime import datetime, date, time
from decimal import Decimal
from typing import Optional
import re


class Validators:
    """Класс для валидации данных"""

    @staticmethod
    def validate_date(date_str: str, allow_past: bool = True) -> Optional[date]:
        """Валидация даты"""
        try:
            parsed_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if not allow_past and parsed_date < date.today():
                return None
            return parsed_date
        except (ValueError, TypeError):
            try:
                # Попробуем российский формат
                parsed_date = datetime.strptime(date_str, '%d.%m.%Y').date()
                if not allow_past and parsed_date < date.today():
                    return None
                return parsed_date
            except (ValueError, TypeError):
                return None

    @staticmethod
    def validate_time(time_str: str) -> Optional[time]:
        """Валидация времени"""
        try:
            if ':' in time_str:
                hours, minutes = map(int, time_str.split(':'))
                if 0 <= hours < 24 and 0 <= minutes < 60:
                    return time(hours, minutes)
        except (ValueError, TypeError):
            pass
        return None

    @staticmethod
    def validate_decimal(value: str) -> Optional[Decimal]:
        """Валидация десятичного числа"""
        try:
            # Заменяем запятую на точку
            clean_value = value.replace(',', '.').replace(' ', '')
            return Decimal(clean_value)
        except (ValueError, TypeError, ArithmeticError):
            return None

    @staticmethod
    def validate_integer(value: str) -> Optional[int]:
        """Валидация целого числа"""
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def validate_email(email: str) -> bool:
        """Валидация email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Валидация телефона"""
        # Удаляем все нецифровые символы кроме +
        clean_phone = re.sub(r'[^\d+]', '', phone)
        return len(clean_phone) >= 10

    @staticmethod
    def validate_inn(inn: str) -> bool:
        """Валидация ИНН"""
        # Простая проверка - только цифры и длина 10 или 12
        clean_inn = re.sub(r'\D', '', inn)
        return len(clean_inn) in [10, 12]

    @staticmethod
    def check_order_deadline(event_date: date, order_date: datetime) -> bool:
        """
        Проверка что заказ создается не позднее чем за сутки до мероприятия
        """
        from datetime import timedelta
        deadline = event_date - timedelta(days=1)
        return order_date.date() <= deadline
