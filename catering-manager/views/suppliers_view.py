"""
Управление поставщиками
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from typing import List, Optional

from models import Supplier, CostCategory
from controllers import CateringController
from utils.formatters import Formatters
from utils.validators import Validators
from .base_view import BasePage  # <--- ИСПРАВЛЕНО


class SuppliersPage(BasePage):
    """Страница управления поставщиками"""

    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Управление поставщиками")
        self.suppliers: List[Supplier] = []
        self.categories: List[CostCategory] = []
        self._create_widgets()
        self.refresh_data()

    def _create_widgets(self):
        """Создание виджетов страницы"""
        # Заголовок
        title_frame = ctk.CTkFrame(self)
        title_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            title_frame,
            text="🏢 Управление поставщиками",
            font=("Arial", 18, "bold")
        ).pack(side="left", padx=10)

        # Фильтры
        filter_frame = ctk.CTkFrame(self)
        filter_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(filter_frame, text="Фильтр по категории:", font=("Arial", 12)).pack(side="left", padx=10)

        self.category_filter = ctk.CTkComboBox(
            filter_frame,
            values=["Все категории"],
            width=200,
            command=self._apply_filter
        )
        self.category_filter.pack(side="left", padx=10)

        ctk.CTkLabel(filter_frame, text="Рейтинг от:", font=("Arial", 12)).pack(side="left", padx=(20, 5))

        self.rating_filter = ctk.CTkComboBox(
            filter_frame,
            values=["Любой", "1+", "2+", "3+", "4+", "5"],
            width=80
        )
        self.rating_filter.pack(side="left", padx=5)
        self.rating_filter.set("Любой")

        ctk.CTkButton(
            filter_frame,
            text="Применить фильтр",
            command=self._apply_filter,
            width=120
        ).pack(side="left", padx=10)

        # Кнопки управления
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkButton(
            button_frame,
            text="➕ Добавить поставщика",
            command=self._add_supplier,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="✏️ Редактировать",
            command=self._edit_supplier,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="📊 Цены",
            command=self._show_prices,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="🔄 Обновить",
            command=self.refresh_data,
            width=150
        ).pack(side="right", padx=5)

        # Таблица поставщиков
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Treeview
        tree_frame = ctk.CTkFrame(table_frame)
        tree_frame.pack(fill="both", expand=True)

        tree_scroll_y = ctk.CTkScrollbar(tree_frame)
        tree_scroll_y.pack(side="right", fill="y")

        tree_scroll_x = ctk.CTkScrollbar(tree_frame, orientation="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")

        self.tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            selectmode="browse"
        )

        tree_scroll_y.configure(command=self.tree.yview)
        tree_scroll_x.configure(command=self.tree.xview)

        # Колонки
        self.tree['columns'] = (
        'id', 'name', 'category', 'contact', 'phone', 'email', 'rating', 'created_at', 'is_active')
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('name', width=200, anchor=tk.W)
        self.tree.column('category', width=150, anchor=tk.W)
        self.tree.column('contact', width=150, anchor=tk.W)
        self.tree.column('phone', width=120, anchor=tk.W)
        self.tree.column('email', width=180, anchor=tk.W)
        self.tree.column('rating', width=80, anchor=tk.CENTER)
        self.tree.column('created_at', width=120, anchor=tk.W)
        self.tree.column('is_active', width=80, anchor=tk.CENTER)

        # Заголовки
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Название')
        self.tree.heading('category', text='Категория')
        self.tree.heading('contact', text='Контактное лицо')
        self.tree.heading('phone', text='Телефон')
        self.tree.heading('email', text='Email')
        self.tree.heading('rating', text='Рейтинг')
        self.tree.heading('created_at', text='Дата создания')
        self.tree.heading('is_active', text='Активен')

        self.tree.pack(fill="both", expand=True)

        # Привязка двойного клика
        self.tree.bind('<Double-Button-1>', lambda e: self._edit_supplier())

        # Статус
        self.status_label = ctk.CTkLabel(
            self,
            text="Загружено поставщиков: 0",
            font=("Arial", 10)
        )
        self.status_label.pack(side="bottom", fill="x", padx=10, pady=5)

    def refresh_data(self):
        """Обновить данные"""
        try:
            # Очищаем таблицу
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Загружаем данные
            self.suppliers = self.controller.get_all_suppliers()
            self.categories = self.controller.get_all_categories()

            # Обновляем фильтр категорий
            category_names = ["Все категории"] + [cat.name for cat in self.categories]
            self.category_filter.configure(values=category_names)
            self.category_filter.set("Все категории")

            # Заполняем таблицу
            for supplier in self.suppliers:
                category_name = ""
                if supplier.category:
                    category_name = supplier.category.name
                elif supplier.category_id:
                    for cat in self.categories:
                        if cat.id == supplier.category_id:
                            category_name = cat.name
                            break

                # Отображаем рейтинг звездами
                rating_str = "★" * int(supplier.rating) + "☆" * (5 - int(supplier.rating))

                self.tree.insert(
                    '',
                    tk.END,
                    values=(
                        supplier.id,
                        supplier.name,
                        category_name,
                        supplier.contact_person,
                        supplier.phone,
                        supplier.email,
                        rating_str,
                        Formatters.format_date(supplier.created_at),
                        "✓" if supplier.is_active else "✗"
                    ),
                    tags=('active' if supplier.is_active else 'inactive')
                )

            # Настраиваем цвета строк
            self.tree.tag_configure('active', foreground='black')
            self.tree.tag_configure('inactive', foreground='gray')

            # Обновляем статус
            self.status_label.configure(
                text=f"Загружено поставщиков: {len(self.suppliers)}"
            )

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить поставщиков: {str(e)}")

    def _apply_filter(self, event=None):
        """Применить фильтры"""
        category_filter = self.category_filter.get()
        rating_filter = self.rating_filter.get()

        min_rating = 0
        if rating_filter != "Любой":
            if rating_filter == "5":
                min_rating = 5
            else:
                min_rating = int(rating_filter[0])

        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            show_item = True

            # Фильтр по категории
            if category_filter != "Все категории" and values[2] != category_filter:
                show_item = False

            # Фильтр по рейтингу
            if min_rating > 0:
                rating = values[6].count('★')
                if rating < min_rating:
                    show_item = False

            # Показываем/скрываем строку
            if show_item:
                self.tree.item(item, tags=())
            else:
                self.tree.item(item, tags=('hidden',))

        self.tree.tag_configure('hidden', foreground='gray90')

    def _add_supplier(self):
        """Добавить нового поставщика"""
        if not self.categories:
            messagebox.showwarning("Внимание", "Сначала создайте категории затрат")
            return

        dialog = SupplierDialog(self, self.controller, None, self.categories)
        self.wait_window(dialog)
        if dialog.result:
            self.refresh_data()

    def _edit_supplier(self):
        """Редактировать выбранного поставщика"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите поставщика для редактирования")
            return

        # Получаем ID выбранного поставщика
        item = self.tree.item(selected[0])
        supplier_id = item['values'][0]

        # Находим поставщика
        supplier = None
        for sup in self.suppliers:
            if sup.id == supplier_id:
                supplier = sup
                break

        if supplier:
            dialog = SupplierDialog(self, self.controller, supplier, self.categories)
            self.wait_window(dialog)
            if dialog.result:
                self.refresh_data()

    def _show_prices(self):
        """Показать цены поставщика"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите поставщика для просмотра цен")
            return

        # Получаем ID выбранного поставщика
        item = self.tree.item(selected[0])
        supplier_id = item['values'][0]
        supplier_name = item['values'][1]

        messagebox.showinfo(
            "Цены поставщика",
            f"Цены поставщика '{supplier_name}'\n\n"
            "Функция просмотра цен находится в разработке."
        )

class SupplierDialog(ctk.CTkToplevel):
    """Диалог для добавления/редактирования поставщика"""

    def __init__(self, parent, controller, supplier: Optional[Supplier] = None, categories: List[CostCategory] = None):
        super().__init__(parent)

        self.controller = controller
        self.supplier = supplier
        self.categories = categories or []
        self.result = False

        # Настройка окна
        title = "Редактировать поставщика" if supplier else "Добавить поставщика"
        self.title(title)
        self.geometry("1000x600")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._fill_data()

    def _create_widgets(self):
        """Создание виджетов диалога"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Заголовок
        title = "Редактировать поставщика" if self.supplier else "Добавить поставщика"
        ctk.CTkLabel(
            main_frame,
            text=title,
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 20))

        # Форма в две колонки
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="x", pady=10)

        # Левая колонка
        left_frame = ctk.CTkFrame(form_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Правая колонка
        right_frame = ctk.CTkFrame(form_frame)
        right_frame.pack(side="right", fill="both", expand=True)

        # Основная информация (левая колонка)
        ctk.CTkLabel(left_frame, text="Основная информация", font=("Arial", 14, "bold")).pack(anchor="w", pady=(0, 10))

        # Название
        ctk.CTkLabel(left_frame, text="Название *:", font=("Arial", 12)).pack(anchor="w", pady=(5, 0))
        self.name_entry = ctk.CTkEntry(left_frame, font=("Arial", 12))
        self.name_entry.pack(fill="x", pady=(0, 10))

        # Категория
        ctk.CTkLabel(left_frame, text="Категория *:", font=("Arial", 12)).pack(anchor="w", pady=(5, 0))

        category_names = [cat.name for cat in self.categories]
        self.category_combo = ctk.CTkComboBox(
            left_frame,
            values=category_names,
            font=("Arial", 12)
        )
        self.category_combo.pack(fill="x", pady=(0, 10))

        # Контактное лицо
        ctk.CTkLabel(left_frame, text="Контактное лицо:", font=("Arial", 12)).pack(anchor="w", pady=(5, 0))
        self.contact_entry = ctk.CTkEntry(left_frame, font=("Arial", 12))
        self.contact_entry.pack(fill="x", pady=(0, 10))

        # Рейтинг
        ctk.CTkLabel(left_frame, text="Рейтинг (1-5):", font=("Arial", 12)).pack(anchor="w", pady=(5, 0))

        rating_frame = ctk.CTkFrame(left_frame)
        rating_frame.pack(fill="x", pady=(0, 10))

        self.rating_var = tk.IntVar(value=0)
        for i in range(1, 6):
            ctk.CTkRadioButton(
                rating_frame,
                text=f"{i}★",
                variable=self.rating_var,
                value=i,
                font=("Arial", 12)
            ).pack(side="left", padx=5)

        # Контактная информация (правая колонка)
        ctk.CTkLabel(right_frame, text="Контактная информация", font=("Arial", 14, "bold")).pack(anchor="w",
                                                                                                 pady=(0, 10))

        # Телефон
        ctk.CTkLabel(right_frame, text="Телефон:", font=("Arial", 12)).pack(anchor="w", pady=(5, 0))
        self.phone_entry = ctk.CTkEntry(right_frame, font=("Arial", 12))
        self.phone_entry.pack(fill="x", pady=(0, 10))

        # Email
        ctk.CTkLabel(right_frame, text="Email:", font=("Arial", 12)).pack(anchor="w", pady=(5, 0))
        self.email_entry = ctk.CTkEntry(right_frame, font=("Arial", 12))
        self.email_entry.pack(fill="x", pady=(0, 10))

        # Адрес
        ctk.CTkLabel(right_frame, text="Адрес:", font=("Arial", 12)).pack(anchor="w", pady=(5, 0))
        self.address_entry = ctk.CTkTextbox(right_frame, height=60, font=("Arial", 12))
        self.address_entry.pack(fill="x", pady=(0, 10))

        # ИНН
        ctk.CTkLabel(right_frame, text="ИНН:", font=("Arial", 12)).pack(anchor="w", pady=(5, 0))
        self.inn_entry = ctk.CTkEntry(right_frame, font=("Arial", 12))
        self.inn_entry.pack(fill="x", pady=(0, 10))

        # Активность
        self.active_var = tk.BooleanVar(value=True)
        self.active_check = ctk.CTkCheckBox(
            right_frame,
            text="Активный поставщик",
            variable=self.active_var,
            font=("Arial", 12)
        )
        self.active_check.pack(anchor="w", pady=10)

        # Кнопки
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=20)

        ctk.CTkButton(
            button_frame,
            text="Отмена",
            command=self._cancel,
            width=100,
            fg_color="gray",
            hover_color="darkgray"
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="Сохранить",
            command=self._save,
            width=100
        ).pack(side="right", padx=10)

    def _fill_data(self):
        """Заполнить поля данными"""
        if self.supplier:
            self.name_entry.insert(0, self.supplier.name)
            self.contact_entry.insert(0, self.supplier.contact_person)
            self.phone_entry.insert(0, self.supplier.phone)
            self.email_entry.insert(0, self.supplier.email)
            self.address_entry.insert("1.0", self.supplier.address)
            self.inn_entry.insert(0, self.supplier.inn)
            self.rating_var.set(int(self.supplier.rating))
            self.active_var.set(self.supplier.is_active)

            # Устанавливаем категорию
            if self.supplier.category:
                self.category_combo.set(self.supplier.category.name)
            elif self.supplier.category_id:
                for cat in self.categories:
                    if cat.id == self.supplier.category_id:
                        self.category_combo.set(cat.name)
                        break

    def _save(self):
        """Сохранить поставщика"""
        name = self.name_entry.get().strip()
        category_name = self.category_combo.get()
        contact_person = self.contact_entry.get().strip()
        phone = self.phone_entry.get().strip()
        email = self.email_entry.get().strip()
        address = self.address_entry.get("1.0", "end").strip()
        inn = self.inn_entry.get().strip()
        rating = self.rating_var.get()
        is_active = self.active_var.get()

        if not name:
            messagebox.showwarning("Внимание", "Введите название поставщика")
            return

        if not category_name:
            messagebox.showwarning("Внимание", "Выберите категорию поставщика")
            return

        # Валидация email
        if email and not Validators.validate_email(email):
            messagebox.showwarning("Внимание", "Неверный формат email")
            return

        # Валидация ИНН
        if inn and not Validators.validate_inn(inn):
            messagebox.showwarning("Внимание", "Неверный формат ИНН")
            return

        # Находим ID категории
        category_id = None
        for cat in self.categories:
            if cat.name == category_name:
                category_id = cat.id
                break

        if not category_id:
            messagebox.showerror("Ошибка", "Не найдена выбранная категория")
            return

        if self.supplier:
            # Редактирование существующего поставщика
            self.supplier.name = name
            self.supplier.category_id = category_id
            self.supplier.contact_person = contact_person
            self.supplier.phone = phone
            self.supplier.email = email
            self.supplier.address = address
            self.supplier.inn = inn
            self.supplier.rating = rating
            self.supplier.is_active = is_active

            messagebox.showinfo("Редактирование", "Функция редактирования находится в разработке")
        else:
            # Добавление нового поставщика
            success, message = self.controller.add_supplier(
                name=name,
                category_id=category_id,
                contact_person=contact_person,
                phone=phone,
                email=email,
                address=address,
                inn=inn,
                rating=rating
            )

            if success:
                self.result = True
                self.destroy()
            else:
                messagebox.showerror("Ошибка", message)

    def _cancel(self):
        """Отмена"""
        self.destroy()
