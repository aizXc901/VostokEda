"""
Управление категориями затрат
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from typing import List, Optional

from models import CostCategory
from controllers import CateringController
from utils.formatters import Formatters
from .base_view import BasePage  # <--- ИСПРАВЛЕНО


class CategoriesPage(BasePage):
    """Страница управления категориями затрат"""

    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Управление категориями")
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
            text="📂 Управление категориями затрат",
            font=("Arial", 18, "bold")
        ).pack(side="left", padx=10)

        # Кнопки управления
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkButton(
            button_frame,
            text="➕ Добавить категорию",
            command=self._add_category,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="✏️ Редактировать",
            command=self._edit_category,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="🗑️ Удалить",
            command=self._delete_category,
            width=150,
            fg_color="#FF6B6B",
            hover_color="#FF4757"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="🔄 Обновить",
            command=self.refresh_data,
            width=150
        ).pack(side="right", padx=5)

        # Таблица категорий
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Создаем Treeview с прокруткой
        tree_frame = ctk.CTkFrame(table_frame)
        tree_frame.pack(fill="both", expand=True)

        # Вертикальная прокрутка
        tree_scroll_y = ctk.CTkScrollbar(tree_frame)
        tree_scroll_y.pack(side="right", fill="y")

        # Горизонтальная прокрутка
        tree_scroll_x = ctk.CTkScrollbar(tree_frame, orientation="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")

        # Создаем Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            selectmode="browse"
        )

        # Настраиваем прокрутку
        tree_scroll_y.configure(command=self.tree.yview)
        tree_scroll_x.configure(command=self.tree.xview)

        # Определяем колонки
        self.tree['columns'] = ('id', 'name', 'description', 'color', 'created_at', 'is_active')
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('name', width=200, anchor=tk.W)
        self.tree.column('description', width=300, anchor=tk.W)
        self.tree.column('color', width=100, anchor=tk.W)
        self.tree.column('created_at', width=120, anchor=tk.W)
        self.tree.column('is_active', width=80, anchor=tk.CENTER)

        # Заголовки колонок
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Название категории')
        self.tree.heading('description', text='Описание')
        self.tree.heading('color', text='Цвет')
        self.tree.heading('created_at', text='Дата создания')
        self.tree.heading('is_active', text='Активна')

        self.tree.pack(fill="both", expand=True)

        # Привязываем двойной клик для редактирования
        self.tree.bind('<Double-Button-1>', lambda e: self._edit_category())

        # Статусная строка
        self.status_label = ctk.CTkLabel(
            self,
            text="Загружено категорий: 0",
            font=("Arial", 10)
        )
        self.status_label.pack(side="bottom", fill="x", padx=10, pady=5)

    def refresh_data(self):
        """Обновить данные в таблице"""
        try:
            # Очищаем таблицу
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Загружаем категории
            self.categories = self.controller.get_all_categories()

            # Заполняем таблицу
            for category in self.categories:
                # Создаем цветной квадратик
                color_display = f"■ {category.color}"

                self.tree.insert(
                    '',
                    tk.END,
                    values=(
                        category.id,
                        category.name,
                        category.description,
                        color_display,
                        Formatters.format_date(category.created_at),
                        "✓" if category.is_active else "✗"
                    )
                )

            # Обновляем статус
            self.status_label.configure(
                text=f"Загружено категорий: {len(self.categories)}"
            )

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить категории: {str(e)}")

    def _add_category(self):
        """Добавить новую категорию"""
        dialog = CategoryDialog(self, self.controller, None)
        self.wait_window(dialog)
        if dialog.result:
            self.refresh_data()

    def _edit_category(self):
        """Редактировать выбранную категорию"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите категорию для редактирования")
            return

        # Получаем ID выбранной категории
        item = self.tree.item(selected[0])
        category_id = item['values'][0]

        # Находим категорию
        category = None
        for cat in self.categories:
            if cat.id == category_id:
                category = cat
                break

        if category:
            dialog = CategoryDialog(self, self.controller, category)
            self.wait_window(dialog)
            if dialog.result:
                self.refresh_data()

    def _delete_category(self):
        """Удалить выбранную категорию"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите категорию для удаления")
            return

        # Получаем ID выбранной категории
        item = self.tree.item(selected[0])
        category_id = item['values'][0]
        category_name = item['values'][1]

        # Подтверждение удаления
        if not messagebox.askyesno(
                "Подтверждение удаления",
                f"Вы уверены, что хотите удалить категорию '{category_name}'?"
        ):
            return

        # Здесь должна быть логика удаления категории
        # Пока просто показываем сообщение
        messagebox.showinfo(
            "Удаление категории",
            f"Категория '{category_name}' помечена для удаления.\n"
            "Функция удаления находится в разработке."
        )


class CategoryDialog(ctk.CTkToplevel):
    """Диалоговое окно для добавления/редактирования категории"""

    def __init__(self, parent, controller, category: Optional[CostCategory] = None):
        super().__init__(parent)

        self.controller = controller
        self.category = category
        self.result = False

        # Настройка окна
        title = "Редактировать категорию" if category else "Добавить категорию"
        self.title(title)
        self.geometry("500x400")
        self.resizable(False, False)

        # Делаем окно модальным
        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._fill_data()

    def _create_widgets(self):
        """Создание виджетов диалога"""
        # Основной фрейм
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Заголовок
        title = "Редактировать категорию" if self.category else "Добавить категорию"
        ctk.CTkLabel(
            main_frame,
            text=title,
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 20))

        # Поля ввода
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="x", pady=10)

        # Название категории
        ctk.CTkLabel(form_frame, text="Название категории *:", font=("Arial", 12)).pack(anchor="w", padx=10,
                                                                                        pady=(5, 0))
        self.name_entry = ctk.CTkEntry(form_frame, font=("Arial", 12))
        self.name_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Описание
        ctk.CTkLabel(form_frame, text="Описание:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(5, 0))
        self.desc_entry = ctk.CTkTextbox(form_frame, height=60, font=("Arial", 12))
        self.desc_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Цвет
        ctk.CTkLabel(form_frame, text="Цвет (HEX):", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(5, 0))
        color_frame = ctk.CTkFrame(form_frame)
        color_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.color_entry = ctk.CTkEntry(color_frame, font=("Arial", 12), width=100)
        self.color_entry.pack(side="left", padx=(0, 10))

        # Пример цвета
        self.color_preview = ctk.CTkLabel(
            color_frame,
            text="■■■■■",
            font=("Arial", 16),
            width=50
        )
        self.color_preview.pack(side="left")

        # Привязываем обновление предпросмотра
        self.color_entry.bind('<KeyRelease>', self._update_color_preview)

        # Активность
        self.active_var = tk.BooleanVar(value=True)
        self.active_check = ctk.CTkCheckBox(
            form_frame,
            text="Активная категория",
            variable=self.active_var,
            font=("Arial", 12)
        )
        self.active_check.pack(anchor="w", padx=10, pady=10)

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
        """Заполнить поля данными категории"""
        if self.category:
            self.name_entry.insert(0, self.category.name)
            self.desc_entry.insert("1.0", self.category.description)
            self.color_entry.insert(0, self.category.color)
            self.active_var.set(self.category.is_active)
            self._update_color_preview()

    def _update_color_preview(self, event=None):
        """Обновить предпросмотр цвета"""
        color = self.color_entry.get().strip()
        if color and color.startswith('#'):
            try:
                self.color_preview.configure(text_color=color)
            except:
                pass

    def _save(self):
        """Сохранить категорию"""
        name = self.name_entry.get().strip()
        description = self.desc_entry.get("1.0", "end").strip()
        color = self.color_entry.get().strip()
        is_active = self.active_var.get()

        if not name:
            messagebox.showwarning("Внимание", "Введите название категории")
            return

        # Проверяем цвет
        if not color:
            # Используем цвет по умолчанию для этой категории
            color = self.controller.get_category_color(name)
        elif not color.startswith('#'):
            color = '#' + color

        if self.category:
            # Редактирование существующей категории
            self.category.name = name
            self.category.description = description
            self.category.color = color
            self.category.is_active = is_active

            success, message = self.controller.db.update_category(self.category)
        else:
            # Добавление новой категории
            category = CostCategory(
                name=name,
                description=description,
                color=color,
                is_active=is_active
            )
            success, message = self.controller.add_category(category.name, category.description, category.color)

        if success:
            self.result = True
            self.destroy()
        else:
            messagebox.showerror("Ошибка", message)

    def _cancel(self):
        """Отмена"""
        self.destroy()
