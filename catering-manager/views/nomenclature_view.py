"""
Управление номенклатурой
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from typing import List, Optional

from models import Nomenclature, CostCategory
from controllers import CateringController
from utils.formatters import Formatters
from .base_view import BasePage  # <--- ИСПРАВЛЕНО


class NomenclaturePage(BasePage):
    """Страница управления номенклатурой"""

    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Управление номенклатурой")
        self.nomenclatures: List[Nomenclature] = []
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
            text="🍽️ Управление номенклатурой",
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

        # Кнопки управления
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkButton(
            button_frame,
            text="➕ Добавить позицию",
            command=self._add_nomenclature,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="✏️ Редактировать",
            command=self._edit_nomenclature,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="🔄 Обновить",
            command=self.refresh_data,
            width=150
        ).pack(side="right", padx=5)

        # Таблица номенклатуры
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Создаем Treeview
        tree_frame = ctk.CTkFrame(table_frame)
        tree_frame.pack(fill="both", expand=True)

        # Прокрутки
        tree_scroll_y = ctk.CTkScrollbar(tree_frame)
        tree_scroll_y.pack(side="right", fill="y")

        tree_scroll_x = ctk.CTkScrollbar(tree_frame, orientation="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")

        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            selectmode="browse"
        )

        tree_scroll_y.configure(command=self.tree.yview)
        tree_scroll_x.configure(command=self.tree.xview)

        # Колонки
        self.tree['columns'] = ('id', 'name', 'category', 'unit', 'description', 'created_at', 'is_active')
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('name', width=200, anchor=tk.W)
        self.tree.column('category', width=150, anchor=tk.W)
        self.tree.column('unit', width=80, anchor=tk.CENTER)
        self.tree.column('description', width=300, anchor=tk.W)
        self.tree.column('created_at', width=120, anchor=tk.W)
        self.tree.column('is_active', width=80, anchor=tk.CENTER)

        # Заголовки
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Название')
        self.tree.heading('category', text='Категория')
        self.tree.heading('unit', text='Ед.изм.')
        self.tree.heading('description', text='Описание')
        self.tree.heading('created_at', text='Дата создания')
        self.tree.heading('is_active', text='Активна')

        self.tree.pack(fill="both", expand=True)

        # Привязка двойного клика
        self.tree.bind('<Double-Button-1>', lambda e: self._edit_nomenclature())

        # Статус
        self.status_label = ctk.CTkLabel(
            self,
            text="Загружено позиций: 0",
            font=("Arial", 10)
        )
        self.status_label.pack(side="bottom", fill="x", padx=10, pady=5)

    def _apply_filter(self):
        """Применить фильтр к таблице номенклатуры"""
        search_text = self.search_entry.text().strip().lower()

        for row in range(self.table.rowCount()):
            match = False
            # Проверяем все видимые столбцы
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break

            # Показываем/скрываем строку
            self.table.setRowHidden(row, not match)

    def _add_nomenclature(self):
        """Добавить новую номенклатуру (заглушка)"""
        print("Добавление номенклатуры...")
        # TODO: Реализовать добавление номенклатуры
        messagebox.showinfo("Информация", "Функция добавления номенклатуры будет реализована позже")

    def _edit_nomenclature(self):
        """Редактировать номенклатуру (заглушка)"""
        print("Редактирование номенклатуры...")
        # TODO: Реализовать редактирование

    def _delete_nomenclature(self):
        """Удалить номенклатуру (заглушка)"""
        print("Удаление номенклатуры...")
        # TODO: Реализовать удаление

    def refresh_data(self):
        """Обновить данные"""
