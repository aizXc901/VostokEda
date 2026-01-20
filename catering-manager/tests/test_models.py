"""
Тесты для моделей данных
"""

import unittest
from datetime import datetime, date, time
from decimal import Decimal

from models import *


class TestModels(unittest.TestCase):
    """Тесты для моделей данных"""

    def test_cost_category(self):
        """Тест категории затрат"""
        category = CostCategory(
            id=1,
            name="Продукты",
            description="Продукты питания",
            color="#FF0000"
        )

        self.assertEqual(category.id, 1)
        self.assertEqual(category.name, "Продукты")
        self.assertEqual(category.description, "Продукты питания")
        self.assertEqual(category.color, "#FF0000")
        self.assertTrue(category.is_active)

    def test_nomenclature(self):
        """Тест номенклатуры"""
        category = CostCategory(id=1, name="Продукты")
        nomenclature = Nomenclature(
            id=1,
            name="Салат Цезарь",
            category=category,
            unit="порц.",
            description="Салат с курицей"
        )

        self.assertEqual(nomenclature.id, 1)
        self.assertEqual(nomenclature.name, "Салат Цезарь")
        self.assertEqual(nomenclature.category, category)
        self.assertEqual(nomenclature.unit, "порц.")
        self.assertEqual(nomenclature.description, "Салат с курицей")

    def test_supplier(self):
        """Тест поставщика"""
        category = CostCategory(id=1, name="Продукты")
        supplier = Supplier(
            id=1,
            name="Ресторан 'Вкусно'",
            category=category,
            contact_person="Иван Иванов",
            phone="+79991234567",
            email="info@vkusno.ru"
        )

        self.assertEqual(supplier.id, 1)
        self.assertEqual(supplier.name, "Ресторан 'Вкусно'")
        self.assertEqual(supplier.category, category)
        self.assertEqual(supplier.contact_person, "Иван Иванов")
        self.assertEqual(supplier.phone, "+79991234567")
        self.assertEqual(supplier.email, "info@vkusno.ru")
        self.assertEqual(supplier.rating, 0.0)

    def test_supplier_price(self):
        """Тест цены поставщика"""
        supplier = Supplier(id=1, name="Поставщик")
        nomenclature = Nomenclature(id=1, name="Товар")

        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)

        price = SupplierPrice(
            id=1,
            supplier=supplier,
            nomenclature=nomenclature,
            price=Decimal('100.50'),
            start_date=start_date,
            end_date=end_date
        )

        self.assertEqual(price.id, 1)
        self.assertEqual(price.supplier, supplier)
        self.assertEqual(price.nomenclature, nomenclature)
        self.assertEqual(price.price, Decimal('100.50'))
        self.assertEqual(price.start_date, start_date)
        self.assertEqual(price.end_date, end_date)

        # Тест проверки активности цены
        test_date = date(2024, 6, 15)
        self.assertTrue(price.is_active(test_date))

        # Дата до начала действия
        test_date = date(2023, 12, 31)
        self.assertFalse(price.is_active(test_date))

        # Дата после окончания
        test_date = date(2025, 1, 1)
        self.assertFalse(price.is_active(test_date))

    def test_event(self):
        """Тест мероприятия"""
        event_date = date(2024, 12, 31)
        start_time = time(18, 0)

        event = Event(
            id=1,
            name="Новый год",
            event_date=event_date,
            start_time=start_time,
            guests_count=100,
            budget=Decimal('500000')
        )

        self.assertEqual(event.id, 1)
        self.assertEqual(event.name, "Новый год")
        self.assertEqual(event.event_date, event_date)
        self.assertEqual(event.start_time, start_time)
        self.assertEqual(event.guests_count, 100)
        self.assertEqual(event.budget, Decimal('500000'))
        self.assertEqual(event.status, "планируется")

    def test_order_item(self):
        """Тест позиции заказа"""
        nomenclature = Nomenclature(id=1, name="Товар")
        supplier = Supplier(id=1, name="Поставщик")

        item = OrderItem(
            nomenclature=nomenclature,
            supplier=supplier,
            quantity=Decimal('10'),
            unit_price=Decimal('100.50')
        )

        item.calculate_total()

        self.assertEqual(item.nomenclature, nomenclature)
        self.assertEqual(item.supplier, supplier)
        self.assertEqual(item.quantity, Decimal('10'))
        self.assertEqual(item.unit_price, Decimal('100.50'))
        self.assertEqual(item.total_price, Decimal('1005.00'))

    def test_order(self):
        """Тест заказа"""
        event = Event(id=1, name="Мероприятие")

        order = Order(
            id=1,
            order_number="ORD-20240101-001",
            event=event
        )

        self.assertEqual(order.id, 1)
        self.assertEqual(order.event, event)
        self.assertEqual(order.status, "черновик")
        self.assertEqual(order.total_amount, Decimal('0.00'))

        # Проверка автоматической генерации номера заказа
        order2 = Order(id=2, event_id=1)
        self.assertTrue(order2.order_number.startswith("ORD-"))

    def test_budget_control(self):
        """Тест контроля бюджета"""
        event = Event(id=1, name="Мероприятие")
        category = CostCategory(id=1, name="Продукты")

        control = BudgetControl(
            event=event,
            category=category,
            planned_amount=Decimal('100000'),
            actual_amount=Decimal('120000')
        )

        self.assertEqual(control.event, event)
        self.assertEqual(control.category, category)
        self.assertEqual(control.planned_amount, Decimal('100000'))
        self.assertEqual(control.actual_amount, Decimal('120000'))
        self.assertEqual(control.difference, Decimal('20000'))
        self.assertEqual(control.percentage, 120.0)


if __name__ == '__main__':
    unittest.main()
