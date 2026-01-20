"""
Тесты для контроллеров
"""

import unittest
from datetime import datetime, date, time
from decimal import Decimal
from unittest.mock import Mock, patch

from controllers import CateringController
from models import *


class TestCateringController(unittest.TestCase):
    """Тесты для контроллера"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        # Создаем mock для DatabaseManager
        self.mock_db = Mock()
        self.controller = CateringController(self.mock_db)

    def test_add_category(self):
        """Тест добавления категории"""
        # Успешное добавление
        self.mock_db.get_category_by_name.return_value = None
        self.mock_db.add_category.return_value = 1

        success, message = self.controller.add_category("Новая категория", "Описание")

        self.assertTrue(success)
        self.assertIn("успешно добавлена", message)

        # Категория уже существует
        existing_category = CostCategory(id=1, name="Новая категория")
        self.mock_db.get_category_by_name.return_value = existing_category

        success, message = self.controller.add_category("Новая категория")

        self.assertFalse(success)
        self.assertIn("уже существует", message)

        # Пустое название
        success, message = self.controller.add_category("")

        self.assertFalse(success)
        self.assertIn("не может быть пустым", message)

    def test_get_budget_status(self):
        """Тест получения статуса бюджета"""
        # Без текущего мероприятия
        status = self.controller.get_budget_status()
        self.assertEqual(status, {})

        # С мероприятием
        event = Event(
            id=1,
            name="Тестовое мероприятие",
            budget=Decimal('100000')
        )
        self.controller.current_event = event

        # Мок для заказов
        order = Mock()
        order.total_amount = Decimal('30000')
        self.mock_db.get_orders_for_event.return_value = [order]

        status = self.controller.get_budget_status()

        self.assertEqual(status['budget'], Decimal('100000'))
        self.assertEqual(status['spent'], Decimal('30000'))
        self.assertEqual(status['remaining'], Decimal('70000'))
        self.assertEqual(status['percentage'], 30.0)
        self.assertEqual(status['status'], "green")

    def test_get_budget_status_color(self):
        """Тест определения цвета статуса бюджета"""
        # Менее 80% - зеленый
        self.assertEqual(self.controller._get_budget_status_color(0.5), "green")
        self.assertEqual(self.controller._get_budget_status_color(0.79), "green")

        # 80-90% - желтый
        self.assertEqual(self.controller._get_budget_status_color(0.8), "yellow")
        self.assertEqual(self.controller._get_budget_status_color(0.89), "yellow")

        # 90-100% - оранжевый
        self.assertEqual(self.controller._get_budget_status_color(0.9), "orange")
        self.assertEqual(self.controller._get_budget_status_color(0.99), "orange")

        # 100% и более - красный
        self.assertEqual(self.controller._get_budget_status_color(1.0), "red")
        self.assertEqual(self.controller._get_budget_status_color(1.1), "red")

    @patch('controllers.Validators')
    def test_check_order_deadline(self, mock_validators):
        """Тест проверки дедлайна заказа"""
        # Настройка моков
        mock_validators.check_order_deadline.return_value = True

        event_date = date(2024, 12, 31)
        order_date = datetime(2024, 12, 30, 10, 0)  # За сутки до

        result = mock_validators.check_order_deadline(event_date, order_date)

        self.assertTrue(result)
        mock_validators.check_order_deadline.assert_called_once_with(event_date, order_date)

    def test_add_item_to_order(self):
        """Тест добавления позиции в заказ"""
        # Создаем тестовые данные
        event = Event(id=1, name="Тест", budget=Decimal('1000'))
        self.controller.current_event = event
        self.controller.current_order = Order(id=1, event=event)

        # Мок для номенклатуры
        nomenclature = Nomenclature(id=1, name="Товар")
        self.mock_db.get_nomenclature_by_id.return_value = nomenclature

        # Мок для цен
        price = Mock()
        price.price = Decimal('100')
        self.mock_db.get_prices_for_nomenclature.return_value = [price]

        # Добавляем позицию
        success, message = self.controller.add_item_to_order(
            nomenclature_id=1,
            supplier_id=1,
            quantity=Decimal('5')
        )

        self.assertTrue(success)
        self.assertEqual(len(self.controller.current_order.items), 1)

        # Проверяем превышение бюджета
        success, message = self.controller.add_item_to_order(
            nomenclature_id=1,
            supplier_id=1,
            quantity=Decimal('20')  # 20 * 100 = 2000, что больше бюджета 1000
        )

        self.assertFalse(success)
        self.assertIn("Превышение бюджета", message)


if __name__ == '__main__':
    unittest.main()
