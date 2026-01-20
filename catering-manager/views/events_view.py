"""
Управление мероприятиями
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime, date, time
from typing import List, Optional
from decimal import Decimal

from models import Event
from controllers import CateringController
from utils.formatters import Formatters
from utils.validators import Validators
from .base_view import BasePage


class EventsPage(BasePage):
    """Страница управления мероприятиями"""

    def __init__(self, parent, controller, main_window):
        super().__init__(parent, controller, "Управление мероприятиями")
        self.main_window = main_window
        self.events: List[Event] = []
        self._create_widgets()
        self.refresh_data()

    def _create_widgets(self):
        """Создание виджетов страницы"""
        # Заголовок
        title_frame = ctk.CTkFrame(self)
        title_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            title_frame,
            text="📋 Управление мероприятиями",
            font=("Arial", 18, "bold")
        ).pack(side="left", padx=10)

        # Кнопки управления
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkButton(
            button_frame,
            text="➕ Добавить мероприятие",
            command=self._add_event,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="📝 Заказы",
            command=self._show_orders,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="✅ Выбрать",
            command=self._select_event,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="🔄 Обновить",
            command=self.refresh_data,
            width=150
        ).pack(side="right", padx=5)

        # Таблица мероприятий
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
        self.tree['columns'] = ('id', 'name', 'date', 'time', 'guests', 'budget', 'status', 'location', 'responsible')
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('id', width=50, anchor=tk.CENTER)
        self.tree.column('name', width=200, anchor=tk.W)
        self.tree.column('date', width=100, anchor=tk.CENTER)
        self.tree.column('time', width=80, anchor=tk.CENTER)
        self.tree.column('guests', width=80, anchor=tk.CENTER)
        self.tree.column('budget', width=120, anchor=tk.E)
        self.tree.column('status', width=120, anchor=tk.CENTER)
        self.tree.column('location', width=150, anchor=tk.W)
        self.tree.column('responsible', width=150, anchor=tk.W)

        # Заголовки
        self.tree.heading('id', text='ID')
        self.tree.heading('name', text='Название')
        self.tree.heading('date', text='Дата')
        self.tree.heading('time', text='Время')
        self.tree.heading('guests', text='Гостей')
        self.tree.heading('budget', text='Бюджет, руб')
        self.tree.heading('status', text='Статус')
        self.tree.heading('location', text='Место')
        self.tree.heading('responsible', text='Ответственный')

        self.tree.pack(fill="both", expand=True)

        # Привязка двойного клика
        self.tree.bind('<Double-Button-1>', lambda e: self._select_event())

        # Статус
        self.status_label = ctk.CTkLabel(
            self,
            text="Загружено мероприятий: 0 | Текущее: Не выбрано",
            font=("Arial", 10)
        )
        self.status_label.pack(side="bottom", fill="x", padx=10, pady=5)

    def refresh_data(self):
        """Обновить данные"""
        try:
            # Очищаем таблицу
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Загружаем мероприятия
            self.events = self.controller.get_all_events()

            # Заполняем таблицу
            for event in self.events:
                # Определяем цвет статуса
                status_color = ""
                if event.status == "планируется":
                    status_color = "blue"
                elif event.status == "идет":
                    status_color = "orange"
                elif event.status == "завершено":
                    status_color = "green"

                self.tree.insert(
                    '',
                    tk.END,
                    values=(
                        event.id,
                        event.name,
                        Formatters.format_date(event.event_date),
                        Formatters.format_time(event.start_time),
                        event.guests_count,
                        Formatters.format_currency(event.budget, show_symbol=False),
                        event.status,
                        Formatters.truncate_text(event.location, 20),
                        Formatters.truncate_text(event.responsible_person, 20)
                    ),
                    tags=(event.status,)
                )

            # Настраиваем цвета для статусов
            self.tree.tag_configure('планируется', foreground='blue')
            self.tree.tag_configure('идет', foreground='orange')
            self.tree.tag_configure('завершено', foreground='green')

            # Обновляем статус
            current_event_text = "Не выбрано"
            if self.controller.current_event:
                current_event_text = self.controller.current_event.name

            self.status_label.configure(
                text=f"Загружено мероприятий: {len(self.events)} | Текущее: {current_event_text}"
            )

            # Обновляем отображение бюджета в главном окне
            self.main_window.update_budget_display()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить мероприятия: {str(e)}")

    def _add_event(self):
        """Добавить новое мероприятие"""
        dialog = EventDialog(self, self.controller)
        self.wait_window(dialog)
        if dialog.result:
            self.refresh_data()

    def _select_event(self):
        """Выбрать мероприятие как текущее"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите мероприятие")
            return

        # Получаем ID выбранного мероприятия
        item = self.tree.item(selected[0])
        event_id = item['values'][0]
        event_name = item['values'][1]

        # Выбираем мероприятие в контроллере
        if self.controller.select_event(event_id):
            messagebox.showinfo("Выбор мероприятия", f"Выбрано мероприятие: {event_name}")
            self.refresh_data()  # Обновляем статус
        else:
            messagebox.showerror("Ошибка", "Не удалось выбрать мероприятие")

    def _show_orders(self):
        """Показать заказы для выбранного мероприятия"""
        if not self.controller.current_event:
            messagebox.showwarning("Внимание", "Сначала выберите мероприятие")
            return

        # Создаем окно заказов
        orders_window = OrdersWindow(self, self.controller)
        self.wait_window(orders_window)


class EventDialog(ctk.CTkToplevel):
    """Диалог для добавления/редактирования мероприятия"""

    def __init__(self, parent, controller, event: Optional[Event] = None):
        super().__init__(parent)

        self.controller = controller
        self.event = event
        self.result = False

        # Настройка окна
        title = "Редактировать мероприятие" if event else "Добавить мероприятие"
        self.title(title)
        self.geometry("700x600")
        self.resizable(True, True)

        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self._fill_data()

    def _create_widgets(self):
        """Создание виджетов диалога"""
        # Создаем основной скроллируемый контейнер
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True)

        # Создаем канвас и скроллбар
        canvas = tk.Canvas(main_frame)
        scrollbar = ctk.CTkScrollbar(main_frame, orientation="vertical", command=canvas.yview)

        # Фрейм для размещения всех виджетов внутри канваса
        self.scrollable_frame = ctk.CTkFrame(canvas)

        # Настройка прокрутки
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Размещение элементов
        canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y")

        # Заголовок
        title = "Редактировать мероприятие" if self.event else "Добавить мероприятие"
        ctk.CTkLabel(
            self.scrollable_frame,
            text=title,
            font=("Arial", 16, "bold")
        ).pack(pady=(10, 20), padx=20)

        # Форма
        form_frame = ctk.CTkFrame(self.scrollable_frame)
        form_frame.pack(fill="x", pady=10, padx=20)

        # Название
        ctk.CTkLabel(form_frame, text="Название мероприятия *:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(10, 0))
        self.name_entry = ctk.CTkEntry(form_frame, font=("Arial", 12))
        self.name_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Дата и время
        datetime_frame = ctk.CTkFrame(form_frame)
        datetime_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Дата
        ctk.CTkLabel(datetime_frame, text="Дата *:", font=("Arial", 12)).pack(side="left", padx=(0, 10))
        self.date_entry = ctk.CTkEntry(datetime_frame, font=("Arial", 12), width=100, placeholder_text="дд.мм.гггг")
        self.date_entry.pack(side="left", padx=(0, 20))

        # Время
        ctk.CTkLabel(datetime_frame, text="Время *:", font=("Arial", 12)).pack(side="left", padx=(0, 10))
        self.time_entry = ctk.CTkEntry(datetime_frame, font=("Arial", 12), width=80, placeholder_text="чч:мм")
        self.time_entry.pack(side="left")

        # Количество гостей
        ctk.CTkLabel(form_frame, text="Количество гостей *:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(5, 0))
        self.guests_entry = ctk.CTkEntry(form_frame, font=("Arial", 12))
        self.guests_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Бюджет
        ctk.CTkLabel(form_frame, text="Бюджет, руб *:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(5, 0))
        self.budget_entry = ctk.CTkEntry(form_frame, font=("Arial", 12))
        self.budget_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Место проведения
        ctk.CTkLabel(form_frame, text="Место проведения:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(5, 0))
        self.location_entry = ctk.CTkEntry(form_frame, font=("Arial", 12))
        self.location_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Ответственный
        ctk.CTkLabel(form_frame, text="Ответственный:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(5, 0))
        self.responsible_entry = ctk.CTkEntry(form_frame, font=("Arial", 12))
        self.responsible_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Статус
        ctk.CTkLabel(form_frame, text="Статус:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(5, 0))
        status_options = ["планируется", "идет", "завершено"]
        self.status_combo = ctk.CTkComboBox(
            form_frame,
            values=status_options,
            font=("Arial", 12)
        )
        self.status_combo.pack(fill="x", padx=10, pady=(0, 10))
        self.status_combo.set("планируется")

        # Описание
        ctk.CTkLabel(form_frame, text="Описание:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(5, 0))
        self.description_entry = ctk.CTkTextbox(form_frame, height=100, font=("Arial", 12))
        self.description_entry.pack(fill="x", padx=10, pady=(0, 10))

        # Кнопки
        button_frame = ctk.CTkFrame(self.scrollable_frame)
        button_frame.pack(fill="x", pady=(20, 10), padx=20)

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

        # Настроить прокрутку колесиком мыши
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

    def _fill_data(self):
        """Заполнить поля данными"""
        if self.event:
            self.name_entry.insert(0, self.event.name)
            self.date_entry.insert(0, Formatters.format_date(self.event.event_date))
            self.time_entry.insert(0, Formatters.format_time(self.event.start_time))
            self.guests_entry.insert(0, str(self.event.guests_count))
            self.budget_entry.insert(0, str(self.event.budget))
            self.location_entry.insert(0, self.event.location)
            self.responsible_entry.insert(0, self.event.responsible_person)
            self.status_combo.set(self.event.status)
            self.description_entry.insert("1.0", self.event.description)

    def _save(self):
        """Сохранить мероприятие"""
        name = self.name_entry.get().strip()
        date_str = self.date_entry.get().strip()
        time_str = self.time_entry.get().strip()
        guests_str = self.guests_entry.get().strip()
        budget_str = self.budget_entry.get().strip()
        location = self.location_entry.get().strip()
        responsible = self.responsible_entry.get().strip()
        status = self.status_combo.get()
        description = self.description_entry.get("1.0", "end-1c").strip()

        # Валидация
        if not name:
            messagebox.showwarning("Внимание", "Введите название мероприятия")
            return

        # Валидация даты
        event_date = Validators.validate_date(date_str, allow_past=False)
        if not event_date:
            messagebox.showwarning("Внимание", "Неверный формат даты. Используйте дд.мм.гггг")
            return

        # Валидация времени
        event_time = Validators.validate_time(time_str)
        if not event_time:
            messagebox.showwarning("Внимание", "Неверный формат времени. Используйте чч:мм")
            return

        # Валидация количества гостей
        guests_count = Validators.validate_integer(guests_str)
        if guests_count is None or guests_count <= 0:
            messagebox.showwarning("Внимание", "Введите корректное количество гостей (больше 0)")
            return

        # Валидация бюджета
        budget = Validators.validate_decimal(budget_str)
        if budget is None or budget <= Decimal('0'):
            messagebox.showwarning("Внимание", "Введите корректный бюджет (больше 0)")
            return

        if self.event:
            # Редактирование существующего мероприятия
            self.event.name = name
            self.event.event_date = event_date
            self.event.start_time = event_time
            self.event.guests_count = guests_count
            self.event.budget = budget
            self.event.location = location
            self.event.responsible_person = responsible
            self.event.status = status
            self.event.description = description

            messagebox.showinfo("Редактирование", "Функция редактирования находится в разработке")
        else:
            # Добавление нового мероприятия
            try:
                from models import Event
                from datetime import datetime

                new_event = Event(
                    name=name,
                    event_date=event_date,
                    start_time=event_time,
                    guests_count=guests_count,
                    budget=budget,
                    description=description,
                    location=location,
                    responsible_person=responsible,
                    status=status,
                    created_at=datetime.now()
                )

                # Сохраняем через DatabaseManager
                from database import DatabaseManager
                db = DatabaseManager()
                event_id = db.add_event(new_event)

                if event_id:
                    self.result = True
                    messagebox.showinfo("Успех", f"Мероприятие '{name}' успешно добавлено!")
                    self.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось добавить мероприятие")

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при добавлении мероприятия: {str(e)}")

    def _cancel(self):
        """Отмена"""
        self.destroy()


class OrdersWindow(ctk.CTkToplevel):
    """Окно для просмотра заказов мероприятия"""

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        # Настройка окна
        event_name = controller.current_event.name if controller.current_event else "Мероприятие"
        self.title(f"Заказы мероприятия: {event_name}")
        self.geometry("1000x700")

        self.transient(parent)
        self.grab_set()

        self._create_widgets()
        self.refresh_data()

    def _create_widgets(self):
        """Создание виджетов окна"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Заголовок
        title_frame = ctk.CTkFrame(main_frame)
        title_frame.pack(fill="x", pady=(0, 10))

        event_name = self.controller.current_event.name if self.controller.current_event else "Мероприятие"
        ctk.CTkLabel(
            title_frame,
            text=f"📦 Заказы мероприятия: {event_name}",
            font=("Arial", 16, "bold")
        ).pack(side="left", padx=10)

        # Кнопки
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            button_frame,
            text="➕ Создать заказ",
            command=self._create_order,
            width=150
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="🔄 Обновить",
            command=self.refresh_data,
            width=150
        ).pack(side="right", padx=5)

        # Таблица заказов
        table_frame = ctk.CTkFrame(main_frame)
        table_frame.pack(fill="both", expand=True)

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
        self.tree['columns'] = ('number', 'date', 'status', 'items', 'amount', 'notes')
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('number', width=120, anchor=tk.W)
        self.tree.column('date', width=120, anchor=tk.W)
        self.tree.column('status', width=100, anchor=tk.CENTER)
        self.tree.column('items', width=80, anchor=tk.CENTER)
        self.tree.column('amount', width=120, anchor=tk.RIGHT)
        self.tree.column('notes', width=300, anchor=tk.W)

        # Заголовки
        self.tree.heading('number', text='Номер заказа')
        self.tree.heading('date', text='Дата заказа')
        self.tree.heading('status', text='Статус')
        self.tree.heading('items', text='Позиций')
        self.tree.heading('amount', text='Сумма, руб')
        self.tree.heading('notes', text='Примечания')

        self.tree.pack(fill="both", expand=True)

        # Привязка двойного клика
        self.tree.bind('<Double-Button-1>', lambda e: self._view_order_details())

        # Статус
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Загружено заказов: 0",
            font=("Arial", 10)
        )
        self.status_label.pack(side="bottom", fill="x", pady=5)

    def refresh_data(self):
        """Обновить данные"""
        if not self.controller.current_event:
            return

        try:
            # Очищаем таблицу
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Загружаем заказы
            orders = self.controller.get_orders_for_current_event()

            # Заполняем таблицу
            for order in orders:
                self.tree.insert(
                    '',
                    tk.END,
                    values=(
                        order.order_number,
                        Formatters.format_datetime(order.order_date),
                        order.status,
                        len(order.items),
                        Formatters.format_currency(order.total_amount, show_symbol=False),
                        Formatters.truncate_text(order.notes, 40)
                    ),
                    tags=(order.status,)
                )

            # Настраиваем цвета для статусов
            self.tree.tag_configure('черновик', foreground='gray')
            self.tree.tag_configure('подтвержден', foreground='green')
            self.tree.tag_configure('отменен', foreground='red')

            # Обновляем статус
            self.status_label.configure(
                text=f"Загружено заказов: {len(orders)} | Общая сумма: {Formatters.format_currency(sum(o.total_amount for o in orders))}"
            )

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить заказы: {str(e)}")

    def _create_order(self):
        """Создать новый заказ"""
        if not self.controller.current_event:
            messagebox.showwarning("Внимание", "Не выбрано мероприятие")
            return

        messagebox.showinfo("Создание заказа", "Функция создания заказа находится в разработке")

    def _view_order_details(self):
        """Просмотреть детали заказа"""
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        order_number = item['values'][0]

        messagebox.showinfo(
            "Детали заказа",
            f"Заказ №{order_number}\n\nФункция просмотра деталей находится в разработке."
        )