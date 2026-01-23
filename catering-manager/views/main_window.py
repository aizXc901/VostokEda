"""
Главное окно приложения
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from datetime import datetime
from typing import Optional, List

from config import Config
from models import *
from controllers import CateringController
from utils.formatters import Formatters

# Импорты страниц (убраны циклические зависимости)
from .categories_view import CategoriesPage
from .nomenclature_view import NomenclaturePage
from .suppliers_view import SuppliersPage
from .events_view import EventsPage
from .orders_view import OrdersPage
from .reports_view import ReportsPage

# Глобальная переменная для отслеживания активного окна
_active_window = None

class MainWindow(ctk.CTk):
    """Главное окно приложения"""

    # Статическое свойство для доступа к экземпляру
    _instance = None

    def __init__(self, controller: CateringController):
        # Проверка на существование экземпляра
        if MainWindow._instance is not None:
            raise RuntimeError("MainWindow уже существует!")

        # Сохраняем ссылку на экземпляр
        MainWindow._instance = self
        global _active_window
        _active_window = self

        super().__init__()

        self.controller = controller

        # Настройка окна
        self.title(f"{Config.APP_NAME} v{Config.APP_VERSION}")
        self.geometry("1200x700")
        self.minsize(1000, 600)  # Минимальный размер окна

        # Настройка реакции на закрытие окна
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Создание интерфейса
        self._create_widgets()
        self._setup_layout()

        # Загрузка данных
        self._load_initial_data()

    def _on_closing(self):
        """Обработка закрытия окна"""
        # Удаляем ссылку на экземпляр
        MainWindow._instance = None
        global _active_window
        _active_window = None

        # Закрываем окно
        self.destroy()

    def _create_widgets(self):
        """Создание виджетов"""
        # Верхняя панель
        self.top_frame = ctk.CTkFrame(self, height=50)

        self.title_label = ctk.CTkLabel(
            self.top_frame,
            text=Config.APP_NAME,
            font=("Arial", 20, "bold")
        )

        self.status_label = ctk.CTkLabel(
            self.top_frame,
            text="Готов к работе",
            font=("Arial", 12)
        )

        # Левая панель навигации
        self.nav_frame = ctk.CTkFrame(self, width=200)

        nav_buttons = [
            ("📋 Мероприятия", self.show_events),
            ("🍽️ Номенклатура", self.show_nomenclature),
            ("🏢 Поставщики", self.show_suppliers),
            ("📊 Отчеты", self.show_reports),
            ("⚙️ Настройки", self.show_settings),
            ("ℹ️ О программе", self.show_about)
        ]

        self.nav_buttons = []
        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                self.nav_frame,
                text=text,
                command=command,
                anchor="w",
                height=40,
                font=("Arial", 14)
            )
            self.nav_buttons.append(btn)

        # Основная область
        self.main_frame = ctk.CTkFrame(self)

        # Виджет бюджета (будет отображаться при выборе мероприятия)
        self.budget_frame = ctk.CTkFrame(self.main_frame)
        self.budget_label = ctk.CTkLabel(
            self.budget_frame,
            text="Бюджет мероприятия: не выбран",
            font=("Arial", 14, "bold")
        )

        self.budget_progress = ctk.CTkProgressBar(self.budget_frame)
        self.budget_progress.set(0)

        self.budget_details = ctk.CTkLabel(
            self.budget_frame,
            text="",
            font=("Arial", 12)
        )

        # Область контента
        self.content_frame = ctk.CTkFrame(self.main_frame)

        # Инициализация страниц
        self._init_pages()

    def _setup_layout(self):
        """Настройка layout"""
        # Верхняя панель
        self.top_frame.pack(side="top", fill="x", padx=10, pady=5)
        self.title_label.pack(side="left", padx=20)
        self.status_label.pack(side="right", padx=20)

        # Основной layout
        self.nav_frame.pack(side="left", fill="y", padx=10, pady=10)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Размещение кнопок навигации
        for btn in self.nav_buttons:
            btn.pack(fill="x", padx=10, pady=5)

        # Бюджетная панель
        self.budget_frame.pack(fill="x", padx=10, pady=5)
        self.budget_label.pack(anchor="w", padx=10, pady=5)
        self.budget_progress.pack(fill="x", padx=10, pady=5)
        self.budget_details.pack(anchor="w", padx=10, pady=(0, 5))

        # Область контента
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Скрываем бюджетную панель по умолчанию
        self.budget_frame.pack_forget()

    def _init_pages(self):
        """Инициализация страниц"""
        # Страница мероприятий
        self.events_page = EventsPage(self.content_frame, self.controller, self)

        # Страница номенклатуры
        self.nomenclature_page = NomenclaturePage(self.content_frame, self.controller)

        # Страница поставщиков
        self.suppliers_page = SuppliersPage(self.content_frame, self.controller)

        # Страница отчетов
        self.reports_page = ReportsPage(self.content_frame, self.controller)

        # Показываем страницу мероприятий по умолчанию
        self.show_events()

    def _load_initial_data(self):
        """Загрузка начальных данных"""
        self.update_status("Загрузка данных...")

        # Здесь можно загрузить начальные данные

        self.update_status("Готов к работе")

    def update_status(self, message: str):
        """Обновить статусную строку"""
        self.status_label.configure(text=message)
        self.update()

    def show_budget_panel(self, show: bool = True):
        """Показать/скрыть панель бюджета"""
        if show:
            self.budget_frame.pack(fill="x", padx=10, pady=5)
        else:
            self.budget_frame.pack_forget()

    def update_budget_display(self):
        """Обновить отображение бюджета"""
        if not self.controller.current_event:
            self.show_budget_panel(False)
            return

        budget_status = self.controller.get_budget_status()

        self.budget_label.configure(
            text=f"Бюджет мероприятия: {self.controller.current_event.name}"
        )

        # Прогресс-бар
        usage = budget_status['percentage'] / 100
        self.budget_progress.set(min(usage, 1.0))

        # Цвет прогресс-бара в зависимости от использования
        if usage < Config.BUDGET_WARNING_THRESHOLD:
            self.budget_progress.configure(progress_color="green")
        elif usage < Config.BUDGET_ALERT_THRESHOLD:
            self.budget_progress.configure(progress_color="yellow")
        elif usage < Config.BUDGET_CRITICAL_THRESHOLD:
            self.budget_progress.configure(progress_color="orange")
        else:
            self.budget_progress.configure(progress_color="red")

        # Детали бюджета
        details = (
            f"Выделено: {Formatters.format_currency(budget_status['budget'])} | "
            f"Потрачено: {Formatters.format_currency(budget_status['spent'])} | "
            f"Осталось: {Formatters.format_currency(budget_status['remaining'])} | "
            f"Использовано: {Formatters.format_percentage(budget_status['percentage'])}"
        )
        self.budget_details.configure(text=details)

        self.show_budget_panel(True)

    # ===== Навигация =====

    def show_events(self):
        """Показать страницу мероприятий"""
        self._hide_all_pages()
        self.events_page.pack(fill="both", expand=True)
        self.update_budget_display()

    def show_nomenclature(self):
        """Показать страницу номенклатуры"""
        self._hide_all_pages()
        self.nomenclature_page.pack(fill="both", expand=True)
        self.show_budget_panel(False)

    def show_suppliers(self):
        """Показать страницу поставщиков"""
        self._hide_all_pages()
        self.suppliers_page.pack(fill="both", expand=True)
        self.show_budget_panel(False)

    def show_reports(self):
        """Показать страницу отчетов"""
        self._hide_all_pages()
        self.reports_page.pack(fill="both", expand=True)
        self.update_budget_display()

    def show_settings(self):
        """Показать страницу настроек"""
        messagebox.showinfo("Настройки", "Раздел настроек находится в разработке")

    def show_about(self):
        """Показать информацию о программе"""
        about_text = f"""
{Config.APP_NAME} v{Config.APP_VERSION}

Разработано для:
{Config.APP_COMPANY}

Автоматизация организации питания на мероприятиях

© 2024 Все права защищены
"""
        messagebox.showinfo("О программе", about_text)

    def _hide_all_pages(self):
        """Скрыть все страницы"""
        for page in [self.events_page, self.nomenclature_page,
                    self.suppliers_page, self.reports_page]:
            page.pack_forget()

    def focus_window(self):
        """Фокусировка на окне"""
        self.lift()
        self.focus_force()
