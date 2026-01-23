"""
Модели данных (сущности) - адаптировано под существующую структуру БД
"""

from dataclasses import dataclass, field
from datetime import datetime, date, time
from decimal import Decimal
from typing import List, Optional
import uuid


@dataclass
class CostCategory:
    """Категория затрат"""
    id: int = 0
    name: str = ""
    description: str = ""
    color: str = "#808080"
    created_at: Optional[datetime] = None
    is_active: bool = True

    def __str__(self):
        return self.name


@dataclass
class Nomenclature:
    """Номенклатура (блюда, напитки, услуги)"""
    id: int = 0
    name: str = ""
    category_id: int = 0
    category: Optional[CostCategory] = None
    unit: str = "шт."
    description: str = ""
    image_path: str = ""
    created_at: Optional[datetime] = None
    is_active: bool = True

    def __str__(self):
        return f"{self.name} ({self.unit})"


@dataclass
class Supplier:
    """Поставщик"""
    id: int = 0
    name: str = ""
    category_id: int = 0
    category: Optional[CostCategory] = None
    contact_person: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""
    inn: str = ""
    rating: float = 0.0
    created_at: Optional[datetime] = None
    is_active: bool = True

    def __str__(self):
        return self.name


@dataclass
class SupplierPrice:
    """Цена поставщика"""
    id: int = 0
    supplier_id: int = 0
    nomenclature_id: int = 0
    supplier: Optional[Supplier] = None
    nomenclature: Optional[Nomenclature] = None
    price: Decimal = Decimal('0.00')
    currency: str = "RUB"
    start_date: date = field(default_factory=date.today)
    end_date: Optional[date] = None
    min_quantity: Decimal = Decimal('1')
    created_at: Optional[datetime] = None

    def is_active(self, check_date: Optional[date] = None) -> bool:
        """Проверка активности цены на указанную дату"""
        if check_date is None:
            check_date = date.today()

        if self.start_date <= check_date:
            if self.end_date is None or self.end_date >= check_date:
                return True
        return False


@dataclass
class Event:
    """Мероприятие"""
    id: int = 0
    name: str = ""
    event_date: date = field(default_factory=date.today)
    start_time: time = time(10, 0)
    guests_count: int = 0
    budget: Decimal = Decimal('0.00')
    description: str = ""
    status: str = "планируется"
    location: str = ""
    responsible_person: str = ""
    created_at: Optional[datetime] = None

    def __str__(self):
        return f"{self.name} ({self.event_date.strftime('%d.%m.%Y')})"


@dataclass
class OrderItem:
    """Позиция заказа"""
    id: int = 0
    order_id: int = 0
    nomenclature_id: int = 0
    supplier_id: int = 0
    nomenclature: Optional[Nomenclature] = None
    supplier: Optional[Supplier] = None
    quantity: Decimal = Decimal('1')
    unit_price: Decimal = Decimal('0.00')
    total_price: Decimal = Decimal('0.00')
    notes: str = ""
    delivery_date: Optional[date] = None
    delivery_time: Optional[time] = None

    def __post_init__(self):
        """Автоматический расчет общей стоимости"""
        if self.total_price == Decimal('0.00'):
            self.calculate_total()

    def calculate_total(self):
        """Расчитать общую стоимость"""
        self.total_price = self.quantity * self.unit_price


@dataclass
class Order:
    """Заказ"""
    id: int = 0
    order_number: str = ""
    event_id: int = 0
    event: Optional[Event] = None
    order_date: Optional[datetime] = None
    status: str = "черновик"
    total_amount: Decimal = Decimal('0.00')
    notes: str = ""
    created_at: Optional[datetime] = None
    items: List[OrderItem] = field(default_factory=list)

    def __post_init__(self):
        """Генерация номера заказа если он не задан"""
        if not self.order_number:
            self.order_number = f"ORD-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        if not self.order_date:
            self.order_date = datetime.now()
        if not self.created_at:
            self.created_at = datetime.now()

    def __str__(self):
        return f"Заказ №{self.order_number}"

    def add_item(self, item: OrderItem):
        """Добавить позицию в заказ"""
        self.items.append(item)
        self.total_amount += item.total_price

    def remove_item(self, index: int):
        """Удалить позицию из заказа"""
        if 0 <= index < len(self.items):
            removed_item = self.items.pop(index)
            self.total_amount -= removed_item.total_price

@dataclass
class Settings:
    """Настройки приложения"""
    id: int = 1
    budget_warning_threshold: float = 0.8
    budget_alert_threshold: float = 0.9
    budget_critical_threshold: float = 1.0
    default_currency: str = "RUB"
    language: str = "ru"  # Только русский по умолчанию
    theme: str = "dark"
    auto_backup_enabled: bool = True
    backup_interval_days: int = 7
    reports_format: str = "excel"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class BudgetControl:
    """Контроль бюджета по категориям"""
    id: int = 0
    event_id: int = 0
    category_id: int = 0
    event: Optional[Event] = None
    category: Optional[CostCategory] = None
    planned_amount: Decimal = Decimal('0.00')
    actual_amount: Decimal = Decimal('0.00')
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def difference(self) -> Decimal:
        """Разница между планом и фактом"""
        return self.actual_amount - self.planned_amount

    @property
    def percentage(self) -> float:
        """Процент выполнения (факт/план)"""
        if self.planned_amount == Decimal('0.00'):
            return 0.0
        return float(self.actual_amount / self.planned_amount * 100)


# DTO (Data Transfer Objects) для отчетов
@dataclass
class ExpenseReportItem:
    """Элемент отчета по расходам"""
    category_name: str
    planned_amount: Decimal
    actual_amount: Decimal
    percentage: float = 0.0

    def __post_init__(self):
        """Расчет процента"""
        if self.planned_amount == Decimal('0.00'):
            self.percentage = 0.0
        else:
            self.percentage = float(self.actual_amount / self.planned_amount * 100)


@dataclass
class EventSummary:
    """Сводка по мероприятию"""
    event: Event
    total_orders: int
    total_amount: Decimal
    budget_utilization: float
    categories_summary: List[ExpenseReportItem]
