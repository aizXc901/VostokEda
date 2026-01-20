"""
Точка входа приложения
"""

import sys
import logging
from pathlib import Path

# Добавляем корневую директорию в путь Python
sys.path.insert(0, str(Path(__file__).parent))

import customtkinter as ctk
from config import Config
from controllers import CateringController
from views.main_window import MainWindow

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),  # <--- Теперь это атрибут класса
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),  # <--- Теперь это атрибут класса
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Основная функция приложения"""
    try:
        logger.info(f"Запуск {Config.APP_NAME} v{Config.APP_VERSION}")  # <--- Теперь это атрибуты класса

        # Создаем контроллер
        controller = CateringController()

        # Проверяем базу данных
        tables_exist = controller.db.check_tables_exist()
        logger.info(f"Таблицы в БД: {tables_exist}")

        # Создаем главное окно
        app = MainWindow(controller)

        # Запускаем приложение
        logger.info("Приложение запущено успешно")
        app.mainloop()

    except Exception as e:
        logger.error(f"Ошибка запуска приложения: {e}")
        # Показываем сообщение об ошибке
        error_window = ctk.CTk()
        error_window.title("Ошибка запуска")
        error_window.geometry("400x200")

        label = ctk.CTkLabel(
            error_window,
            text=f"Ошибка запуска приложения:\n{str(e)}",
            font=("Arial", 12),
            wraplength=350
        )
        label.pack(pady=20)

        button = ctk.CTkButton(
            error_window,
            text="Выход",
            command=error_window.destroy,
            width=100
        )
        button.pack(pady=10)

        error_window.mainloop()
        sys.exit(1)

if __name__ == "__main__":
    main()
