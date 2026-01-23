"""
Точка входа приложения
"""

import sys
import logging
from pathlib import Path
import os
import atexit

# Добавляем корневую директорию в путь Python
sys.path.insert(0, str(Path(__file__).parent))

import customtkinter as ctk
from config import Config
from controllers import CateringController
from views.main_window import MainWindow

# Файл блокировки для предотвращения дублирования запусков
LOCK_FILE = "catering_manager.lock"

def create_lock():
    """Создание файла блокировки"""
    if os.path.exists(LOCK_FILE):
        # Проверяем, что процесс с PID в файле еще существует
        try:
            with open(LOCK_FILE, 'r') as f:
                pid = int(f.read().strip())
                if os.path.exists(f"/proc/{pid}"):
                    raise RuntimeError("Приложение уже запущено!")
        except (ValueError, OSError):
            # Если не удалось прочитать или проверить PID, удаляем файл и создаем новый
            if os.path.exists(LOCK_FILE):
                os.remove(LOCK_FILE)

    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))

def remove_lock():
    """Удаление файла блокировки"""
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Основная функция приложения"""
    try:
        logger.info(f"Запуск {Config.APP_NAME} v{Config.APP_VERSION}")

        # Создаем контроллер
        controller = CateringController()

        # Проверяем базу данных
        tables_exist = controller.db.check_tables_exist()
        logger.info(f"Таблицы в БД: {tables_exist}")

        # Проверяем, не существует ли уже экземпляр окна
        if MainWindow._instance is not None:
            # Попробуем сфокусироваться на существующем окне
            try:
                MainWindow._instance.focus()
                MainWindow._instance.lift()
                MainWindow._instance.deiconify()
                logger.info("Фокусировка на существующем экземпляре")
                return
            except Exception as e:
                logger.error(f"Ошибка фокусировки на существующее окно: {e}")

        # Создаем файл блокировки
        create_lock()
        atexit.register(remove_lock)

        # Создаем главное окно
        app = MainWindow(controller)

        # Запускаем приложение
        logger.info("Приложение запущено успешно")
        app.mainloop()

    except Exception as e:
        logger.error(f"Ошибка запуска приложения: {e}")

        # Проверяем, не существует ли уже экземпляр окна
        if MainWindow._instance is not None:
            # Если окно уже существует, просто фокусируемся на нем
            try:
                MainWindow._instance.focus()
                MainWindow._instance.lift()
                MainWindow._instance.deiconify()
                logger.warning("Попытка создания второго экземпляра окна")
                return
            except Exception as e:
                logger.error(f"Ошибка фокусировки на существующее окно: {e}")
        else:
            # Создаем окно ошибки только если нет активного окна
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
                command=lambda: [error_window.destroy(), sys.exit(1)],
                width=100
            )
            button.pack(pady=10)

            error_window.mainloop()

        sys.exit(1)

if __name__ == "__main__":
    main()
