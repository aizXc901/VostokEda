"""
Создание и просмотр заказов
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional

from models import Order, OrderItem, Nomenclature, Supplier
from controllers import CateringController
from utils.formatters import Formatters
from utils.validators import Validators
from .base_view import BasePage  # <--- ИСПРАВЛЕНО


class OrdersPage(BasePage):
    """Страница создания заказов (используется в отдельном окне)"""

    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Создание заказа")
        self.order: Optional[Order] = None
        self.nomenclatures: List[Nomenclature] = []
        self.suppliers: List[Supplier] = []
        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов страницы"""
        if not self.controller.current_event:
            ctk.CTkLabel(
                self,
                text="⚠️ Сначала выберите мероприятие на странице 'Мероприятия'",
                font=("Arial", 14),
                text_color="orange"
            ).pack(pady=50)
            return

        # Заголовок с информацией о мероприятии
        title_frame = ctk.CTkFrame(self)
        title_frame.pack(fill="x", padx=10, pady=10)

        event = self.controller.current_event
        title_text = f"📦 Создание заказа для: {event.name} ({Formatters.format_date(event.event_date)})"
        ctk.CTkLabel(
            title_frame,
            text=title_text,
            font=("Arial", 16, "bold")
        ).pack(side="left", padx=10)

        # Бюджетная информация
        budget_frame = ctk.CTkFrame(self)
        budget_frame.pack(fill="x", padx=10, pady=(0, 10))

        budget_status = self.controller.get_budget_status()

        budget_text = (
            f"Бюджет: {Formatters.format_currency(budget_status['budget'])} | "
            f"Потрачено: {Formatters.format_currency(budget_status['spent'])} | "
            f"Осталось: {Formatters.format_currency(budget_status['remaining'])} | "
            f"Использовано: {Formatters.format_percentage(budget_status['percentage'])}"
        )

        self.budget_label = ctk.CTkLabel(
            budget_frame,
            text=budget_text,
            font=("Arial", 12)
        )
        self.budget_label.pack(padx=10, pady=5)

        # Прогресс-бар бюджета
        self.budget_progress = ctk.CTkProgressBar(budget_frame)
        self.budget_progress.pack(fill="x", padx=10, pady=(0, 5))
        self.budget_progress.set(min(budget_status['percentage'] / 100, 1.0))

        # Цвет прогресс-бара
        usage = budget_status['percentage'] / 100
        if usage < 0.8:
            self.budget_progress.configure(progress_color="green")
        elif usage < 0.9:
            self.budget_progress.configure(progress_color="yellow")
        elif usage < 1.0:
            self.budget_progress.configure(progress_color="orange")
        else:
            self.budget_progress.configure(progress_color="red")

        # Основной фрейм с двумя колонками
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Левая колонка - добавление позиций
        left_frame = ctk.CTkFrame(main_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ctk.CTkLabel(
            left_frame,
            text="Добавить позицию в заказ",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=(0, 10))

        # Форма добавления позиции
        form_frame = ctk.CTkFrame(left_frame)
        form_frame.pack(fill="x", padx=10, pady=10)

        # Номенклатура
        ctk.CTkLabel(form_frame, text="Позиция:", font=("Arial", 12)).pack(anchor="w", pady=(5, 0))

        self.nomenclature_combo = ctk.CTkComboBox(
            form_frame,
            values=[],
            font=("Arial", 12),
            command=self._on_nomenclature_select
        )
        self.nomenclature_combo.pack(fill="x", pady=(0, 10))

        # Поставщик
        ctk.CTkLabel(form_frame, text="Поставщик:", font=("Arial", 12)).pack(anchor="w", pady=(5, 0))

        self.supplier_combo = ctk.CTkComboBox(
            form_frame,
            values=[],
            font=("Arial", 12),
            command=self._on_supplier_select
        )
        self.supplier_combo.pack(fill="x", pady=(0, 10))

        # Количество и цена
        qty_price_frame = ctk.CTkFrame(form_frame)
        qty_price_frame.pack(fill="x", pady=(0, 10))

        # Количество
        ctk.CTkLabel(qty_price_frame, text="Количество:", font=("Arial", 12)).pack(side="left", padx=(0, 10))
        self.quantity_entry = ctk.CTkEntry(qty_price_frame, font=("Arial", 12), width=100)
        self.quantity_entry.pack(side="left", padx=(0, 20))
        self.quantity_entry.insert(0, "1")

        # Цена
        ctk.CTkLabel(qty_price_frame, text="Цена:", font=("Arial", 12)).pack(side="left", padx=(0, 10))
        self.price_entry = ctk.CTkEntry(qty_price_frame, font=("Arial", 12), width=100)
        self.price_entry.pack(side="left")

        # Кнопка добавления
        add_button = ctk.CTkButton(
            form_frame,
            text="➕ Добавить в заказ",
            command=self._add_item_to_order,
            height=40,
            font=("Arial", 12, "bold")
        )
        add_button.pack(fill="x", pady=10)

        # Правая колонка - текущий заказ
        right_frame = ctk.CTkFrame(main_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        ctk.CTkLabel(
            right_frame,
            text="Текущий заказ",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=(0, 10))

        # Таблица позиций заказа
        table_frame = ctk.CTkFrame(right_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Treeview для позиций заказа
        tree_frame = ctk.CTkFrame(table_frame)
        tree_frame.pack(fill="both", expand=True)

        tree_scroll_y = ctk.CTkScrollbar(tree_frame)
        tree_scroll_y.pack(side="right", fill="y")

        self.order_tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=tree_scroll_y.set,
            selectmode="browse",
            height=10
        )

        tree_scroll_y.configure(command=self.order_tree.yview)

        # Колонки
        self.order_tree['columns'] = ('item', 'supplier', 'quantity', 'price', 'total')
        self.order_tree.column('#0', width=0, stretch=tk.NO)
        self.order_tree.column('item', width=150, anchor=tk.W)
        self.order_tree.column('supplier', width=120, anchor=tk.W)
        self.order_tree.column('quantity', width=80, anchor=tk.CENTER)
        self.order_tree.column('price', width=80, anchor=tk.E)
        self.order_tree.column('total', width=100, anchor=tk.E)

        # Заголовки
        self.order_tree.heading('item', text='Позиция')
        self.order_tree.heading('supplier', text='Поставщик')
        self.order_tree.heading('quantity', text='Кол-во')
        self.order_tree.heading('price', text='Цена')
        self.order_tree.heading('total', text='Сумма')

        self.order_tree.pack(fill="both", expand=True)

        # Итоговая сумма
        total_frame = ctk.CTkFrame(right_frame)
        total_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.total_label = ctk.CTkLabel(
            total_frame,
            text="Итого: 0 ₽",
            font=("Arial", 14, "bold")
        )
        self.total_label.pack(side="right", padx=10)

        # Кнопки управления заказом
        button_frame = ctk.CTkFrame(right_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            button_frame,
            text="🗑️ Удалить позицию",
            command=self._remove_item,
            width=120,
            fg_color="#FF6B6B",
            hover_color="#FF4757"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="💾 Сохранить заказ",
            command=self._save_order,
            width=120
        ).pack(side="right", padx=5)

        # Примечания
        notes_frame = ctk.CTkFrame(self)
        notes_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(notes_frame, text="Примечания к заказу:", font=("Arial", 12)).pack(anchor="w", padx=10,
                                                                                        pady=(5, 0))
        self.notes_entry = ctk.CTkTextbox(notes_frame, height=60, font=("Arial", 12))
        self.notes_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Загружаем данные
        self._load_data()

    def _load_data(self):
        """Загрузить данные для формы"""
        try:
            self.nomenclatures = self.controller.get_all_nomenclatures()
            self.suppliers = self.controller.get_all_suppliers()

            # Заполняем комбобоксы
            nomenclature_names = [f"{n.name} ({n.unit})" for n in self.nomenclatures if n.is_active]
            self.nomenclature_combo.configure(values=nomenclature_names)

            supplier_names = [s.name for s in self.suppliers if s.is_active]
            self.supplier_combo.configure(values=supplier_names)

            # Создаем новый заказ
            self.order = self.controller.create_new_order()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")

    def _on_nomenclature_select(self, choice):
        """Обработка выбора номенклатуры"""
        if not choice:
            return

        # Находим выбранную номенклатуру
        for nom in self.nomenclatures:
            display_name = f"{nom.name} ({nom.unit})"
            if display_name == choice:
                # Можно здесь подгрузить цену по умолчанию
                break

    def _on_supplier_select(self, choice):
        """Обработка выбора поставщика"""
        if not choice:
            return

        # Здесь можно подгрузить цены выбранного поставщика
        pass

    def _add_item_to_order(self):
        """Добавить позицию в заказ"""
        if not self.order:
            return

        # Получаем данные из формы
        nomenclature_display = self.nomenclature_combo.get()
        supplier_name = self.supplier_combo.get()
        quantity_str = self.quantity_entry.get().strip()
        price_str = self.price_entry.get().strip()

        # Валидация
        if not nomenclature_display:
            messagebox.showwarning("Внимание", "Выберите позицию")
            return

        if not supplier_name:
            messagebox.showwarning("Внимание", "Выберите поставщика")
            return

        # Находим номенклатуру
        selected_nomenclature = None
        nomenclature_id = None
        for nom in self.nomenclatures:
            display_name = f"{nom.name} ({nom.unit})"
            if display_name == nomenclature_display:
                selected_nomenclature = nom
                nomenclature_id = nom.id
                break

        if not selected_nomenclature:
            messagebox.showerror("Ошибка", "Не найдена выбранная позиция")
            return

        # Находим поставщика
        selected_supplier = None
        supplier_id = None
        for sup in self.suppliers:
            if sup.name == supplier_name:
                selected_supplier = sup
                supplier_id = sup.id
                break

        if not selected_supplier:
            messagebox.showerror("Ошибка", "Не найден выбранный поставщик")
            return

        # Валидация количества
        quantity = Validators.validate_decimal(quantity_str)
        if quantity is None or quantity <= Decimal('0'):
            messagebox.showwarning("Внимание", "Введите корректное количество")
            return

        # Валидация цены
        price = Validators.validate_decimal(price_str)
        if price is None or price <= Decimal('0'):
            messagebox.showwarning("Внимание", "Введите корректную цену")
            return

        # Добавляем позицию в заказ через контроллер
        success, message = self.controller.add_item_to_order(
            nomenclature_id=nomenclature_id,
            supplier_id=supplier_id,
            quantity=quantity,
            unit_price=price
        )

        if success:
            # Добавляем позицию в таблицу
            total = quantity * price
            self.order_tree.insert(
                '',
                tk.END,
                values=(
                    selected_nomenclature.name,
                    selected_supplier.name,
                    Formatters.format_quantity(quantity, selected_nomenclature.unit),
                    Formatters.format_currency(price, show_symbol=False),
                    Formatters.format_currency(total, show_symbol=False)
                )
            )

            # Обновляем итоговую сумму
            self._update_total()

            # Очищаем поля
            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, "1")
            self.price_entry.delete(0, tk.END)

            # Показываем предупреждение если есть
            if "Внимание" in message:
                messagebox.showwarning("Внимание", message)

        else:
            messagebox.showerror("Ошибка", message)

    def _remove_item(self):
        """Удалить выбранную позицию из заказа"""
        selected = self.order_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите позицию для удаления")
            return

        # Получаем индекс выбранной позиции
        item_index = self.order_tree.index(selected[0])

        # Удаляем из заказа
        if item_index < len(self.order.items):
            self.order.remove_item(item_index)

        # Удаляем из таблицы
        self.order_tree.delete(selected[0])

        # Обновляем итоговую сумму
        self._update_total()

    def _update_total(self):
        """Обновить отображение итоговой суммы"""
        if self.order:
            total = self.order.total_amount
            self.total_label.configure(text=f"Итого: {Formatters.format_currency(total)}")

            # Обновляем прогресс-бар бюджета
            budget_status = self.controller.get_budget_status()
            new_spent = budget_status['spent'] + total
            new_percentage = (new_spent / budget_status['budget']) * 100 if budget_status['budget'] > 0 else 0

            self.budget_progress.set(min(new_percentage / 100, 1.0))

            # Цвет прогресс-бара
            if new_percentage < 80:
                self.budget_progress.configure(progress_color="green")
            elif new_percentage < 90:
                self.budget_progress.configure(progress_color="yellow")
            elif new_percentage < 100:
                self.budget_progress.configure(progress_color="orange")
            else:
                self.budget_progress.configure(progress_color="red")

    def _save_order(self):
        """Сохранить заказ"""
        if not self.order or not self.order.items:
            messagebox.showwarning("Внимание", "Заказ пуст")
            return

        # Получаем примечания
        notes = self.notes_entry.get("1.0", "end").strip()

        # Сохраняем заказ через контроллер
        success, message = self.controller.save_current_order(notes)

        if success:
            messagebox.showinfo("Успех", message)

            # Очищаем форму
            self.order_tree.delete(*self.order_tree.get_children())
            self.notes_entry.delete("1.0", tk.END)
            self.total_label.configure(text="Итого: 0 ₽")
            self.budget_progress.set(0)

            # Создаем новый пустой заказ
            self.order = self.controller.create_new_order()

            # Обновляем бюджет
            budget_status = self.controller.get_budget_status()
            self.budget_label.configure(
                text=(
                    f"Бюджет: {Formatters.format_currency(budget_status['budget'])} | "
                    f"Потрачено: {Formatters.format_currency(budget_status['spent'])} | "
                    f"Осталось: {Formatters.format_currency(budget_status['remaining'])} | "
                    f"Использовано: {Formatters.format_percentage(budget_status['percentage'])}"
                )
            )

        else:
            messagebox.showerror("Ошибка", message)
