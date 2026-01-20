"""
Контроллеры бизнес-логики приложения
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple, Dict, Any
import logging

from config import Config
from models import *
from database import DatabaseManager
from utils.validators import Validators
from utils.formatters import Formatters

logger = logging.getLogger(__name__)

class CateringController:
    """Основной контроллер приложения"""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or DatabaseManager()
        self.current_event: Optional[Event] = None
        self.current_order: Optional[Order] = None

    # ===== Управление категориями =====
    def _get_budget_status_color(self, usage: float) -> str:
        """Определить цвет статуса бюджета"""
        if usage < Config.BUDGET_WARNING_THRESHOLD:  # <--- Исправлено
            return "green"
        elif usage < Config.BUDGET_ALERT_THRESHOLD:  # <--- Исправлено
            return "yellow"
        elif usage < Config.BUDGET_CRITICAL_THRESHOLD:  # <--- Исправлено
            return "orange"
        else:
            return "red"

    def get_all_categories(self) -> List[CostCategory]:
        """Получить все категории затрат"""
        return self.db.get_all_categories()

    def add_category(self, name: str, description: str = "", color: str = "") -> Tuple[bool, str]:
        """Добавить новую категорию затрат"""
        if not name.strip():
            return False, "Название категории не может быть пустым"

        # Проверяем, нет ли уже такой категории
        existing = self.db.get_category_by_name(name)
        if existing:
            return False, f"Категория '{name}' уже существует"

        # Определяем цвет, если не задан
        if not color:
            color = Config.get_category_color(name)

        category = CostCategory(
            name=name.strip(),
            description=description.strip(),
            color=color
        )

        try:
            category_id = self.db.add_category(category)
            return True, f"Категория '{name}' успешно добавлена (ID: {category_id})"
        except Exception as e:
            logger.error(f"Ошибка добавления категории: {e}")
            return False, f"Ошибка при добавлении категории: {str(e)}"

    # ===== Управление номенклатурой =====

    def get_all_nomenclatures(self) -> List[Nomenclature]:
        """Получить всю номенклатуру"""
        return self.db.get_all_nomenclatures()

    def add_nomenclature(self, name: str, category_id: int,
                         unit: str = "шт.", description: str = "") -> Tuple[bool, str]:
        """Добавить новую позицию номенклатуры"""
        if not name.strip():
            return False, "Название позиции не может быть пустым"

        if not category_id:
            return False, "Необходимо указать категорию"

        nomenclature = Nomenclature(
            name=name.strip(),
            category_id=category_id,
            unit=unit.strip(),
            description=description.strip()
        )

        try:
            nomenclature_id = self.db.add_nomenclature(nomenclature)
            return True, f"Позиция '{name}' успешно добавлена (ID: {nomenclature_id})"
        except Exception as e:
            logger.error(f"Ошибка добавления номенклатуры: {e}")
            return False, f"Ошибка при добавлении позиции: {str(e)}"

    def get_nomenclatures_by_category(self, category_id: int) -> List[Nomenclature]:
        """Получить номенклатуру по категории"""
        all_nomenclatures = self.db.get_all_nomenclatures()
        return [n for n in all_nomenclatures if n.category_id == category_id]

    # ===== Управление поставщиками =====

    def get_all_suppliers(self) -> List[Supplier]:
        """Получить всех поставщиков"""
        return self.db.get_all_suppliers()

    def add_supplier(self, name: str, category_id: int, contact_person: str = "",
                     phone: str = "", email: str = "", address: str = "",
                     inn: str = "", rating: float = 0.0) -> Tuple[bool, str]:
        """Добавить нового поставщика"""
        if not name.strip():
            return False, "Название поставщика не может быть пустым"

        if not category_id:
            return False, "Необходимо указать категорию поставщика"

        # Валидация email
        if email and not Validators.validate_email(email):
            return False, "Неверный формат email"

        # Валидация ИНН
        if inn and not Validators.validate_inn(inn):
            return False, "Неверный формат ИНН"

        supplier = Supplier(
            name=name.strip(),
            category_id=category_id,
            contact_person=contact_person.strip(),
            phone=phone.strip(),
            email=email.strip(),
            address=address.strip(),
            inn=inn.strip(),
            rating=rating
        )

        try:
            supplier_id = self.db.add_supplier(supplier)
            return True, f"Поставщик '{name}' успешно добавлен (ID: {supplier_id})"
        except Exception as e:
            logger.error(f"Ошибка добавления поставщика: {e}")
            return False, f"Ошибка при добавлении поставщика: {str(e)}"

    # ===== Управление мероприятиями =====

    def get_all_events(self) -> List[Event]:
        """Получить все мероприятия"""
        return self.db.get_all_events()

    def add_event(self, name: str, event_date: date, start_time: time, guests_count: int, budget: Decimal,
                  description: str = "", location: str = "", responsible_person: str = "", 
                  status: str = "планируется") -> Tuple[bool, str]:
        """Добавить мероприятие"""
        try:
            event = Event(
                name=name,
                event_date=event_date,
                start_time=start_time,
                guests_count=guests_count,
                budget=budget,
                description=description,
                location=location,
                responsible_person=responsible_person,
                status=status,
                created_at=datetime.now()
            )

            event_id = self.db.add_event(event)
            return True, f"Мероприятие '{name}' успешно добавлено (ID: {event_id})"
        except Exception as e:
            logger.error(f"Ошибка добавления мероприятия: {e}")
            return False, f"Ошибка: {str(e)}"

    def select_event(self, event_id: int) -> bool:
        """Выбрать текущее мероприятие"""
        events = self.db.get_all_events()
        for event in events:
            if event.id == event_id:
                self.current_event = event
                return True
        return False

    # ===== Управление заказами =====

    def create_new_order(self) -> Order:
        """Создать новый заказ для текущего мероприятия"""
        if not self.current_event:
            raise ValueError("Не выбрано мероприятие")

        self.current_order = Order(
            event_id=self.current_event.id,
            event=self.current_event
        )
        return self.current_order

    def add_item_to_order(self, nomenclature_id: int, supplier_id: int,
                          quantity: Decimal, unit_price: Optional[Decimal] = None) -> Tuple[bool, str]:
        """Добавить позицию в текущий заказ"""
        if not self.current_order:
            return False, "Сначала создайте заказ"

        # Получаем информацию о номенклатуре и поставщике
        nomenclature = self.db.get_nomenclature_by_id(nomenclature_id)
        if not nomenclature:
            return False, "Номенклатура не найдена"

        # Получаем актуальную цену если не указана
        if unit_price is None:
            prices = self.db.get_prices_for_nomenclature(nomenclature_id)
            supplier_prices = [p for p in prices if p.supplier_id == supplier_id]

            if not supplier_prices:
                return False, "Не найдена цена для выбранного поставщика"

            unit_price = supplier_prices[0].price

        # Проверяем минимальное количество если есть
        # (пропускаем для упрощения)

        # Создаем позицию заказа
        item = OrderItem(
            nomenclature_id=nomenclature_id,
            supplier_id=supplier_id,
            nomenclature=nomenclature,
            quantity=quantity,
            unit_price=unit_price
        )

        # Проверяем бюджет
        if self.current_event:
            new_total = self.current_order.total_amount + item.total_price
            budget_usage = new_total / self.current_event.budget

            if budget_usage > Config.BUDGET_CRITICAL_THRESHOLD:
                return False, f"Превышение бюджета на {Formatters.format_percentage((budget_usage - 1) * 100)}"
            elif budget_usage > Config.BUDGET_ALERT_THRESHOLD:
                # Предупреждение, но разрешаем
                self.current_order.add_item(item)
                warning_msg = f"Внимание: использовано {Formatters.format_percentage(budget_usage * 100)} бюджета"
                return True, warning_msg

        self.current_order.add_item(item)
        return True, f"Позиция добавлена. Сумма: {Formatters.format_currency(item.total_price)}"

    def save_current_order(self, notes: str = "") -> Tuple[bool, str]:
        """Сохранить текущий заказ"""
        if not self.current_order:
            return False, "Нет активного заказа"

        if not self.current_order.items:
            return False, "Заказ не может быть пустым"

        # Проверяем срок заказа (не позднее чем за сутки до мероприятия)
        if self.current_event:
            if not Validators.check_order_deadline(
                    self.current_event.event_date,
                    self.current_order.order_date
            ):
                return False, "Заказ можно формировать не позднее чем за сутки до мероприятия"

        # Устанавливаем примечания
        self.current_order.notes = notes

        try:
            order_id = self.db.create_order(self.current_order)
            self.current_order.id = order_id

            # Обновляем контроль бюджета
            self._update_budget_controls()

            message = f"Заказ №{self.current_order.order_number} сохранен. " \
                      f"Сумма: {Formatters.format_currency(self.current_order.total_amount)}"

            # Сбрасываем текущий заказ
            saved_order = self.current_order
            self.current_order = None

            return True, message
        except Exception as e:
            logger.error(f"Ошибка сохранения заказа: {e}")
            return False, f"Ошибка при сохранении заказа: {str(e)}"

    def get_orders_for_current_event(self) -> List[Order]:
        """Получить заказы для текущего мероприятия"""
        if not self.current_event:
            return []
        return self.db.get_orders_for_event(self.current_event.id)

    # ===== Контроль бюджета =====

    def _update_budget_controls(self):
        """Обновить контроль бюджета после сохранения заказа"""
        if not self.current_event or not self.current_order:
            return

        # Здесь должна быть логика обновления budget_controls
        # В твоей структуре таблицы нет planned_amount,
        # поэтому просто записываем фактические расходы
        pass

    def get_budget_status(self) -> Dict[str, Any]:
        """Получить статус бюджета текущего мероприятия"""
        if not self.current_event:
            return {}

        orders = self.get_orders_for_current_event()
        total_spent = sum(order.total_amount for order in orders)
        budget = self.current_event.budget

        if budget == Decimal('0'):
            percentage = 0.0
        else:
            percentage = float(total_spent / budget * 100)

        remaining = budget - total_spent

        return {
            'budget': budget,
            'spent': total_spent,
            'remaining': remaining,
            'percentage': percentage,
            'status': self._get_budget_status_color(percentage / 100),
            'orders_count': len(orders)
        }

    def _get_budget_status_color(self, usage: float) -> str:
        """Определить цвет статуса бюджета"""
        if usage < Config.BUDGET_WARNING_THRESHOLD:
            return "green"
        elif usage < Config.BUDGET_ALERT_THRESHOLD:
            return "yellow"
        elif usage < Config.BUDGET_CRITICAL_THRESHOLD:
            return "orange"
        else:
            return "red"

    # ===== Отчеты =====

    def get_expense_report(self, event_id: Optional[int] = None) -> Optional[EventSummary]:
        """Получить отчет по расходам"""
        if not event_id and self.current_event:
            event_id = self.current_event.id

        if not event_id:
            return None

        # Получаем мероприятие
        events = self.db.get_all_events()
        event = next((e for e in events if e.id == event_id), None)
        if not event:
            return None

        # Получаем заказы
        orders = self.db.get_orders_for_event(event_id)
        total_amount = sum(order.total_amount for order in orders)

        # Получаем детализацию по категориям
        categories_summary = self.db.get_expense_report(event_id)

        # Рассчитываем использование бюджета
        if event.budget == Decimal('0'):
            budget_utilization = 0.0
        else:
            budget_utilization = float(total_amount / event.budget * 100)

        return EventSummary(
            event=event,
            total_orders=len(orders),
            total_amount=total_amount,
            budget_utilization=budget_utilization,
            categories_summary=categories_summary
        )

    # ===== Утилиты =====

    def populate_test_data(self):
        """Заполнить базу тестовыми данными"""
        self.db.populate_test_data()
        return True, "Тестовые данные успешно добавлены"
