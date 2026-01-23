""" Управление номенклатурой """
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from typing import List, Optional
from models import Nomenclature, CostCategory
from controllers import CateringController
from utils.formatters import Formatters
from .base_view import BasePage
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

        ctk.CTkLabel(filter_frame, text="Поиск:", font=("Arial", 12)).pack(side="left", padx=(20, 5))

        self.search_entry = ctk.CTkEntry(filter_frame, width=150, font=("Arial", 12))
        self.search_entry.pack(side="left", padx=5)
        self.search_entry.bind('<KeyRelease>', self._apply_filter)

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
            text="🗑️ Удалить",
            command=self._delete_nomenclature,
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

    def refresh_data(self):
        """Обновить данные"""
        try:
            # Очищаем таблицу
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Загружаем данные
            self.nomenclatures = self.controller.get_all_nomenclatures()
            self.categories = self.controller.get_all_categories()

            # Обновляем фильтр категорий
            category_names = ["Все категории"] + [cat.name for cat in self.categories]
            self.category_filter.configure(values=category_names)
            self.category_filter.set("Все категории")

            # Заполняем таблицу
            for nomenclature in self.nomenclatures:
                category_name = ""
                if nomenclature.category:
                    category_name = nomenclature.category.name
                elif nomenclature.category_id:
                    for cat in self.categories:
                        if cat.id == nomenclature.category_id:
                            category_name = cat.name
                            break

                self.tree.insert(
                    '',
                    tk.END,
                    values=(
                        nomenclature.id,
                        nomenclature.name,
                        category_name,
                        nomenclature.unit,
                        Formatters.truncate_text(nomenclature.description, 40),
                        Formatters.format_date(nomenclature.created_at),
                        "✓" if nomenclature.is_active else "✗"
                    ),
                    tags=('active' if nomenclature.is_active else 'inactive')
                )

            # Настраиваем цвета строк
            self.tree.tag_configure('active', foreground='black')
            self.tree.tag_configure('inactive', foreground='gray')

            # Обновляем статус
            self.status_label.configure(
                text=f"Загружено позиций: {len(self.nomenclatures)}"
            )

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить номенклатуру: {str(e)}")

    def _apply_filter(self, event=None):
        """Применить фильтры"""
        category_filter = self.category_filter.get()
        search_text = self.search_entry.get().strip().lower()

        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            show_item = True

            # Фильтр по категории
            if category_filter != "Все категории" and values[2] != category_filter:
                show_item = False

            # Фильтр по поисковому запросу
            if search_text:
                item_matches = any(search_text in str(val).lower() for val in values)
                if not item_matches:
                    show_item = False

            # Показываем/скрываем строку
            if show_item:
                self.tree.item(item, tags=())
            else:
                self.tree.item(item, tags=('hidden',))

        self.tree.tag_configure('hidden', foreground='gray90')

    def _add_nomenclature(self):
        """Добавить новую номенклатуру"""
        if not self.categories:
            messagebox.showwarning("Внимание", "Сначала создайте категории затрат")
            return

        dialog = NomenclatureDialog(self, self.controller, None, self.categories)
        self.wait_window(dialog)
        if dialog.result:
            self.refresh_data()

    def _edit_nomenclature(self):
        """Редактировать выбранную номенклатуру"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите позицию для редактирования")
            return

        # Получаем ID выбранной номенклатуры
        item = self.tree.item(selected[0])
        nomenclature_id = item['values'][0]

        # Находим номенклатуру
        nomenclature = None
        for nom in self.nomenclatures:
            if nom.id == nomenclature_id:
                nomenclature = nom
                break

        if nomenclature:
            dialog = NomenclatureDialog(self, self.controller, nomenclature, self.categories)
            self.wait_window(dialog)
            if dialog.result:
                self.refresh_data()

    def _delete_nomenclature(self):
        """Удалить выбранную номенклатуру"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите позицию для удаления")
            return

        # Получаем ID выбранной номенклатуры
        item = self.tree.item(selected[0])
        nomenclature_id = item['values'][0]
        nomenclature_name = item['values'][1]

        if messagebox.askyesno("Подтверждение", f"Удалить позицию '{nomenclature_name}'?"):
            try:
                from database import DatabaseManager
                db = DatabaseManager()

                # Проверяем, используется ли номенклатура в заказах
                orders_with_this_nomenclature = db.get_orders_using_nomenclature(nomenclature_id)
                if orders_with_this_nomenclature:
                    messagebox.showwarning(
                        "Внимание",
                        f"Номенклатура '{nomenclature_name}' используется в {len(orders_with_this_nomenclature)} заказах.\n" +
                        "Удаление невозможно."
                    )
                    return

                # Удаляем номенклатуру
                success, message = db.delete_nomenclature(nomenclature_id)
                if success:
                    messagebox.showinfo("Успех", message)
                    self.refresh_data()
                else:
                    messagebox.showerror("Ошибка", message)

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить номенклатуру: {str(e)}")

class NomenclatureDialog(ctk.CTkToplevel):
    """Диалог для добавления/редактирования номенклатуры"""
    def __init__(self, parent, controller, nomenclature: Optional[Nomenclature] = None, categories: List[CostCategory] = None):
        super().__init__(parent)

        self.controller = controller
        self.nomenclature = nomenclature
        self.categories = categories or []
        self.result = False

        # Настройка окна
        title = "Редактировать позицию" if nomenclature else "Добавить позицию"
        self.title(title)
        self.geometry("700x550")
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
        title = "Редактировать позицию" if self.nomenclature else "Добавить позицию"
        ctk.CTkLabel(
            main_frame,
            text=title,
            font=("Arial", 16, "bold")
        ).pack(pady=(0, 20))

        # Форма
        form_frame = ctk.CTkFrame(main_frame)
        form_frame.pack(fill="x", pady=10)

        # Название
        ctk.CTkLabel(form_frame, text="Название *:", font=("Arial", 12)).pack(anchor="w", pady=(5, 0))
        self.name_entry = ctk.CTkEntry(form_frame, font=("Arial", 12))
        self.name_entry.pack(fill="x", pady=(0, 10))

        # Категория
        ctk.CTkLabel(form_frame, text="Категория *:", font=("Arial", 12)).pack(anchor="w", pady=(5, 0))

        category_names = [cat.name for cat in self.categories]
        self.category_combo = ctk.CTkComboBox(
            form_frame,
            values=category_names,
            font=("Arial", 12)
        )
        self.category_combo.pack(fill="x", pady=(0, 10))

        # Единица измерения
        ctk.CTkLabel(form_frame, text="Единица измерения *:", font=("Arial", 12)).pack(anchor="w", pady=(5, 0))
        self.unit_entry = ctk.CTkEntry(form_frame, font=("Arial", 12))
        self.unit_entry.pack(fill="x", pady=(0, 10))
        self.unit_entry.insert(0, "шт.")

        # Описание
        ctk.CTkLabel(form_frame, text="Описание:", font=("Arial", 12)).pack(anchor="w", pady=(5, 0))
        self.description_text = ctk.CTkTextbox(form_frame, height=80, font=("Arial", 12))
        self.description_text.pack(fill="x", pady=(0, 10))

        # Активность
        self.active_var = tk.BooleanVar(value=True)
        self.active_check = ctk.CTkCheckBox(
            form_frame,
            text="Активная позиция",
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
        if self.nomenclature:
            self.name_entry.insert(0, self.nomenclature.name)
            self.unit_entry.insert(0, self.nomenclature.unit)
            self.description_text.insert("1.0", self.nomenclature.description)
            self.active_var.set(self.nomenclature.is_active)

            # Устанавливаем категорию
            if self.nomenclature.category:
                self.category_combo.set(self.nomenclature.category.name)
            elif self.nomenclature.category_id:
                for cat in self.categories:
                    if cat.id == self.nomenclature.category_id:
                        self.category_combo.set(cat.name)
                        break

    def _save(self):
        """Сохранить номенклатуру"""
        name = self.name_entry.get().strip()
        category_name = self.category_combo.get()
        unit = self.unit_entry.get().strip()
        description = self.description_text.get("1.0", "end").strip()
        is_active = self.active_var.get()

        if not name:
            messagebox.showwarning("Внимание", "Введите название позиции")
            return

        if not category_name:
            messagebox.showwarning("Внимание", "Выберите категорию")
            return

        if not unit:
            messagebox.showwarning("Внимание", "Введите единицу измерения")
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

        if self.nomenclature:
            # Редактирование существующей номенклатуры
            self.nomenclature.name = name
            self.nomenclature.category_id = category_id
            self.nomenclature.unit = unit
            self.nomenclature.description = description
            self.nomenclature.is_active = is_active

            try:
                from database import DatabaseManager
                db = DatabaseManager()
                success, message = db.update_nomenclature(self.nomenclature)

                if success:
                    self.result = True
                    self.destroy()
                else:
                    messagebox.showerror("Ошибка", message)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось обновить номенклатуру: {str(e)}")
        else:
            # Добавление новой номенклатуры
            try:
                from database import DatabaseManager
                db = DatabaseManager()

                new_nomenclature = Nomenclature(
                    name=name,
                    category_id=category_id,
                    unit=unit,
                    description=description,
                    is_active=is_active
                )

                nomenclature_id = db.add_nomenclature(new_nomenclature)
                if nomenclature_id:
                    self.result = True
                    messagebox.showinfo("Успех", f"Позиция '{name}' успешно добавлена!")
                    self.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось добавить позицию")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить номенклатуру: {str(e)}")

    def _cancel(self):
        """Отмена"""
        self.destroy()
