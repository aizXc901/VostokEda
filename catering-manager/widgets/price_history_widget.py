"""
Виджет истории изменения цен
"""

import tkinter as tk
import customtkinter as ctk
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Dict, Optional
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib

matplotlib.use('TkAgg')

from models import SupplierPrice, Nomenclature, Supplier
from controllers import CateringController
from utils.formatters import Formatters


class PriceHistoryWidget(ctk.CTkFrame):
    """Виджет для отображения истории цен"""

    def __init__(self, parent, controller: CateringController, **kwargs):
        super().__init__(parent, **kwargs)

        self.controller = controller
        self.current_nomenclature: Optional[Nomenclature] = None
        self.current_supplier: Optional[Supplier] = None
        self.price_history: List[SupplierPrice] = []

        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов"""
        # Заголовок
        self.title_label = ctk.CTkLabel(
            self,
            text="📈 История изменения цен",
            font=("Arial", 14, "bold")
        )
        self.title_label.pack(anchor="w", padx=10, pady=(10, 5))

        # Панель выбора
        selection_frame = ctk.CTkFrame(self)
        selection_frame.pack(fill="x", padx=10, pady=5)

        # Выбор номенклатуры
        ctk.CTkLabel(selection_frame, text="Позиция:", font=("Arial", 11)).pack(side="left", padx=(0, 5))

        self.nomenclature_combo = ctk.CTkComboBox(
            selection_frame,
            values=[],
            width=200,
            command=self._on_nomenclature_select
        )
        self.nomenclature_combo.pack(side="left", padx=(0, 20))

        # Выбор поставщика
        ctk.CTkLabel(selection_frame, text="Поставщик:", font=("Arial", 11)).pack(side="left", padx=(0, 5))

        self.supplier_combo = ctk.CTkComboBox(
            selection_frame,
            values=["Все поставщики"],
            width=200,
            command=self._on_supplier_select
        )
        self.supplier_combo.pack(side="left")

        # Кнопка обновления
        ctk.CTkButton(
            selection_frame,
            text="Обновить",
            width=80,
            command=self._load_price_history
        ).pack(side="right", padx=10)

        # Фрейм для графика
        self.chart_frame = ctk.CTkFrame(self)
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Заглушка для графика
        self.placeholder_label = ctk.CTkLabel(
            self.chart_frame,
            text="Выберите позицию для отображения истории цен",
            font=("Arial", 12)
        )
        self.placeholder_label.pack(expand=True)

        # Таблица с ценами
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Treeview для цен
        tree_frame = ctk.CTkFrame(table_frame)
        tree_frame.pack(fill="both", expand=True)

        tree_scroll_y = ctk.CTkScrollbar(tree_frame)
        tree_scroll_y.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            tree_frame,
            yscrollcommand=tree_scroll_y.set,
            selectmode="browse",
            height=5
        )

        tree_scroll_y.configure(command=self.tree.yview)

        # Колонки
        self.tree['columns'] = ('supplier', 'start_date', 'end_date', 'price', 'min_quantity')
        self.tree.column('#0', width=0, stretch=tk.NO)
        self.tree.column('supplier', width=150, anchor=tk.W)
        self.tree.column('start_date', width=100, anchor=tk.CENTER)
        self.tree.column('end_date', width=100, anchor=tk.CENTER)
        self.tree.column('price', width=100, anchor=tk.RIGHT)
        self.tree.column('min_quantity', width=80, anchor=tk.CENTER)

        # Заголовки
        self.tree.heading('supplier', text='Поставщик')
        self.tree.heading('start_date', text='Дата начала')
        self.tree.heading('end_date', text='Дата окончания')
        self.tree.heading('price', text='Цена, руб')
        self.tree.heading('min_quantity', text='Мин. кол-во')

        self.tree.pack(fill="both", expand=True)

        # Загружаем данные
        self._load_data()

    def _load_data(self):
        """Загрузить данные для выбора"""
        try:
            # Загружаем номенклатуру
            nomenclatures = self.controller.get_all_nomenclatures()
            nomenclature_names = [f"{n.name} ({n.unit})" for n in nomenclatures if n.is_active]
            self.nomenclature_combo.configure(values=nomenclature_names)

            # Загружаем поставщиков
            suppliers = self.controller.get_all_suppliers()
            supplier_names = ["Все поставщики"] + [s.name for s in suppliers if s.is_active]
            self.supplier_combo.configure(values=supplier_names)
            self.supplier_combo.set("Все поставщики")

        except Exception as e:
            print(f"Ошибка загрузки данных: {e}")

    def _on_nomenclature_select(self, choice):
        """Обработка выбора номенклатуры"""
        if not choice:
            return

        # Находим выбранную номенклатуру
        nomenclatures = self.controller.get_all_nomenclatures()
        for nom in nomenclatures:
            display_name = f"{nom.name} ({nom.unit})"
            if display_name == choice:
                self.current_nomenclature = nom
                self._load_price_history()
                break

    def _on_supplier_select(self, choice):
        """Обработка выбора поставщика"""
        if choice == "Все поставщики":
            self.current_supplier = None
        else:
            suppliers = self.controller.get_all_suppliers()
            for sup in suppliers:
                if sup.name == choice:
                    self.current_supplier = sup
                    break

        self._load_price_history()

    def _load_price_history(self):
        """Загрузить историю цен"""
        if not self.current_nomenclature:
            return

        try:
            # Здесь должна быть логика загрузки истории цен из БД
            # Пока создаем тестовые данные

            self.price_history = []

            # Очищаем таблицу
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Обновляем график
            self._update_chart()

            # Обновляем заголовок
            if self.current_nomenclature:
                title = f"История цен: {self.current_nomenclature.name}"
                if self.current_supplier:
                    title += f" - {self.current_supplier.name}"
                self.title_label.configure(text=title)

        except Exception as e:
            print(f"Ошибка загрузки истории цен: {e}")

    def _update_chart(self):
        """Обновить график цен"""
        if not self.price_history:
            # Очищаем график
            for widget in self.chart_frame.winfo_children():
                widget.destroy()

            self.placeholder_label = ctk.CTkLabel(
                self.chart_frame,
                text="Нет данных для отображения графика",
                font=("Arial", 12)
            )
            self.placeholder_label.pack(expand=True)
            return

        try:
            # Очищаем фрейм
            for widget in self.chart_frame.winfo_children():
                widget.destroy()

            # Группируем цены по поставщикам
            suppliers_data = {}
            for price in self.price_history:
                supplier_name = price.supplier.name if price.supplier else "Неизвестно"
                if supplier_name not in suppliers_data:
                    suppliers_data[supplier_name] = []

                suppliers_data[supplier_name].append({
                    'date': price.start_date,
                    'price': float(price.price)
                })

            # Создаем график
            fig, ax = plt.subplots(figsize=(8, 4))

            colors = plt.cm.tab10.colors
            color_idx = 0

            for supplier_name, prices in suppliers_data.items():
                if not prices:
                    continue

                # Сортируем по дате
                prices.sort(key=lambda x: x['date'])

                dates = [p['date'] for p in prices]
                price_values = [p['price'] for p in prices]

                # Отображаем на графике
                ax.plot(
                    dates,
                    price_values,
                    marker='o',
                    label=supplier_name,
                    color=colors[color_idx % len(colors)],
                    linewidth=2
                )

                color_idx += 1

            # Настраиваем график
            ax.set_xlabel('Дата')
            ax.set_ylabel('Цена, руб')
            ax.set_title('Динамика изменения цен')
            ax.legend()
            ax.grid(True, alpha=0.3)

            # Форматируем даты
            fig.autofmt_xdate()

            # Встраиваем в Tkinter
            canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)

        except Exception as e:
            # В случае ошибки показываем сообщение
            for widget in self.chart_frame.winfo_children():
                widget.destroy()

            error_label = ctk.CTkLabel(
                self.chart_frame,
                text=f"Ошибка при создании графика: {str(e)}",
                font=("Arial", 10),
                text_color="red"
            )
            error_label.pack(expand=True)
