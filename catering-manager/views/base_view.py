"""
Базовые классы для всех view-страниц
"""

import tkinter as tk
import customtkinter as ctk
from typing import Optional

from controllers import CateringController


class BasePage(ctk.CTkFrame):
    """Базовый класс для всех страниц"""

    def __init__(self, parent, controller: CateringController, title: str = ""):
        super().__init__(parent)
        self.controller = controller
        self.title = title

        self._create_widgets()

    def _create_widgets(self):
        """Создание виджетов страницы (должен быть переопределен)"""
        pass

    def refresh_data(self):
        """Обновить данные страницы (должен быть переопределен)"""
        pass
