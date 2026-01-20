"""
Виджет контроля бюджета
"""

import tkinter as tk
import customtkinter as ctk
from decimal import Decimal
from typing import Dict, Any

from config import Config
from utils.formatters import Formatters

class BudgetWidget(ctk.CTkFrame):
    """Виджет для отображения и контроля бюджета"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        self.budget_data: Dict[str, Any] = {}
        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов"""
        # Заголовок
        self.title_label = ctk.CTkLabel(
            self,
            text="Контроль бюджета",
            font=("Arial", 14, "bold")
        )
        self.title_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Прогресс-бар
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(fill="x", padx=10, pady=5)
        self.progress_bar.set(0)

        # Детали бюджета
        self.details_frame = ctk.CTkFrame(self)
        self.details_frame.pack(fill="x", padx=10, pady=5)

        # Размещаем метки в сетке
        self.budget_labels = {}

        labels_info = [
            ("budget", "Бюджет:", "0 ₽"),
            ("spent", "Потрачено:", "0 ₽"),
            ("remaining", "Осталось:", "0 ₽"),
            ("percentage", "Использовано:", "0%")
        ]

        for i, (key, label_text, default_value) in enumerate(labels_info):
            row = i // 2
            col = (i % 2) * 2

            # Метка названия
            name_label = ctk.CTkLabel(
                self.details_frame,
                text=label_text,
                font=("Arial", 11)
            )
            name_label.grid(row=row, column=col, padx=(5, 2), pady=2, sticky="w")

            # Метка значения
            value_label = ctk.CTkLabel(
                self.details_frame,
                text=default_value,
                font=("Arial", 11, "bold")
            )
            value_label.grid(row=row, column=col + 1, padx=(2, 5), pady=2, sticky="e")

            self.budget_labels[key] = value_label

        # Статус бюджета
        self.status_label = ctk.CTkLabel(
            self,
            text="Статус: Нормальный",
            font=("Arial", 11)
        )
        self.status_label.pack(anchor="w", padx=10, pady=(5, 10))

    def update_budget(self, budget_data: Dict[str, Any]):
        """Обновить данные бюджета"""
        self.budget_data = budget_data

        # Обновляем значения
        if 'budget' in budget_data:
            self.budget_labels['budget'].configure(
                text=Formatters.format_currency(budget_data['budget'])
            )

        if 'spent' in budget_data:
            self.budget_labels['spent'].configure(
                text=Formatters.format_currency(budget_data['spent'])
            )

        if 'remaining' in budget_data:
            self.budget_labels['remaining'].configure(
                text=Formatters.format_currency(budget_data['remaining'])
            )

        if 'percentage' in budget_data:
            percentage = budget_data['percentage']
            self.budget_labels['percentage'].configure(
                text=Formatters.format_percentage(percentage)
            )

            # Обновляем прогресс-бар
            progress_value = min(percentage / 100, 1.0)
            self.progress_bar.set(progress_value)

            # Меняем цвет в зависимости от использования
            if percentage < Config.BUDGET_WARNING_THRESHOLD * 100:  # <--- Исправлено
                self.progress_bar.configure(progress_color="green")
                self.status_label.configure(text="Статус: В норме", text_color="green")
            elif percentage < Config.BUDGET_ALERT_THRESHOLD * 100:  # <--- Исправлено
                self.progress_bar.configure(progress_color="yellow")
                self.status_label.configure(text="Статус: Предупреждение", text_color="orange")
            elif percentage < Config.BUDGET_CRITICAL_THRESHOLD * 100:  # <--- Исправлено
                self.progress_bar.configure(progress_color="orange")
                self.status_label.configure(text="Статус: Опасность", text_color="red")
            else:
                self.progress_bar.configure(progress_color="red")
                self.status_label.configure(text="Статус: ПРЕВЫШЕНИЕ БЮДЖЕТА!", text_color="red")

    def set_event_name(self, event_name: str):
        """Установить название мероприятия"""
        if event_name:
            self.title_label.configure(text=f"Бюджет: {event_name}")
        else:
            self.title_label.configure(text="Контроль бюджета")
