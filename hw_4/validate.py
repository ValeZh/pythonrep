import re
from datetime import datetime


# Валидация поля user_full_name
def validate_user_full_name(user_full_name):
    # Удаляем все символы, не являющиеся буквами
    user_full_name = re.sub(r'[^a-zA-Z\s]', '', user_full_name)
    # Разделяем имя и фамилию по любым пробельным символам
    name, surname = user_full_name.strip().split(None, 1)
    return name, surname


# Валидация полей с строгим набором значений
def validate_field_value(field, value, allowed_values):
    if value not in allowed_values:
        raise ValueError("error: not allowed value {} for field {}!".format(value, field))


def validate_account_number(account_number):
    # Замена специальных символов на тире
    account_number = re.sub(r'[#%_?&]', '-', account_number)

    # Проверка на количество символов
    if len(account_number) <18:
        raise ValueError("error: too little")
    if len(account_number) > 18:
        raise ValueError("error: many chars")

    # Проверка формата
    if not account_number.startswith("ID--"):
        raise ValueError("error: wrong format")

    # Проверка на наличие нужного паттерна
    if not re.match(r'ID--[a-zA-Z]{1,3}-\d+-', account_number):
        raise ValueError("an error: broken ID")

    return account_number


# Функция для проверки и добавления времени транзакции
def add_transaction_time(transaction_time):
    if not transaction_time:
        transaction_time = datetime.now()
    return transaction_time


