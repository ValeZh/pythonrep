import sqlite3
from functools import wraps


def db_connection(func):
    """
    Декоратор для установки соединения с базой данных и его закрытия после выполнения функции.

    Args:
        func (function): Функция базы данных, которая будет выполнена.

    Returns:
        function: Вложенная функция-обертка, которая обеспечивает соединение и закрытие.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        """
        Вложенная функция-обертка, обеспечивающая соединение и закрытие.

        Args:
            *args: Позиционные аргументы, переданные в функцию.
            **kwargs: Именованные аргументы, переданные в функцию.

        Returns:
            any: Результат выполнения оригинальной функции.
        """
        # Устанавливаем соединение с базой данных
        conn = sqlite3.connect('bank.db')
        # Создаем объект курсора
        c = conn.cursor()
        result = None
        try:
            # Вызываем оригинальную функцию, передавая ей курсор и все переданные аргументы
            result = func(c, *args, **kwargs)
        except Exception as e:
            # Обрабатываем ошибки и логируем их
            print(f"Error: {str(e)}")
        finally:
            conn.commit()
            conn.close()
            return result
    # Возвращаем вложенную функцию-обертку в качестве декоратора
    return wrapper
