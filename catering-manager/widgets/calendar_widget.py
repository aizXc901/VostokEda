"""
Кастомный виджет календаря
"""

import tkinter as tk
import customtkinter as ctk
from datetime import datetime, date, timedelta
from typing import Optional, Callable, Dict, List
import calendar


class CalendarWidget(ctk.CTkFrame):
    """Виджет календаря для выбора дат"""

    def __init__(self, parent, on_date_select: Optional[Callable] = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.on_date_select = on_date_select
        self.current_date = date.today()
        self.selected_date: Optional[date] = None
        self.marked_dates: Dict[date, str] = {}  # дата -> цвет

        self._create_widgets()
        self._update_calendar()

    def _create_widgets(self):
        """Создание виджетов календаря"""
        # Заголовок с навигацией
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=5, pady=5)

        # Кнопка предыдущего месяца
        self.prev_button = ctk.CTkButton(
            header_frame,
            text="◀",
            width=30,
            command=self._prev_month
        )
        self.prev_button.pack(side="left", padx=2)

        # Отображение месяца и года
        self.month_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=("Arial", 14, "bold")
        )
        self.month_label.pack(side="left", expand=True)

        # Кнопка следующего месяца
        self.next_button = ctk.CTkButton(
            header_frame,
            text="▶",
            width=30,
            command=self._next_month
        )
        self.next_button.pack(side="right", padx=2)

        # Кнопка сегодня
        ctk.CTkButton(
            header_frame,
            text="Сегодня",
            width=70,
            command=self._go_today
        ).pack(side="right", padx=5)

        # Дни недели
        days_frame = ctk.CTkFrame(self)
        days_frame.pack(fill="x", padx=5, pady=2)

        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for day in days:
            label = ctk.CTkLabel(
                days_frame,
                text=day,
                width=30,
                font=("Arial", 10, "bold")
            )
            label.pack(side="left", expand=True)

        # Фрейм для дней
        self.days_frame = ctk.CTkFrame(self)
        self.days_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Создаем кнопки для дней
        self.day_buttons: List[ctk.CTkButton] = []
        for row in range(6):  # Максимум 6 недель в месяце
            for col in range(7):  # 7 дней в неделе
                btn = ctk.CTkButton(
                    self.days_frame,
                    text="",
                    width=30,
                    height=30,
                    font=("Arial", 10),
                    fg_color="transparent",
                    command=lambda r=row, c=col: self._on_day_click(r, c)
                )
                btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
                self.day_buttons.append(btn)

            # Настраиваем пропорции строк и столбцов
            self.days_frame.grid_rowconfigure(row, weight=1)
            self.days_frame.grid_columnconfigure(col, weight=1)

    def _update_calendar(self):
        """Обновить отображение календаря"""
        # Обновляем заголовок
        month_names = [
            "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
            "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
        ]

        month_name = month_names[self.current_date.month - 1]
        year = self.current_date.year
        self.month_label.configure(text=f"{month_name} {year}")

        # Получаем календарь для текущего месяца
        cal = calendar.monthcalendar(year, self.current_date.month)

        # Сбрасываем все кнопки
        for btn in self.day_buttons:
            btn.configure(text="", fg_color="transparent", state="normal")

        # Заполняем календарь
        today = date.today()
        button_index = 0

        for week in cal:
            for day in week:
                if day == 0:
                    # Пустой день
                    self.day_buttons[button_index].configure(state="disabled")
                else:
                    day_date = date(year, self.current_date.month, day)

                    # Устанавливаем текст
                    self.day_buttons[button_index].configure(text=str(day))

                    # Проверяем выделенные даты
                    if self.selected_date and day_date == self.selected_date:
                        self.day_buttons[button_index].configure(fg_color="#4ECDC4")
                    elif day_date == today:
                        self.day_buttons[button_index].configure(fg_color="#FFD166")
                    elif day_date in self.marked_dates:
                        color = self.marked_dates[day_date]
                        self.day_buttons[button_index].configure(fg_color=color)

                    # Делаем прошедшие даты менее яркими
                    if day_date < today:
                        self.day_buttons[button_index].configure(text_color="gray")

                button_index += 1

    def _prev_month(self):
        """Перейти к предыдущему месяцу"""
        if self.current_date.month == 1:
            self.current_date = date(self.current_date.year - 1, 12, 1)
        else:
            self.current_date = date(self.current_date.year, self.current_date.month - 1, 1)

        self._update_calendar()

    def _next_month(self):
        """Перейти к следующему месяцу"""
        if self.current_date.month == 12:
            self.current_date = date(self.current_date.year + 1, 1, 1)
        else:
            self.current_date = date(self.current_date.year, self.current_date.month + 1, 1)

        self._update_calendar()

    def _go_today(self):
        """Перейти к сегодняшней дате"""
        self.current_date = date.today()
        self._update_calendar()

    def _on_day_click(self, row: int, col: int):
        """Обработка клика по дню"""
        index = row * 7 + col
        day_text = self.day_buttons[index].cget("text")

        if day_text and day_text != "":
            day = int(day_text)
            selected_date = date(self.current_date.year, self.current_date.month, day)

            # Обновляем выбранную дату
            self.selected_date = selected_date

            # Обновляем отображение
            self._update_calendar()

            # Вызываем callback если есть
            if self.on_date_select:
                self.on_date_select(selected_date)

    def get_selected_date(self) -> Optional[date]:
        """Получить выбранную дату"""
        return self.selected_date

    def set_selected_date(self, new_date: date):
        """Установить выбранную дату"""
        self.selected_date = new_date

        # Переходим к месяцу выбранной даты
        self.current_date = date(new_date.year, new_date.month, 1)
        self._update_calendar()

    def mark_date(self, date_to_mark: date, color: str = "#FF6B6B"):
        """Пометить дату цветом"""
        self.marked_dates[date_to_mark] = color
        self._update_calendar()

    def clear_marks(self):
        """Очистить все пометки"""
        self.marked_dates.clear()
        self._update_calendar()
