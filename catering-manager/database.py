"""
Модуль работы с существующей базой данных SQLite
Структура таблиц уже определена
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, date, time
from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import logging

from config import Config
from models import *

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Менеджер базы данных для работы с существующей структурой"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Config.get_database_path()
        logger.info(f"Использую базу данных: {self.db_path}")

    @contextmanager
    def get_connection(self):
        """Контекстный менеджер для соединения с БД"""
        conn = None
        try:
            conn = sqlite3.connect(
                str(self.db_path),
                detect_types=sqlite3.PARSE_DECLTYPES
            )
            conn.row_factory = sqlite3.Row
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Ошибка базы данных: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def check_tables_exist(self) -> Dict[str, bool]:
        """Проверить существование всех таблиц"""
        tables = [
            'cost_categories',
            'nomenclatures',
            'suppliers',
            'supplier_prices',
            'events',
            'orders',
            'order_items',
            'budget_controls',
            'settings'  # Добавляем проверку таблицы настроек
        ]

        result = {}
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for table in tables:
                cursor.execute(f"""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, (table,))
                result[table] = cursor.fetchone() is not None

        return result

    # ===== CRUD для cost_categories =====

    def get_all_categories(self) -> List[CostCategory]:
        """Получить все категории затрат"""
        categories = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cost_categories ORDER BY name")
            rows = cursor.fetchall()

            for row in rows:
                categories.append(CostCategory(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'] or '',
                    color=row['color'] if 'color' in row.keys() else '#808080',
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now(),
                    is_active=bool(row['is_active']) if 'is_active' in row.keys() else True
                ))

        return categories

    def get_category_by_id(self, category_id: int) -> Optional[CostCategory]:
        """Получить категорию по ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cost_categories WHERE id = ?", (category_id,))
            row = cursor.fetchone()

            if row:
                return CostCategory(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'] or '',
                    color=row['color'] if 'color' in row.keys() else '#808080',
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now(),
                    is_active=bool(row['is_active']) if 'is_active' in row.keys() else True
                )
        return None

    def get_category_by_name(self, name: str) -> Optional[CostCategory]:
        """Получить категорию по имени"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM cost_categories WHERE name = ?", (name,))
            row = cursor.fetchone()

            if row:
                return CostCategory(
                    id=row['id'],
                    name=row['name'],
                    description=row['description'] or '',
                    color=row['color'] if 'color' in row.keys() else '#808080',
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now(),
                    is_active=bool(row['is_active']) if 'is_active' in row.keys() else True
                )
        return None

    def add_category(self, category: CostCategory) -> int:
        """Добавить новую категорию"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO cost_categories (name, description, color, created_at, is_active)
                VALUES (?, ?, ?, ?, ?)
            """, (
                category.name,
                category.description,
                category.color,
                category.created_at.isoformat() if category.created_at else datetime.now().isoformat(),
                1 if category.is_active else 0
            ))
            conn.commit()
            return cursor.lastrowid

    def update_category(self, category: CostCategory) -> bool:
        """Обновить категорию"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE cost_categories 
                SET name = ?, description = ?, color = ?, is_active = ?
                WHERE id = ?
            """, (
                category.name,
                category.description,
                category.color,
                1 if category.is_active else 0,
                category.id
            ))
            conn.commit()
            return cursor.rowcount > 0

    # ===== CRUD для nomenclatures =====

    def get_all_nomenclatures(self) -> List[Nomenclature]:
        """Получить всю номенклатуру"""
        nomenclatures = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT n.*, c.name as category_name, c.color as category_color
                FROM nomenclatures n
                LEFT JOIN cost_categories c ON n.category_id = c.id
                ORDER BY n.name
            """)
            rows = cursor.fetchall()

            for row in rows:
                category = None
                if row['category_id']:
                    category = CostCategory(
                        id=row['category_id'],
                        name=row['category_name'] or '',
                        color=row['category_color'] or '#808080'
                    )

                nomenclatures.append(Nomenclature(
                    id=row['id'],
                    name=row['name'],
                    category_id=row['category_id'],
                    category=category,
                    unit=row['unit'] or 'шт.',
                    description=row['description'] or '',
                    image_path=row['image_path'] or '',
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now(),
                    is_active=bool(row['is_active'])
                ))

        return nomenclatures

    def get_nomenclature_by_id(self, nomenclature_id: int) -> Optional[Nomenclature]:
        """Получить номенклатуру по ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT n.*, c.name as category_name, c.color as category_color
                FROM nomenclatures n
                LEFT JOIN cost_categories c ON n.category_id = c.id
                WHERE n.id = ?
            """, (nomenclature_id,))
            row = cursor.fetchone()

            if row:
                category = None
                if row['category_id']:
                    category = CostCategory(
                        id=row['category_id'],
                        name=row['category_name'] or '',
                        color=row['category_color'] or '#808080'
                    )

                return Nomenclature(
                    id=row['id'],
                    name=row['name'],
                    category_id=row['category_id'],
                    category=category,
                    unit=row['unit'] or 'шт.',
                    description=row['description'] or '',
                    image_path=row['image_path'] or '',
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now(),
                    is_active=bool(row['is_active'])
                )
        return None

    def add_nomenclature(self, nomenclature: Nomenclature) -> int:
        """Добавить новую номенклатуру"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO nomenclatures 
                (name, category_id, unit, description, image_path, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                nomenclature.name,
                nomenclature.category_id,
                nomenclature.unit,
                nomenclature.description,
                nomenclature.image_path,
                nomenclature.created_at.isoformat() if nomenclature.created_at else datetime.now().isoformat(),
                1 if nomenclature.is_active else 0
            ))
            conn.commit()
            return cursor.lastrowid

    # ===== CRUD для suppliers =====

    def get_all_suppliers(self) -> List[Supplier]:
        """Получить всех поставщиков"""
        suppliers = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.*, c.name as category_name, c.color as category_color
                FROM suppliers s
                LEFT JOIN cost_categories c ON s.category_id = c.id
                ORDER BY s.name
            """)
            rows = cursor.fetchall()

            for row in rows:
                category = None
                if row['category_id']:
                    category = CostCategory(
                        id=row['category_id'],
                        name=row['category_name'] or '',
                        color=row['category_color'] or '#808080'
                    )

                suppliers.append(Supplier(
                    id=row['id'],
                    name=row['name'],
                    category_id=row['category_id'],
                    category=category,
                    contact_person=row['contact_person'] or '',
                    phone=row['phone'] or '',
                    email=row['email'] or '',
                    address=row['address'] or '',
                    inn=row['inn'] or '',
                    rating=row['rating'] or 0.0,
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now(),
                    is_active=bool(row['is_active'])
                ))

        return suppliers

    def add_supplier(self, supplier: Supplier) -> int:
        """Добавить нового поставщика"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO suppliers 
                (name, category_id, contact_person, phone, email, address, inn, rating, created_at, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                supplier.name,
                supplier.category_id,
                supplier.contact_person,
                supplier.phone,
                supplier.email,
                supplier.address,
                supplier.inn,
                supplier.rating,
                supplier.created_at.isoformat() if supplier.created_at else datetime.now().isoformat(),
                1 if supplier.is_active else 0
            ))
            conn.commit()
            return cursor.lastrowid

    # ===== CRUD для supplier_prices =====

    def get_prices_for_nomenclature(self, nomenclature_id: int, check_date: Optional[date] = None) -> List[SupplierPrice]:
        """Получить цены на номенклатуру на определенную дату"""
        if check_date is None:
            check_date = date.today()

        prices = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sp.*, s.name as supplier_name, n.name as nomenclature_name
                FROM supplier_prices sp
                JOIN suppliers s ON sp.supplier_id = s.id
                JOIN nomenclatures n ON sp.nomenclature_id = n.id
                WHERE sp.nomenclature_id = ? 
                AND sp.start_date <= ?
                AND (sp.end_date IS NULL OR sp.end_date >= ?)
                ORDER BY sp.price
            """, (nomenclature_id, check_date.isoformat(), check_date.isoformat()))

            rows = cursor.fetchall()
            for row in rows:
                start_date = date.fromisoformat(row['start_date']) if row['start_date'] else check_date
                end_date = date.fromisoformat(row['end_date']) if row['end_date'] else None
                
                prices.append(SupplierPrice(
                    id=row['id'],
                    supplier_id=row['supplier_id'],
                    nomenclature_id=row['nomenclature_id'],
                    price=Decimal(str(row['price'])),
                    currency=row['currency'] if 'currency' in row.keys() else 'RUB',
                    start_date=start_date,
                    end_date=end_date,
                    min_quantity=Decimal(str(row['min_quantity'])) if 'min_quantity' in row.keys() else Decimal('1')
                ))

        return prices

    def add_supplier_price(self, price: SupplierPrice) -> int:
        """Добавить цену поставщика"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO supplier_prices 
                (supplier_id, nomenclature_id, price, currency, start_date, end_date, min_quantity)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                price.supplier_id,
                price.nomenclature_id,
                float(price.price),
                price.currency,
                price.start_date.isoformat(),
                price.end_date.isoformat() if price.end_date else None,
                float(price.min_quantity)
            ))
            conn.commit()
            return cursor.lastrowid

    # ===== CRUD для events =====

    def get_all_events(self) -> List[Event]:
        """Получить все мероприятия"""
        events = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM events ORDER BY event_date DESC")
            rows = cursor.fetchall()

            for row in rows:
                # Парсим время
                event_time = time(10, 0)  # По умолчанию 10:00
                if row['start_time']:
                    try:
                        if ':' in row['start_time']:
                            hours, minutes = map(int, row['start_time'].split(':'))
                            event_time = time(hours, minutes)
                    except:
                        pass

                events.append(Event(
                    id=row['id'],
                    name=row['name'],
                    event_date=date.fromisoformat(row['event_date']),
                    start_time=event_time,
                    guests_count=row['guests_count'],
                    budget=Decimal(str(row['budget'])),
                    description=row['description'] or '',
                    status=row['status'] or 'планируется',
                    location=row['location'] or '',
                    responsible_person=row['responsible_person'] or '',
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now()
                ))

        return events

    def add_event(self, event: Event) -> int:
        """Добавить новое мероприятие"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events 
                (name, event_date, start_time, guests_count, budget, description, 
                 status, location, responsible_person, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.name,
                event.event_date.isoformat(),
                event.start_time.strftime('%H:%M'),
                event.guests_count,
                float(event.budget),
                event.description,
                event.status,
                event.location,
                event.responsible_person,
                event.created_at.isoformat() if event.created_at else datetime.now().isoformat()
            ))
            conn.commit()
            return cursor.lastrowid

    # ===== CRUD для orders =====

    def add_item_to_order(self, nomenclature_id: int, supplier_id: int,
                          quantity: Decimal, unit_price: Optional[Decimal] = None) -> Tuple[bool, str]:
        """Добавить позицию в текущий заказ"""
        if not self.current_order:
            return False, "Сначала создайте заказ"

        # Получаем информацию о номенклатуре и поставщике
        nomenclature = self.db.get_nomenclature_by_id(nomenclature_id)
        if not nomenclature:
            return False, "Номенклатура не найдена"

        supplier = next((s for s in self.get_all_suppliers() if s.id == supplier_id), None)
        if not supplier:
            return False, "Поставщик не найден"

        # Получаем актуальную цену если не указана
        if unit_price is None:
            prices = self.db.get_prices_for_nomenclature(nomenclature_id)
            supplier_prices = [p for p in prices if p.supplier_id == supplier_id]

            if not supplier_prices:
                return False, "Не найдена цена для выбранного поставщика"

            unit_price = supplier_prices[0].price

        # Создаем позицию заказа
        item = OrderItem(
            nomenclature_id=nomenclature_id,
            supplier_id=supplier_id,
            nomenclature=nomenclature,
            supplier=supplier,
            quantity=quantity,
            unit_price=unit_price
        )

        # Проверяем бюджет
        if self.current_event:
            new_total = self.current_order.total_amount + item.total_price
            budget_usage = new_total / self.current_event.budget

            if budget_usage > Config.BUDGET_CRITICAL_THRESHOLD:
                return False, f"Превышение бюджета на {Formatters.format_percentage((budget_usage - 1) * 100)}%"
            elif budget_usage > Config.BUDGET_ALERT_THRESHOLD:
                # Предупреждение, но разрешаем
                self.current_order.add_item(item)
                warning_msg = f"Внимание: использовано {Formatters.format_percentage(budget_usage * 100)}% бюджета"
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
            from datetime import timedelta
            deadline = self.current_event.event_date - timedelta(days=1)
            if self.current_order.order_date.date() > deadline:
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

    def get_settings(self) -> Settings:
        """Получить настройки приложения"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM settings WHERE id = 1")
            row = cursor.fetchone()

            if row:
                return Settings(
                    id=row['id'],
                    budget_warning_threshold=float(row['budget_warning_threshold']),
                    budget_alert_threshold=float(row['budget_alert_threshold']),
                    budget_critical_threshold=float(row['budget_critical_threshold']),
                    default_currency=row['default_currency'],
                    language=row['language'],
                    theme=row['theme'],
                    auto_backup_enabled=bool(row['auto_backup_enabled']),
                    backup_interval_days=row['backup_interval_days'],
                    reports_format=row['reports_format'],
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now(),
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else datetime.now()
                )

        # Если настройки не найдены, возвращаем значения по умолчанию
        return Settings()

    def save_settings(self, settings: Settings) -> bool:
        """Сохранить настройки приложения"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Проверяем, существуют ли настройки
            cursor.execute("SELECT id FROM settings WHERE id = 1")
            exists = cursor.fetchone() is not None

            if exists:
                cursor.execute("""
                    UPDATE settings 
                    SET budget_warning_threshold = ?, 
                        budget_alert_threshold = ?, 
                        budget_critical_threshold = ?, 
                        default_currency = ?, 
                        language = ?, 
                        theme = ?, 
                        auto_backup_enabled = ?, 
                        backup_interval_days = ?, 
                        reports_format = ?, 
                        updated_at = ?
                    WHERE id = ?
                """, (
                    settings.budget_warning_threshold,
                    settings.budget_alert_threshold,
                    settings.budget_critical_threshold,
                    settings.default_currency,
                    settings.language,
                    settings.theme,
                    int(settings.auto_backup_enabled),
                    settings.backup_interval_days,
                    settings.reports_format,
                    datetime.now().isoformat(),
                    settings.id
                ))
            else:
                cursor.execute("""
                    INSERT INTO settings 
                    (id, budget_warning_threshold, budget_alert_threshold, budget_critical_threshold, 
                     default_currency, language, theme, auto_backup_enabled, 
                     backup_interval_days, reports_format, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    settings.id,
                    settings.budget_warning_threshold,
                    settings.budget_alert_threshold,
                    settings.budget_critical_threshold,
                    settings.default_currency,
                    settings.language,
                    settings.theme,
                    int(settings.auto_backup_enabled),
                    settings.backup_interval_days,
                    settings.reports_format,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))

            conn.commit()
            return True

    def delete_order(self, order_id: int) -> Tuple[bool, str]:
        """Удалить заказ"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM orders WHERE id = ?
            """, (order_id,))
            conn.commit()
            return True, "Заказ удален"

    def get_orders_for_event(self, event_id: int) -> List[Order]:
        """Получить все заказы для мероприятия"""
        orders = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT o.*, e.name as event_name, e.event_date
                FROM orders o
                JOIN events e ON o.event_id = e.id
                WHERE o.event_id = ?
                ORDER BY o.order_date DESC
            """, (event_id,))

            rows = cursor.fetchall()
            for row in rows:
                event = Event(
                    id=event_id,
                    name=row['event_name'],
                    event_date=date.fromisoformat(row['event_date'])
                )

                order = Order(
                    id=row['id'],
                    order_number=row['order_number'],
                    event_id=event_id,
                    event=event,
                    order_date=datetime.fromisoformat(row['order_date']),
                    status=row['status'],
                    total_amount=Decimal(str(row['total_amount'])),
                    notes=row['notes'] or '',
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now()
                )

                # Загружаем позиции заказа
                cursor.execute("""
                    SELECT oi.*, n.name as nomenclature_name, s.name as supplier_name
                    FROM order_items oi
                    LEFT JOIN nomenclatures n ON oi.nomenclature_id = n.id
                    LEFT JOIN suppliers s ON oi.supplier_id = s.id
                    WHERE oi.order_id = ?
                """, (order.id,))

                items_rows = cursor.fetchall()
                for item_row in items_rows:
                    nomenclature = None
                    if item_row['nomenclature_id']:
                        nomenclature = Nomenclature(
                            id=item_row['nomenclature_id'],
                            name=item_row['nomenclature_name'] or ''
                        )

                    supplier = None
                    if item_row['supplier_id']:
                        supplier = Supplier(
                            id=item_row['supplier_id'],
                            name=item_row['supplier_name'] or ''
                        )

                    order_item = OrderItem(
                        id=item_row['id'],
                        order_id=order.id,
                        nomenclature_id=item_row['nomenclature_id'],
                        supplier_id=item_row['supplier_id'],
                        nomenclature=nomenclature,
                        supplier=supplier,
                        quantity=Decimal(str(item_row['quantity'])),
                        unit_price=Decimal(str(item_row['unit_price'])),
                        total_price=Decimal(str(item_row['total_price'])),
                        notes=item_row['notes'] or '',
                        delivery_date=date.fromisoformat(item_row['delivery_date']) if item_row[
                            'delivery_date'] else None,
                        delivery_time=time.fromisoformat(item_row['delivery_time']) if item_row[
                            'delivery_time'] else None
                    )
                    order.items.append(order_item)

                orders.append(order)

        return orders

    # ===== Работа с budget_controls =====

    def get_budget_for_event(self, event_id: int) -> List[BudgetControl]:
        """Получить контроль бюджета для мероприятия"""
        controls = []
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT bc.*, c.name as category_name
                FROM budget_controls bc
                LEFT JOIN cost_categories c ON bc.category_id = c.id
                WHERE bc.event_id = ?
            """, (event_id,))

            rows = cursor.fetchall()
            for row in rows:
                category = None
                if row['category_id']:
                    category = CostCategory(
                        id=row['category_id'],
                        name=row['category_name'] or ''
                    )

                controls.append(BudgetControl(
                    id=row['id'],
                    event_id=event_id,
                    category_id=row['category_id'],
                    category=category,
                    actual_amount=Decimal(str(row['actual_amount'])),
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now(),
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else datetime.now()
                ))

        return controls

    # ===== Отчеты =====

    def get_expense_report(self, event_id: int) -> List[ExpenseReportItem]:
        """Получить отчет по расходам для мероприятия"""
        report_items = []
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Получаем общий бюджет мероприятия
            cursor.execute("SELECT budget FROM events WHERE id = ?", (event_id,))
            event_row = cursor.fetchone()
            total_budget = Decimal(str(event_row['budget'])) if event_row else Decimal('0')

            # Получаем расходы по категориям
            cursor.execute("""
                SELECT 
                    c.id as category_id,
                    c.name as category_name,
                    COALESCE(SUM(oi.total_price), 0) as total_spent
                FROM cost_categories c
                LEFT JOIN nomenclatures n ON c.id = n.category_id
                LEFT JOIN order_items oi ON n.id = oi.nomenclature_id
                LEFT JOIN orders o ON oi.order_id = o.id
                WHERE o.event_id = ? OR o.event_id IS NULL
                GROUP BY c.id, c.name
                HAVING total_spent > 0
                ORDER BY total_spent DESC
            """, (event_id,))

            rows = cursor.fetchall()
            for row in rows:
                # В твоей структуре нет planned_amount, используем пропорциональное распределение
                # или можно добавить логику распределения бюджета
                actual_amount = Decimal(str(row['total_spent']))
                planned_amount = Decimal('0')  # Нет данных о запланированном бюджете по категориям

                report_items.append(ExpenseReportItem(
                    category_name=row['category_name'],
                    planned_amount=planned_amount,
                    actual_amount=actual_amount,
                    percentage=0.0  # Будет рассчитано в __post_init__
                ))

        return report_items

    # ===== Утилиты =====

    def populate_test_data(self):
        """Заполнить базу тестовыми данными согласно ТЗ"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 1. Добавляем 6 категорий затрат
            categories = [
                ("Продукты/готовые блюда", "Продукты и готовые блюда для мероприятий", "#FF6B6B"),
                ("Напитки", "Алкогольные и безалкогольные напитки", "#4ECDC4"),
                ("Оборудование", "Аренда оборудования", "#FFD166"),
                ("Персонал", "Обслуживающий персонал", "#06D6A0"),
                ("Транспорт", "Транспортные расходы", "#118AB2"),
                ("Прочие расходы", "Прочие расходы на мероприятие", "#9D4EDD")
            ]

            for name, description, color in categories:
                cursor.execute("""
                    INSERT OR IGNORE INTO cost_categories (name, description, color, is_active)
                    VALUES (?, ?, ?, 1)
                """, (name, description, color))

            # 2. Добавляем номенклатуру
            # Получаем ID категорий
            cursor.execute("SELECT id, name FROM cost_categories")
            category_map = {row['name']: row['id'] for row in cursor.fetchall()}

            # Номенклатура для продуктов (6 позиций)
            food_items = [
                ("Салат Цезарь", category_map["Продукты/готовые блюда"], "порц.", "Салат Цезарь с курицей"),
                ("Стейк из лосося", category_map["Продукты/готовые блюда"], "порц.", "Стейк из лосося на гриле"),
                ("Картофель по-деревенски", category_map["Продукты/готовые блюда"], "порц.", "Запеченный картофель"),
                ("Брускетта с томатами", category_map["Продукты/готовые блюда"], "шт.", "Итальянская закуска"),
                ("Фруктовая тарелка", category_map["Продукты/готовые блюда"], "порц.", "Сезонные фрукты"),
                ("Тирамису", category_map["Продукты/готовые блюда"], "порц.", "Итальянский десерт")
            ]

            for name, cat_id, unit, desc in food_items:
                cursor.execute("""
                    INSERT INTO nomenclatures (name, category_id, unit, description, is_active)
                    VALUES (?, ?, ?, ?, 1)
                """, (name, cat_id, unit, desc))

            # Напитки (4 позиции)
            drink_items = [
                ("Сок апельсиновый", category_map["Напитки"], "л", "Свежевыжатый апельсиновый сок"),
                ("Вода минеральная", category_map["Напитки"], "шт.", "Минеральная вода 0.5л"),
                ("Кофе латте", category_map["Напитки"], "чашка", "Кофе латте с молоком"),
                ("Чай черный", category_map["Напитки"], "чашка", "Черный чай")
            ]

            for name, cat_id, unit, desc in drink_items:
                cursor.execute("""
                    INSERT INTO nomenclatures (name, category_id, unit, description, is_active)
                    VALUES (?, ?, ?, ?, 1)
                """, (name, cat_id, unit, desc))

            # Персонал (1 позиция)
            cursor.execute("""
                INSERT INTO nomenclatures (name, category_id, unit, description, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, ("Заказ персонала", category_map["Персонал"], "час", "Обслуживающий персонал", 1))

            # Транспорт (1 позиция)
            cursor.execute("""
                INSERT INTO nomenclatures (name, category_id, unit, description, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, ("Заказ такси", category_map["Транспорт"], "поездка", "Транспортные услуги", 1))

            conn.commit()
            logger.info("Тестовые данные добавлены в базу")

        def delete_nomenclature(self, nomenclature_id: int) -> Tuple[bool, str]:
            """Удалить номенклатуру"""
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Проверяем, используется ли номенклатура в заказах
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM order_items
                    WHERE nomenclature_id = ?
                """, (nomenclature_id,))

                usage_count = cursor.fetchone()['count']
                if usage_count > 0:
                    return False, f"Номенклатура используется в {usage_count} позициях заказов, удаление невозможно"

                # Удаляем номенклатуру
                cursor.execute("""
                    DELETE FROM nomenclatures
                    WHERE id = ?
                """, (nomenclature_id,))

                conn.commit()

                if cursor.rowcount > 0:
                    return True, "Номенклатура успешно удалена"
                else:
                    return False, "Номенклатура не найдена"

        def update_nomenclature(self, nomenclature: Nomenclature) -> Tuple[bool, str]:
            """Обновить номенклатуру"""
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE nomenclatures
                    SET name = ?, category_id = ?, unit = ?, description = ?, is_active = ?
                    WHERE id = ?
                """, (
                    nomenclature.name,
                    nomenclature.category_id,
                    nomenclature.unit,
                    nomenclature.description,
                    1 if nomenclature.is_active else 0,
                    nomenclature.id
                ))
                conn.commit()

                if cursor.rowcount > 0:
                    return True, "Номенклатура успешно обновлена"
                else:
                    return False, "Номенклатура не найдена"

        def get_orders_using_nomenclature(self, nomenclature_id: int) -> List[Order]:
            """Получить заказы, в которых используется номенклатура"""
            orders = []
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT DISTINCT o.* 
                    FROM orders o
                    JOIN order_items oi ON o.id = oi.order_id
                    WHERE oi.nomenclature_id = ?
                """, (nomenclature_id,))

                rows = cursor.fetchall()
                for row in rows:
                    orders.append(Order(
                        id=row['id'],
                        order_number=row['order_number'],
                        event_id=row['event_id'],
                        order_date=datetime.fromisoformat(row['order_date']),
                        status=row['status'],
                        total_amount=Decimal(str(row['total_amount'])),
                        notes=row['notes'] or '',
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else datetime.now()
                    ))

            return orders
