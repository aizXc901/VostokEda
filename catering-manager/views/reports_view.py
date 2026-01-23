"""
Модуль отчетов
"""

import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog  # Добавлен импорт filedialog
import customtkinter as ctk
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd


from models import Event, EventSummary, ExpenseReportItem
from controllers import CateringController
from utils.formatters import Formatters
from .base_view import BasePage


class ReportsPage(BasePage):
    """Страница отчетов"""

    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Отчеты")
        self.selected_event: Optional[Event] = None
        self._create_widgets()
        self._load_events()

    def _create_widgets(self):
        """Создание виджетов страницы"""
        # Заголовок
        title_frame = ctk.CTkFrame(self)
        title_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            title_frame,
            text="📊 Отчеты и аналитика",
            font=("Arial", 18, "bold")
        ).pack(side="left", padx=10)

        # Выбор мероприятия
        selection_frame = ctk.CTkFrame(self)
        selection_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(selection_frame, text="Мероприятие:", font=("Arial", 12)).pack(side="left", padx=10)

        self.event_combo = ctk.CTkComboBox(
            selection_frame,
            values=[],
            width=300,
            font=("Arial", 12),
            command=self._on_event_selected
        )
        self.event_combo.pack(side="left", padx=10)

        ctk.CTkButton(
            selection_frame,
            text="🔄 Обновить",
            command=self._refresh_reports,
            width=100
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            selection_frame,
            text="📈 Все мероприятия",
            command=self._show_overall_report,
            width=150
        ).pack(side="right", padx=5)

        # Вкладки отчетов
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Вкладка "Обзор"
        self.tabview.add("Обзор")
        self._create_overview_tab()

        # Вкладка "Расходы"
        self.tabview.add("Расходы")
        self._create_expenses_tab()

        # Вкладка "Анализ"
        self.tabview.add("Анализ")
        self._create_analysis_tab()

    def _create_overview_tab(self):
        """Создание вкладки обзора"""
        # Информационные панели
        info_frame = ctk.CTkFrame(self.tabview.tab("Обзор"))
        info_frame.pack(fill="x", padx=10, pady=10)

        # Общая информация о мероприятии
        self.event_info_frame = ctk.CTkFrame(info_frame)
        self.event_info_frame.pack(fill="x", padx=10, pady=10)

        self.event_info_label = ctk.CTkLabel(
            self.event_info_frame,
            text="Выберите мероприятие для просмотра информации",
            font=("Arial", 12)
        )
        self.event_info_label.pack(pady=20)

        # Панель статуса бюджета
        self.budget_status_frame = ctk.CTkFrame(info_frame)
        self.budget_status_frame.pack(fill="x", padx=10, pady=10)

        self.budget_status_label = ctk.CTkLabel(
            self.budget_status_frame,
            text="Бюджет: не выбран",
            font=("Arial", 12)
        )
        self.budget_status_label.pack(pady=5)

        self.budget_progress = ctk.CTkProgressBar(self.budget_status_frame)
        self.budget_progress.pack(fill="x", padx=10, pady=5)
        self.budget_progress.set(0)

        # Краткая статистика
        stats_frame = ctk.CTkFrame(self.tabview.tab("Обзор"))
        stats_frame.pack(fill="x", padx=10, pady=10)

        self.stats_labels = []
        for i in range(4):
            stat_frame = ctk.CTkFrame(stats_frame)
            stat_frame.pack(side="left", fill="x", expand=True, padx=5)

            value_label = ctk.CTkLabel(
                stat_frame,
                text="0",
                font=("Arial", 18, "bold")
            )
            value_label.pack(pady=10)

            desc_label = ctk.CTkLabel(
                stat_frame,
                text="",
                font=("Arial", 10)
            )
            desc_label.pack(pady=(0, 10))

            self.stats_labels.append((value_label, desc_label))

    def _create_expenses_tab(self):
        """Создание вкладки расходов"""
        # Таблица расходов
        expenses_table_frame = ctk.CTkFrame(self.tabview.tab("Расходы"))
        expenses_table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Treeview для расходов
        tree_frame = ctk.CTkFrame(expenses_table_frame)
        tree_frame.pack(fill="both", expand=True)

        tree_scroll_y = ctk.CTkScrollbar(tree_frame)
        tree_scroll_y.pack(side="right", fill="y")

        self.expenses_tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=tree_scroll_y.set,
            selectmode="browse"
        )

        tree_scroll_y.configure(command=self.expenses_tree.yview)

        # Колонки
        self.expenses_tree['columns'] = ('category', 'planned', 'actual', 'difference', 'percentage')
        self.expenses_tree.column('#0', width=0, stretch=tk.NO)
        self.expenses_tree.column('category', width=200, anchor=tk.W)
        self.expenses_tree.column('planned', width=120, anchor=tk.E)
        self.expenses_tree.column('actual', width=120, anchor=tk.E)
        self.expenses_tree.column('difference', width=120, anchor=tk.E)
        self.expenses_tree.column('percentage', width=100, anchor=tk.CENTER)

        # Заголовки
        self.expenses_tree.heading('category', text='Категория')
        self.expenses_tree.heading('planned', text='План, руб')
        self.expenses_tree.heading('actual', text='Факт, руб')
        self.expenses_tree.heading('difference', text='Разница, руб')
        self.expenses_tree.heading('percentage', text='% исполнения')

        self.expenses_tree.pack(fill="both", expand=True)

    def _create_analysis_tab(self):
        """Создание вкладки анализа"""
        # Фрейм для графиков
        charts_frame = ctk.CTkFrame(self.tabview.tab("Анализ"))
        charts_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Canvas для matplotlib графиков
        self.figure_frame = ctk.CTkFrame(charts_frame)
        self.figure_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def _load_events(self):
        """Загрузка списка мероприятий"""
        try:
            events = self.controller.get_all_events()
            event_names = [f"{event.name} ({Formatters.format_date(event.event_date)})" for event in events]
            self.event_combo.configure(values=event_names)

            if events:
                self.event_combo.set(event_names[0])
                self.selected_event = events[0]
                self._refresh_reports()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить мероприятия: {str(e)}")

    def _on_event_selected(self, choice):
        """Обработка выбора мероприятия"""
        if not choice:
            return

        # Найти выбранное мероприятие
        events = self.controller.get_all_events()
        for event in events:
            event_display = f"{event.name} ({Formatters.format_date(event.event_date)})"
            if event_display == choice:
                self.selected_event = event
                break

        self._refresh_reports()

    def _refresh_reports(self):
        """Обновление всех отчетов"""
        if not self.selected_event:
            return

        try:
            # Получить данные отчета
            summary = self.controller.get_expense_report(self.selected_event.id)
            if not summary:
                return

            # Обновить вкладку "Обзор"
            self._update_overview_tab(summary)

            # Обновить вкладку "Расходы"
            self._update_expenses_tab(summary)

            # Обновить вкладку "Анализ"
            self._update_analysis_tab(summary)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить отчеты: {str(e)}")

    def _show_overall_report(self):
        """Показать отчет по всем мероприятиям"""
        try:
            # В будущем можно реализовать общий отчет по всем мероприятиям
            messagebox.showinfo("В разработке", "Общий отчет по всем мероприятиям будет реализован позже")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при отображении общего отчета: {str(e)}")

    def _update_overview_tab(self, summary: EventSummary):
        """Обновление вкладки обзора"""
        # Обновить информацию о мероприятии
        event_info = (
            f"Мероприятие: {summary.event.name}\n"
            f"Дата: {Formatters.format_date(summary.event.event_date)}\n"
            f"Статус: {summary.event.status}\n"
            f"Гостей: {summary.event.guests_count}\n"
            f"Бюджет: {Formatters.format_currency(summary.event.budget)}"
        )
        self.event_info_label.configure(text=event_info)

        # Обновить статус бюджета
        budget_used = summary.total_amount
        budget_total = summary.event.budget
        budget_remaining = budget_total - budget_used

        if budget_total > 0:
            usage_percentage = (budget_used / budget_total) * 100
        else:
            usage_percentage = 0

        self.budget_status_label.configure(
            text=(
                f"Бюджет: {Formatters.format_currency(budget_total)} | "
                f"Потрачено: {Formatters.format_currency(budget_used)} | "
                f"Осталось: {Formatters.format_currency(budget_remaining)} | "
                f"Использовано: {Formatters.format_percentage(usage_percentage)}"
            )
        )

        # Обновить прогресс-бар бюджета
        progress_value = min(usage_percentage / 100, 1.0)
        self.budget_progress.set(progress_value)

        # Цвет прогресс-бара
        if usage_percentage < 80:
            self.budget_progress.configure(progress_color="green")
        elif usage_percentage < 90:
            self.budget_progress.configure(progress_color="yellow")
        elif usage_percentage < 100:
            self.budget_progress.configure(progress_color="orange")
        else:
            self.budget_progress.configure(progress_color="red")

        # Обновить статистику
        stats_data = [
            (summary.total_orders, "Заказов"),
            (Formatters.format_currency(summary.total_amount), "Потрачено"),
            (Formatters.format_percentage(summary.budget_utilization), "Использовано бюджета"),
            (len(summary.categories_summary), "Категорий")
        ]

        for i, (value, description) in enumerate(stats_data):
            if i < len(self.stats_labels):
                value_label, desc_label = self.stats_labels[i]
                value_label.configure(text=str(value))
                desc_label.configure(text=description)

    def _update_expenses_tab(self, summary: EventSummary):
        """Обновление вкладки расходов"""
        # Очистить таблицу
        for item in self.expenses_tree.get_children():
            self.expenses_tree.delete(item)

        # Заполнить таблицу данными
        for item in summary.categories_summary:
            # Рассчитать разницу
            difference = item.actual_amount - item.planned_amount

            # Рассчитать процент выполнения
            if item.planned_amount > 0:
                percentage = (item.actual_amount / item.planned_amount) * 100
            else:
                percentage = 0

            # Добавить строку в таблицу
            self.expenses_tree.insert(
                '',
                tk.END,
                values=(
                    item.category_name,
                    Formatters.format_currency(item.planned_amount, show_symbol=False),
                    Formatters.format_currency(item.actual_amount, show_symbol=False),
                    Formatters.format_currency(difference, show_symbol=False),
                    f"{Formatters.format_percentage(percentage)}"
                )
            )

    def _create_general_report_tab(self):
        """Создание вкладки общего отчета"""
        # Информационная панель
        info_frame = ctk.CTkFrame(self.tabview.tab("Общий отчет"))
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Текстовое поле для отображения общей статистики
        self.general_report_text = ctk.CTkTextbox(
            info_frame,
            font=("Arial", 12),
            wrap="word"
        )
        self.general_report_text.pack(fill="both", expand=True, padx=10, pady=10)

        # Кнопки действий
        button_frame = ctk.CTkFrame(info_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            button_frame,
            text="📊 Диаграммы",
            command=lambda: self._show_general_charts()
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="📝 Экспорт",
            command=lambda: self._export_general_report()
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="🔄 Обновить",
            command=self._refresh_general_report
        ).pack(side="right", padx=5)

    def refresh_data(self):
        """Обновить данные страницы"""
        self._load_events()

    def _show_overall_report(self):
        """Показать отчет по всем мероприятиям"""
        try:
            # Получить все мероприятия
            events = self.controller.get_all_events()
            if not events:
                messagebox.showinfo("Информация", "Нет мероприятий для отображения")
                return

            # Подготовить общую статистику
            total_events = len(events)
            total_guests = sum(event.guests_count for event in events)
            total_budget = sum(float(event.budget) for event in events)

            # Подсчитать общие расходы
            total_spent = 0
            for event in events:
                event_summary = self.controller.get_expense_report(event.id)
                if event_summary:
                    total_spent += float(event_summary.total_amount)

            # Подсчитать статусы мероприятий
            status_counts = {"планируется": 0, "идет": 0, "завершено": 0}
            for event in events:
                status_counts[event.status] += 1

            # Подсчитать среднюю стоимость мероприятия
            avg_cost = total_spent / total_events if total_events > 0 else 0

            # Показать общую информацию
            overall_info = (
                f"📊 ОБЩАЯ СТАТИСТИКА ПО МЕРОПРИЯТИЯМ\n\n"
                f"Всего мероприятий: {total_events}\n"
                f"Всего гостей: {total_guests}\n"
                f"Общий бюджет: {Formatters.format_currency(Decimal(str(total_budget)))}\n"
                f"Общие расходы: {Formatters.format_currency(Decimal(str(total_spent)))}\n"
                f"Остаток бюджета: {Formatters.format_currency(Decimal(str(total_budget - total_spent)))}\n"
                f"Средняя стоимость мероприятия: {Formatters.format_currency(Decimal(str(avg_cost)))}\n\n"
                f"Статусы мероприятий:\n"
                f"- Планируется: {status_counts['планируется']}\n"
                f"- Идет: {status_counts['идет']}\n"
                f"- Завершено: {status_counts['завершено']}\n\n"
                f"Эффективность бюджета: {Formatters.format_percentage((total_spent / total_budget) * 100) if total_budget > 0 else '0%'}"
            )

            # Создать окно с общей статистикой
            self._show_overall_stats_window(overall_info, events)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при формировании общего отчета: {str(e)}")

    def _show_overall_stats_window(self, info_text: str, events: List[Event]):
        """Показать окно с общей статистикой"""
        # Создать новое окно
        stats_window = ctk.CTkToplevel(self)
        stats_window.title("Общая статистика по мероприятиям")
        stats_window.geometry("800x600")
        stats_window.transient(self)
        stats_window.grab_set()

        # Добавить текстовую информацию
        info_frame = ctk.CTkFrame(stats_window)
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)

        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=("Arial", 12),
            justify="left"
        )
        info_label.pack(pady=10)

        # Добавить кнопки действий
        button_frame = ctk.CTkFrame(stats_window)
        button_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            button_frame,
            text="📊 Диаграммы",
            command=lambda: self._show_overall_charts(events)
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="📝 Экспорт",
            command=lambda: self._export_overall_report(events)
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="Закрыть",
            command=stats_window.destroy
        ).pack(side="right", padx=5)

    def _show_overall_charts(self, events: List[Event]):
        """Показать диаграммы для общего отчета"""
        try:
            # Создать новое окно для диаграмм
            chart_window = ctk.CTkToplevel(self)
            chart_window.title("Диаграммы по всем мероприятиям")
            chart_window.geometry("1000x700")
            chart_window.transient(self)
            chart_window.grab_set()

            # Фрейм для графиков
            figure_frame = ctk.CTkFrame(chart_window)
            figure_frame.pack(fill="both", expand=True, padx=10, pady=10)

            # Подготовить данные для графиков
            event_names = [event.name for event in events]
            budgets = [float(event.budget) for event in events]
            spent_amounts = []

            for event in events:
                summary = self.controller.get_expense_report(event.id)
                if summary:
                    spent_amounts.append(float(summary.total_amount))
                else:
                    spent_amounts.append(0.0)

            # Создать фигуру matplotlib
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
            fig.suptitle('Общая аналитика по мероприятиям', fontsize=16)

            # Диаграмма 1: Бюджеты мероприятий
            ax1.bar(event_names, budgets, alpha=0.7, label='Бюджет', color='skyblue')
            ax1.bar(event_names, spent_amounts, alpha=0.7, label='Потрачено', color='lightcoral')
            ax1.set_xlabel('Мероприятия')
            ax1.set_ylabel('Сумма, руб')
            ax1.set_title('Сравнение бюджетов и расходов')
            ax1.tick_params(axis='x', rotation=45)
            ax1.legend()

            # Диаграмма 2: Использование бюджета в %
            usage_percentages = []
            for i, event in enumerate(events):
                if budgets[i] > 0:
                    usage = (spent_amounts[i] / budgets[i]) * 100
                else:
                    usage = 0
                usage_percentages.append(usage)

            bars = ax2.bar(event_names, usage_percentages, alpha=0.7)
            ax2.set_xlabel('Мероприятия')
            ax2.set_ylabel('Использование бюджета, %')
            ax2.set_title('Процент использования бюджета')
            ax2.tick_params(axis='x', rotation=45)

            # Раскрасить столбцы в зависимости от уровня использования
            for i, bar in enumerate(bars):
                height = bar.get_height()
                if height > 100:
                    bar.set_color('red')
                elif height > 90:
                    bar.set_color('orange')
                elif height > 75:
                    bar.set_color('yellow')
                else:
                    bar.set_color('green')

            # Диаграмма 3: Распределение по статусам
            status_counts = {"планируется": 0, "идет": 0, "завершено": 0}
            for event in events:
                status_counts[event.status] += 1

            status_labels = list(status_counts.keys())
            status_values = list(status_counts.values())

            ax3.pie(status_values, labels=status_labels, autopct='%1.1f%%', startangle=90)
            ax3.set_title('Распределение мероприятий по статусам')

            # Диаграмма 4: Расходы по мероприятиям
            ax4.plot(event_names, spent_amounts, marker='o', linestyle='-', linewidth=2, markersize=6)
            ax4.set_xlabel('Мероприятия')
            ax4.set_ylabel('Потрачено, руб')
            ax4.set_title('Расходы по мероприятиям')
            ax4.tick_params(axis='x', rotation=45)
            ax4.grid(True)

            # Настроить макет
            plt.tight_layout()

            # Встроить график в Tkinter
            canvas = FigureCanvasTkAgg(fig, master=figure_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при построении диаграмм: {str(e)}")

    def _export_overall_report(self, events: List[Event]):
        """Экспорт общего отчета в файл"""
        try:
            # Запросить путь для сохранения файла
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv"), ("All files", "*.*")]
            )

            if not file_path:
                return  # Пользователь отменил операцию

            # Подготовить данные для экспорта
            export_data = []
            for event in events:
                summary = self.controller.get_expense_report(event.id)
                spent = summary.total_amount if summary else Decimal('0')

                export_data.append({
                    'Название мероприятия': event.name,
                    'Дата': Formatters.format_date(event.event_date),
                    'Статус': event.status,
                    'Гостей': event.guests_count,
                    'Бюджет': float(event.budget),
                    'Потрачено': float(spent),
                    'Остаток': float(event.budget - spent),
                    'Использовано (%)': round(float(spent / event.budget * 100), 2) if event.budget > 0 else 0
                })

            # Создать DataFrame и сохранить в файл
            df = pd.DataFrame(export_data)

            if file_path.endswith('.xlsx'):
                df.to_excel(file_path, index=False)
            elif file_path.endswith('.csv'):
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
            else:
                # По умолчанию сохраняем как Excel
                df.to_excel(file_path + '.xlsx', index=False)

            messagebox.showinfo("Успех", f"Отчет успешно экспортирован в {file_path}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при экспорте отчета: {str(e)}")

    def _create_widgets(self):
        """Создание виджетов страницы"""
        # Заголовок
        title_frame = ctk.CTkFrame(self)
        title_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            title_frame,
            text="📊 Отчеты и аналитика",
            font=("Arial", 18, "bold")
        ).pack(side="left", padx=10)

        # Выбор мероприятия
        selection_frame = ctk.CTkFrame(self)
        selection_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(selection_frame, text="Мероприятие:", font=("Arial", 12)).pack(side="left", padx=10)

        self.event_combo = ctk.CTkComboBox(
            selection_frame,
            values=[],
            width=300,
            font=("Arial", 12),
            command=self._on_event_selected
        )
        self.event_combo.pack(side="left", padx=10)

        ctk.CTkButton(
            selection_frame,
            text="🔄 Обновить",
            command=self._refresh_reports,
            width=100
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            selection_frame,
            text="📈 Общий отчет",
            command=self._show_overall_report,
            width=120
        ).pack(side="right", padx=5)

        # Вкладки отчетов
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Вкладка "Обзор"
        self.tabview.add("Обзор")
        self._create_overview_tab()

        # Вкладка "Расходы"
        self.tabview.add("Расходы")
        self._create_expenses_tab()

        # Вкладка "Анализ"
        self.tabview.add("Анализ")
        self._create_analysis_tab()

        # Вкладка "Общий отчет"
        self.tabview.add("Общий отчет")
        self._create_general_report_tab()

    def _create_general_report_tab(self):
        """Создание вкладки общего отчета"""
        # Информационная панель
        info_frame = ctk.CTkFrame(self.tabview.tab("Общий отчет"))
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Текстовое поле для отображения общей статистики
        self.general_report_text = ctk.CTkTextbox(
            info_frame,
            font=("Arial", 12),
            wrap="word"
        )
        self.general_report_text.pack(fill="both", expand=True, padx=10, pady=10)

        # Кнопки действий
        button_frame = ctk.CTkFrame(info_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            button_frame,
            text="📊 Диаграммы",
            command=lambda: self._show_general_charts()
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="📝 Экспорт",
            command=lambda: self._export_general_report()
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            button_frame,
            text="🔄 Обновить",
            command=self._refresh_general_report
        ).pack(side="right", padx=5)

    def _refresh_general_report(self):
        """Обновить общий отчет"""
        try:
            events = self.controller.get_all_events()
            if not events:
                self.general_report_text.delete("1.0", "end")
                self.general_report_text.insert("1.0", "Нет мероприятий для отображения")
                return

            # Подготовить общую статистику
            total_events = len(events)
            total_guests = sum(event.guests_count for event in events)
            total_budget = sum(float(event.budget) for event in events)

            # Подсчитать общие расходы
            total_spent = 0
            completed_events = 0
            planned_events = 0
            active_events = 0
            for event in events:
                event_summary = self.controller.get_expense_report(event.id)
                if event_summary:
                    total_spent += float(event_summary.total_amount)
                if event.status == "завершено":
                    completed_events += 1
                elif event.status == "планируется":
                    planned_events += 1
                elif event.status == "идет":
                    active_events += 1

            # Подсчитать статусы мероприятий
            status_counts = {"планируется": planned_events, "идет": active_events, "завершено": completed_events}

            # Подсчитать среднюю стоимость мероприятия
            avg_cost = total_spent / total_events if total_events > 0 else 0

            # Подсчитать эффективность бюджета
            budget_efficiency = (total_spent / total_budget * 100) if total_budget > 0 else 0

            # Формировать отчет
            report_content = (
                "📊 ОБЩИЙ ОТЧЕТ ПО ВСЕМ МЕРОПРИЯТИЯМ\n\n"
                f"Всего мероприятий: {total_events}\n"
                f"Завершенных мероприятий: {completed_events}\n"
                f"Всего гостей: {total_guests}\n"
                f"Общий бюджет: {Formatters.format_currency(Decimal(str(total_budget)))}\n"
                f"Общие расходы: {Formatters.format_currency(Decimal(str(total_spent)))}\n"
                f"Остаток бюджета: {Formatters.format_currency(Decimal(str(total_budget - total_spent)))}\n"
                f"Средняя стоимость мероприятия: {Formatters.format_currency(Decimal(str(avg_cost)))}\n"
                f"Эффективность бюджета: {Formatters.format_percentage(budget_efficiency)}\n\n"
                f"РАСПРЕДЕЛЕНИЕ ПО СТАТУСАМ:\n"
                f"- Планируется: {status_counts['планируется']}\n"
                f"- Идет: {status_counts['идет']}\n"
                f"- Завершено: {status_counts['завершено']}\n\n"
            )

            # Добавить информацию о каждом мероприятии
            report_content += "ДЕТАЛИ ПО МЕРОПРИЯТИЯМ:\n\n"
            for event in events:
                summary = self.controller.get_expense_report(event.id)
                spent = summary.total_amount if summary else Decimal('0')
                event_budget_utilization = (float(spent) / float(event.budget) * 100) if event.budget > 0 else 0

                report_content += (
                    f"• {event.name} ({Formatters.format_date(event.event_date)})\n"
                    f"  - Статус: {event.status}, Гостей: {event.guests_count}\n"
                    f"  - Бюджет: {Formatters.format_currency(event.budget)}, "
                    f"Потрачено: {Formatters.format_currency(spent)}, "
                    f"Использовано: {Formatters.format_percentage(event_budget_utilization)}\n\n"
                )

            # Обновить текстовое поле
            self.general_report_text.delete("1.0", "end")
            self.general_report_text.insert("1.0", report_content)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при обновлении общего отчета: {str(e)}")

    def _update_analysis_tab(self, summary: EventSummary):
        """Обновление вкладки анализа"""
        # Очистить предыдущий график
        for widget in self.figure_frame.winfo_children():
            widget.destroy()

        if not summary.categories_summary:
            no_data_label = ctk.CTkLabel(
                self.figure_frame,
                text="Нет данных для построения графиков",
                font=("Arial", 14)
            )
            no_data_label.pack(expand=True)
            return

        # Подготовить данные для графиков
        categories = [item.category_name for item in summary.categories_summary]
        actual_values = [float(item.actual_amount) for item in summary.categories_summary]
        planned_values = [float(item.planned_amount) for item in summary.categories_summary]

        # Создать фигуру matplotlib
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        fig.suptitle(f'Анализ расходов - {summary.event.name}', fontsize=14)

        # График 1: Фактические расходы по категориям
        wedges, texts, autotexts = ax1.pie(
            actual_values,
            labels=categories,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 8}
        )
        ax1.set_title('Фактические расходы по категориям')

        # График 2: Сравнение план/факт
        x = range(len(categories))
        width = 0.4
        ax2.bar([i - width / 2 for i in x], planned_values, width, label='План', alpha=0.7)
        ax2.bar([i + width / 2 for i in x], actual_values, width, label='Факт', alpha=0.7)
        ax2.set_xlabel('Категории')
        ax2.set_ylabel('Сумма, руб')
        ax2.set_title('Сравнение плановых и фактических расходов')
        ax2.set_xticks(x)
        ax2.set_xticklabels(categories, rotation=45, ha='right', fontsize=8)
        ax2.legend()

        # Настроить макет, чтобы всё помещалось
        plt.tight_layout()

        # Встроить график в Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.figure_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def _show_general_charts(self):
        """Показать диаграммы для общего отчета"""
        events = self.controller.get_all_events()
        if events:
            self._show_overall_charts(events)

    def _export_general_report(self):
        """Экспорт общего отчета"""
        events = self.controller.get_all_events()
        if events:
            self._export_overall_report(events)
