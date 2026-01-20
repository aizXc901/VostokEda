"""
Отчеты и аналитика
"""

import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib

# Используем TkAgg для совместимости с Tkinter
matplotlib.use('TkAgg')

from models import Event, EventSummary, ExpenseReportItem
from controllers import CateringController
from utils.formatters import Formatters
from utils.export_utils import ExportUtils
from .base_view import BasePage  # <--- ИСПРАВЛЕНО


class ReportsPage(BasePage):
    """Страница отчетов и аналитики"""

    def __init__(self, parent, controller):
        super().__init__(parent, controller, "Отчеты и аналитика")
        self.events: List[Event] = []
        self.current_report: Optional[EventSummary] = None
        self._create_widgets()
        self.refresh_data()

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

        # Панель фильтров
        filter_frame = ctk.CTkFrame(self)
        filter_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Выбор мероприятия
        ctk.CTkLabel(filter_frame, text="Мероприятие:", font=("Arial", 12)).pack(side="left", padx=10)

        self.event_combo = ctk.CTkComboBox(
            filter_frame,
            values=[],
            width=300,
            command=self._generate_report
        )
        self.event_combo.pack(side="left", padx=10)

        # Кнопки
        ctk.CTkButton(
            filter_frame,
            text="📋 Сформировать отчет",
            command=self._generate_report,
            width=150
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            filter_frame,
            text="📤 Экспорт в Excel",
            command=self._export_to_excel,
            width=150
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            filter_frame,
            text="🔄 Обновить",
            command=self.refresh_data,
            width=150
        ).pack(side="right", padx=10)

        # Основной контент
        content_frame = ctk.CTkFrame(self)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Левая панель - сводка
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        ctk.CTkLabel(
            left_frame,
            text="Сводка по мероприятию",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=(0, 10))

        # Информация о мероприятии
        self.info_frame = ctk.CTkFrame(left_frame)
        self.info_frame.pack(fill="x", padx=10, pady=10)

        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="Выберите мероприятие для отображения отчета",
            font=("Arial", 12),
            wraplength=350
        )
        self.info_label.pack(pady=20)

        # Таблица расходов по категориям
        table_frame = ctk.CTkFrame(left_frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Treeview для категорий
        tree_frame = ctk.CTkFrame(table_frame)
        tree_frame.pack(fill="both", expand=True)

        tree_scroll_y = ctk.CTkScrollbar(tree_frame)
        tree_scroll_y.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=tree_scroll_y.set,
            selectmode="browse",
            height=8
        )

        tree_scroll_y.configure(command=self.tree.yview)

        # Колонки
        self.tree['columns'] = ('category', 'planned', 'actual', 'deviation', 'percentage')
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('category', width=150, anchor=tk.W)
        self.tree.column('planned', width=100, anchor=tk.E)
        self.tree.column('actual', width=100, anchor=tk.E)
        self.tree.column('deviation', width=100, anchor=tk.E)
        self.tree.column('percentage', width=80, anchor=tk.CENTER)

        # Заголовки
        self.tree.heading('category', text='Категория')
        self.tree.heading('planned', text='План, руб')
        self.tree.heading('actual', text='Факт, руб')
        self.tree.heading('deviation', text='Отклонение')
        self.tree.heading('percentage', text='%')

        self.tree.pack(fill="both", expand=True)

        # Правая панель - диаграммы
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))

        ctk.CTkLabel(
            right_frame,
            text="Визуализация расходов",
            font=("Arial", 14, "bold")
        ).pack(anchor="w", padx=10, pady=(0, 10))

        # Фрейм для диаграмм
        self.chart_frame = ctk.CTkFrame(right_frame)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Заглушка для диаграммы
        self.chart_label = ctk.CTkLabel(
            self.chart_frame,
            text="Диаграмма будет отображена после формирования отчета",
            font=("Arial", 12),
            wraplength=350
        )
        self.chart_label.pack(expand=True)

    def refresh_data(self):
        """Обновить данные"""
        try:
            # Загружаем мероприятия
            self.events = self.controller.get_all_events()

            # Обновляем комбобокс
            event_names = [f"{e.name} ({Formatters.format_date(e.event_date)})" for e in self.events]
            self.event_combo.configure(values=event_names)

            # Выбираем текущее мероприятие если есть
            if self.controller.current_event:
                current_display = f"{self.controller.current_event.name} ({Formatters.format_date(self.controller.current_event.event_date)})"
                if current_display in event_names:
                    self.event_combo.set(current_display)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")

    def _generate_report(self, event=None):
        """Сформировать отчет для выбранного мероприятия"""
        selected_display = self.event_combo.get()
        if not selected_display:
            messagebox.showwarning("Внимание", "Выберите мероприятие")
            return

        try:
            # Находим выбранное мероприятие
            selected_event = None
            for event in self.events:
                event_display = f"{event.name} ({Formatters.format_date(event.event_date)})"
                if event_display == selected_display:
                    selected_event = event
                    break

            if not selected_event:
                messagebox.showerror("Ошибка", "Мероприятие не найдено")
                return

            # Получаем отчет через контроллер
            self.current_report = self.controller.get_expense_report(selected_event.id)

            if not self.current_report:
                messagebox.showinfo("Информация", "Нет данных для отчета")
                return

            # Обновляем информацию о мероприятии
            self._update_event_info()

            # Обновляем таблицу категорий
            self._update_categories_table()

            # Обновляем диаграмму
            self._update_chart()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сформировать отчет: {str(e)}")

    def _update_event_info(self):
        """Обновить информацию о мероприятии"""
        if not self.current_report:
            return

        event = self.current_report.event
        info_text = (
            f"Мероприятие: {event.name}\n"
            f"Дата проведения: {Formatters.format_date(event.event_date)}\n"
            f"Общий бюджет: {Formatters.format_currency(event.budget)}\n"
            f"Общие расходы: {Formatters.format_currency(self.current_report.total_amount)}\n"
            f"Использовано бюджета: {Formatters.format_percentage(self.current_report.budget_utilization)}\n"
            f"Количество заказов: {self.current_report.total_orders}"
        )

        # Выделение красным если превышен бюджет
        if self.current_report.budget_utilization > 100:
            info_text += "\n\n⚠️ ПРЕВЫШЕНИЕ БЮДЖЕТА!"

        self.info_label.configure(text=info_text)

    def _update_categories_table(self):
        """Обновить таблицу категорий"""
        if not self.current_report:
            return

        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Заполняем таблицу
        for item in self.current_report.categories_summary:
            deviation = item.actual_amount - item.planned_amount
            deviation_str = Formatters.format_currency(deviation, show_symbol=False)

            # Цвет для отклонения
            tags = ()
            if deviation > Decimal('0'):
                tags = ('over',)
            elif deviation < Decimal('0'):
                tags = ('under',)

            self.tree.insert(
                '',
                tk.END,
                values=(
                    item.category_name,
                    Formatters.format_currency(item.planned_amount, show_symbol=False),
                    Formatters.format_currency(item.actual_amount, show_symbol=False),
                    deviation_str,
                    Formatters.format_percentage(item.percentage, decimals=0)
                ),
                tags=tags
            )

        # Настраиваем цвета
        self.tree.tag_configure('over', foreground='red')
        self.tree.tag_configure('under', foreground='green')

    def _update_chart(self):
        """Обновить диаграмму"""
        if not self.current_report or not self.current_report.categories_summary:
            return

        try:
            # Очищаем фрейм
            for widget in self.chart_frame.winfo_children():
                widget.destroy()

            # Создаем фигуру
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

            # Подготавливаем данные
            categories = []
            amounts = []
            colors = []

            for item in self.current_report.categories_summary:
                if item.actual_amount > Decimal('0'):
                    categories.append(item.category_name)
                    amounts.append(float(item.actual_amount))
                    # Используем цвета из конфига или генерируем
                    colors.append(plt.cm.tab20c(len(categories) % 20))

            # Круговая диаграмма
            if amounts:
                ax1.pie(
                    amounts,
                    labels=categories,
                    colors=colors,
                    autopct='%1.1f%%',
                    startangle=90
                )
                ax1.set_title('Распределение расходов по категориям')
                ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            else:
                ax1.text(0.5, 0.5, 'Нет данных',
                         horizontalalignment='center',
                         verticalalignment='center',
                         transform=ax1.transAxes)
                ax1.set_title('Нет данных для диаграммы')

            # Столбчатая диаграмма (план vs факт)
            if self.current_report.categories_summary:
                categories = [item.category_name for item in self.current_report.categories_summary]
                planned = [float(item.planned_amount) for item in self.current_report.categories_summary]
                actual = [float(item.actual_amount) for item in self.current_report.categories_summary]

                x = range(len(categories))
                width = 0.35

                bars1 = ax2.bar([i - width / 2 for i in x], planned, width, label='План', color='skyblue')
                bars2 = ax2.bar([i + width / 2 for i in x], actual, width, label='Факт', color='lightcoral')

                ax2.set_xlabel('Категории')
                ax2.set_ylabel('Сумма, руб')
                ax2.set_title('План vs Факт по категориям')
                ax2.set_xticks(x)
                ax2.set_xticklabels(categories, rotation=45, ha='right')
                ax2.legend()

                # Добавляем подписи значений
                def autolabel(bars):
                    for bar in bars:
                        height = bar.get_height()
                        if height > 0:
                            ax2.annotate(f'{height:,.0f}',
                                         xy=(bar.get_x() + bar.get_width() / 2, height),
                                         xytext=(0, 3),  # 3 points vertical offset
                                         textcoords="offset points",
                                         ha='center', va='bottom',
                                         fontsize=8)

                autolabel(bars1)
                autolabel(bars2)

                # Настраиваем layout
                plt.tight_layout()

            # Встраиваем диаграмму в Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

            # Кнопка сохранения диаграммы
            save_button = ctk.CTkButton(
                self.chart_frame,
                text="💾 Сохранить диаграмму",
                command=lambda: self._save_chart(fig),
                width=150
            )
            save_button.pack(pady=5)

        except Exception as e:
            # В случае ошибки показываем сообщение
            for widget in self.chart_frame.winfo_children():
                widget.destroy()

            error_label = ctk.CTkLabel(
                self.chart_frame,
                text=f"Ошибка при создании диаграммы: {str(e)}",
                font=("Arial", 10),
                text_color="red"
            )
            error_label.pack(expand=True)

    def _save_chart(self, fig):
        """Сохранить диаграмму как изображение"""
        try:
            from tkinter import filedialog
            import os

            # Предлагаем выбрать место сохранения
            filename = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")],
                initialfile=f"отчет_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            )

            if filename:
                fig.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Успех", f"Диаграмма сохранена:\n{filename}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить диаграмму: {str(e)}")

    def _export_to_excel(self):
        """Экспортировать отчет в Excel"""
        if not self.current_report:
            messagebox.showwarning("Внимание", "Сначала сформируйте отчет")
            return

        try:
            from tkinter import filedialog
            import os

            # Предлагаем выбрать место сохранения
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=f"отчет_{self.current_report.event.name}_{datetime.now().strftime('%Y%m%d')}.xlsx"
            )

            if filename:
                success = ExportUtils.export_expense_report_to_excel(self.current_report, filename)

                if success:
                    messagebox.showinfo("Успех", f"Отчет экспортирован:\n{filename}")
                else:
                    messagebox.showerror("Ошибка", "Не удалось экспортировать отчет")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")
