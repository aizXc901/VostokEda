# file: catering-manager/views/settings_view.py
"""
Модуль настроек приложения
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from typing import Optional

from models import Settings
from controllers import CateringController
from .base_view import BasePage


class SettingsPage(BasePage):
    """Страница настроек приложения"""

    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Настройки")
        self.settings: Optional[Settings] = None
        self._create_widgets()
        self.load_settings()

    def _create_widgets(self):
        """Создание виджетов страницы"""
        # Заголовок
        title_frame = ctk.CTkFrame(self)
        title_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            title_frame,
            text="⚙️ Настройки приложения",
            font=("Arial", 18, "bold")
        ).pack(side="left", padx=10)

        # Кнопки управления
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkButton(
            button_frame,
            text="💾 Сохранить",
            command=self.save_settings,
            width=120
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            button_frame,
            text="🔄 Сбросить",
            command=self.load_settings,
            width=120
        ).pack(side="right", padx=5)

        # Основной фрейм с настройками
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Настройки бюджета
        budget_frame = ctk.CTkFrame(main_frame)
        budget_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(
            budget_frame,
            text="📊 Настройки бюджета",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=10)

        # Порог предупреждения о бюджете
        threshold_frame = ctk.CTkFrame(budget_frame)
        threshold_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(threshold_frame, text="Порог предупреждения (80%):", font=("Arial", 12)).pack(anchor="w", padx=10,
                                                                                                   pady=(5, 0))
        self.warning_threshold = ctk.CTkSlider(
            threshold_frame,
            from_=0.0,
            to=1.0,
            number_of_steps=20,
            width=400
        )
        self.warning_threshold.pack(fill="x", padx=10, pady=5)
        self.warning_label = ctk.CTkLabel(threshold_frame, text="80%", font=("Arial", 12))
        self.warning_label.pack(anchor="w", padx=10, pady=(0, 5))

        # Порог тревоги о бюджете
        alert_frame = ctk.CTkFrame(budget_frame)
        alert_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(alert_frame, text="Порог тревоги (90%):", font=("Arial", 12)).pack(anchor="w", padx=10,
                                                                                        pady=(5, 0))
        self.alert_threshold = ctk.CTkSlider(
            alert_frame,
            from_=0.0,
            to=1.0,
            number_of_steps=20,
            width=400
        )
        self.alert_threshold.pack(fill="x", padx=10, pady=5)
        self.alert_label = ctk.CTkLabel(alert_frame, text="90%", font=("Arial", 12))
        self.alert_label.pack(anchor="w", padx=10, pady=(0, 5))

        # Порог критического превышения бюджета
        critical_frame = ctk.CTkFrame(budget_frame)
        critical_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(critical_frame, text="Порог критического превышения (100%):", font=("Arial", 12)).pack(anchor="w",
                                                                                                            padx=10,
                                                                                                            pady=(5, 0))
        self.critical_threshold = ctk.CTkSlider(
            critical_frame,
            from_=0.0,
            to=1.0,
            number_of_steps=20,
            width=400
        )
        self.critical_threshold.pack(fill="x", padx=10, pady=5)
        self.critical_label = ctk.CTkLabel(critical_frame, text="100%", font=("Arial", 12))
        self.critical_label.pack(anchor="w", padx=10, pady=(0, 5))

        # Привязка событий к слайдерам
        self.warning_threshold.configure(command=self._update_warning_label)
        self.alert_threshold.configure(command=self._update_alert_label)
        self.critical_threshold.configure(command=self._update_critical_label)

        # Настройки отчетов
        reports_frame = ctk.CTkFrame(main_frame)
        reports_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(
            reports_frame,
            text="📋 Настройки отчетов",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=10)

        # Формат отчетов
        format_frame = ctk.CTkFrame(reports_frame)
        format_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(format_frame, text="Формат отчетов:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(5, 0))
        self.reports_format = ctk.CTkComboBox(
            format_frame,
            values=["Excel", "PDF", "CSV"],
            width=200,
            font=("Arial", 12)
        )
        self.reports_format.pack(anchor="w", padx=10, pady=5)

        # Настройки резервного копирования
        backup_frame = ctk.CTkFrame(main_frame)
        backup_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(
            backup_frame,
            text="💾 Настройки резервного копирования",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=10)

        # Автоматическое резервное копирование
        auto_backup_frame = ctk.CTkFrame(backup_frame)
        auto_backup_frame.pack(fill="x", padx=10, pady=5)

        self.auto_backup_var = tk.BooleanVar()
        self.auto_backup_check = ctk.CTkCheckBox(
            auto_backup_frame,
            text="Включить автоматическое резервное копирование",
            variable=self.auto_backup_var,
            font=("Arial", 12)
        )
        self.auto_backup_check.pack(anchor="w", padx=10, pady=5)

        # Интервал резервного копирования
        interval_frame = ctk.CTkFrame(backup_frame)
        interval_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(interval_frame, text="Интервал резервного копирования (дней):", font=("Arial", 12)).pack(
            anchor="w", padx=10, pady=(5, 0))
        self.backup_interval = ctk.CTkEntry(interval_frame, width=100, font=("Arial", 12))
        self.backup_interval.pack(anchor="w", padx=10, pady=5)

        # Настройки интерфейса
        interface_frame = ctk.CTkFrame(main_frame)
        interface_frame.pack(fill="x", pady=5)

        ctk.CTkLabel(
            interface_frame,
            text="🎨 Настройки интерфейса",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=10)

        # Язык интерфейса
        lang_frame = ctk.CTkFrame(interface_frame)
        lang_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(lang_frame, text="Язык интерфейса:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(5, 0))
        self.language = ctk.CTkComboBox(
            lang_frame,
            values=["Русский", "English"],
            width=200,
            font=("Arial", 12)
        )
        self.language.pack(anchor="w", padx=10, pady=5)

        # Тема интерфейса
        theme_frame = ctk.CTkFrame(interface_frame)
        theme_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(theme_frame, text="Тема интерфейса:", font=("Arial", 12)).pack(anchor="w", padx=10, pady=(5, 0))
        self.theme = ctk.CTkComboBox(
            theme_frame,
            values=["Темная", "Светлая", "Системная"],
            width=200,
            font=("Arial", 12)
        )
        self.theme.pack(anchor="w", padx=10, pady=5)

    def _update_warning_label(self, value):
        """Обновление метки порога предупреждения"""
        self.warning_label.configure(text=f"{int(float(value) * 100)}%")

    def _update_alert_label(self, value):
        """Обновление метки порога тревоги"""
        self.alert_label.configure(text=f"{int(float(value) * 100)}%")

    def _update_critical_label(self, value):
        """Обновление метки критического порога"""
        self.critical_label.configure(text=f"{int(float(value) * 100)}%")

    # views/settings_view.py
    def load_settings(self):
        """Загрузка текущих настроек"""
        try:
            self.settings = self.controller.get_settings()

            # Установка значений слайдеров
            self.warning_threshold.set(self.settings.budget_warning_threshold)
            self._update_warning_label(self.settings.budget_warning_threshold)

            self.alert_threshold.set(self.settings.budget_alert_threshold)
            self._update_alert_label(self.settings.budget_alert_threshold)

            self.critical_threshold.set(self.settings.budget_critical_threshold)
            self._update_critical_label(self.settings.budget_critical_threshold)

            # Установка формата отчетов
            format_map = {"excel": "Excel", "pdf": "PDF", "csv": "CSV"}
            self.reports_format.set(format_map.get(self.settings.reports_format.lower(), "Excel"))

            # Установка настроек резервного копирования
            self.auto_backup_var.set(self.settings.auto_backup_enabled)
            self.backup_interval.insert(0, str(self.settings.backup_interval_days))

            # Установка языка интерфейса
            lang_map = {"ru": "Русский", "en": "English"}
            self.language.set(lang_map.get(self.settings.language, "Русский"))

            # Установка темы интерфейса
            theme_map = {"dark": "Темная", "light": "Светлая", "system": "Системная"}
            self.theme.set(theme_map.get(self.settings.theme, "Темная"))

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить настройки: {str(e)}")

    def save_settings(self):
        """Сохранение настроек"""
        try:
            # Обновление значений в модели настроек
            self.settings.budget_warning_threshold = float(self.warning_threshold.get())
            self.settings.budget_alert_threshold = float(self.alert_threshold.get())
            self.settings.budget_critical_threshold = float(self.critical_threshold.get())

            format_map = {"Excel": "excel", "PDF": "pdf", "CSV": "csv"}
            self.settings.reports_format = format_map[self.reports_format.get()]

            self.settings.auto_backup_enabled = self.auto_backup_var.get()
            self.settings.backup_interval_days = int(self.backup_interval.get())

            lang_map = {"Русский": "ru", "English": "en"}
            self.settings.language = lang_map[self.language.get()]

            theme_map = {"Темная": "dark", "Светлая": "light", "Системная": "system"}
            self.settings.theme = theme_map[self.theme.get()]

            # Сохранение настроек через контроллер
            success, message = self.controller.save_settings(self.settings)

            if success:
                messagebox.showinfo("Успех", message)
            else:
                messagebox.showerror("Ошибка", message)

        except ValueError:
            messagebox.showerror("Ошибка", "Некорректное значение в одном из полей")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {str(e)}")
