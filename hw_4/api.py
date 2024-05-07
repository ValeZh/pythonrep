import sqlite3
import requests
import csv
import validate


def db_connection(func):
    """
    Декоратор для установки соединения с базой данных и его закрытия после выполнения функции.

    Args:
        func (function): Функция базы данных, которая будет выполнена.

    Returns:
        function: Вложенная функция-обертка, которая обеспечивает соединение и закрытие.
    """
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
        try:
            # Вызываем оригинальную функцию, передавая ей курсор и все переданные аргументы
            result = func(c, *args, **kwargs)
        except Exception as e:
            # Обрабатываем ошибки и логируем их
            print(f"Error: {str(e)}")
            result = None
        finally:
            # Фиксируем изменения в базе данных и закрываем соединение
            conn.commit()
            conn.close()
            # Возвращаем результат выполнения оригинальной функции
            return result
    # Возвращаем вложенную функцию-обертку в качестве декоратора
    return wrapper


# получает дикт из валют и их значений относительно доллара
def get_curency_data():
    api_key = 'fca_live_bYExvWei85B5olF2iitYB6HunpYb8RYaZAw29iWt'
    url = f'https://api.freecurrencyapi.com/v1/latest?apikey={api_key}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print("data_get successfully")
        print(data['data'])
        return data['data']
    else:
        print("data_get failure")
        return None


# читает цсв файл переобразовывая в дикт
def read_csv_to_dict(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        data_dict = [row for row in reader]
    return data_dict


# преобразует лист диктов в дикт листов
def merge_dicts(dict_list):
    merged_dict = {}
    for d in dict_list:
        for key, value in d.items():
            # Если ключ уже есть в объединенном словаре, добавляем значение в список
            if key in merged_dict:
                merged_dict[key].append(value)
            # Если ключ новый, создаем список значений
            else:
                merged_dict[key] = [value]
    return merged_dict


# проверяет все ли массивы при ключах имеют одинаковую длинну
# эта функция сделана для заполнения базы данных с помощью командной строк
# при желании это можно реализовать
def equal_length_lists(d):
    lengths = {len(lst) for lst in d.values()}
    return len(lengths) == 1


# заполняет таблицу банк
@db_connection
def add_bank(c, bank_data):
    for bank in bank_data:
        c.execute("INSERT INTO Bank(name) VALUES(?)", (bank,))
    return "Bank added successfully."


# заполняет таблицу юзер
@db_connection
def add_user(c, user_name, birthday, accounts):
    for i in range(len(user_name)):
        name, surname = validate.validate_user_full_name(user_name[i])
        c.execute("INSERT INTO User(name,surname,birth_day,accounts) VALUES(?,?,?,?)",
                  (name, surname, f"{birthday[i]}", accounts[i],))
        print(f"user {name} {surname} added success")
    return 'success'


# заполняет таблицу аккаунт
@db_connection
def add_account_to_db(c, user_id, user_type, acc_numb, bank_id, currency, amount, status):
    for i in range(len(user_id)):
        acc_numb[i] = validate.validate_account_number(acc_numb[i])
        c.execute('''INSERT INTO Account(user_id, type, account_number, bank_id, currency, amount, status) 
                VALUES(?,?,?,?,?,?,?)''',
                  (user_id[i], user_type[i], acc_numb[i], bank_id[i], currency[i], amount[i], status[i]))
        # Получаем количество счетов для текущего пользователя

        c.execute("SELECT COUNT(*) FROM Account WHERE user_id = ?", (user_id[i],))
        numb_of_acc = c.fetchone()[0]  # Извлекаем значение из курсора
        #оказалось что это с функцией по какой то причине не работает оставлю так
        c.execute("UPDATE User SET Accounts = ? WHERE id = ?", (numb_of_acc, user_id[i]))

    return 'success'


@db_connection
def change_something(c, table_name, row_id, column, value):
    c.execute(f"UPDATE {table_name} SET {column} = ? WHERE id = ?", (value, row_id, ))
    return 'success'


@db_connection
def delete_row_from_account(c, row_id):
    c.execute(f"DELETE FROM Account WHERE id = ?", (row_id,))
    return 'success'


@db_connection
def delete_row_from_user(c, row_id):
    # в идеале базы данных должны быть связаны между собой по айди
    # поэтому чтоб успешно удалить юзера надо еще удалить все записи связаные с ним
    # это же и касается банка
    delete_row_from_account(row_id)
    c.execute(f"DELETE FROM User WHERE id = ?", (row_id,))
    return 'success'


@db_connection
def delete_row_from_bank(c, row_id):
    delete_row_from_account(row_id)
    c.execute(f"DELETE FROM Bank WHERE id = ?", (row_id,))
    return 'success'


# она просто очищает таблицы в бд
@db_connection
def clear_table(c, table_name):
    c.execute(f"DELETE FROM {table_name}")
    return 'success'

def add_account_by_file(path):
    data = merge_dicts(read_csv_to_dict(path))
    add_account_to_db(data["user_id"], data["type"], data["account_number"],
                      data["bank_id"], data["currency"], data["amount"], data["status"])
    return "success"


def add_bank_by_file(path):
    data = merge_dicts(read_csv_to_dict(path))
    add_bank(data['Name'])
    return "success"


def add_user_by_file(path):
    data = merge_dicts(read_csv_to_dict(path))
    add_user(data["user_name"], data["birthday"], data["accounts"])


def convert_currency(currency_values, orig_currency, conv_currency, amount):
    return round((amount/currency_values[orig_currency]) * currency_values[conv_currency], 2)


@db_connection
def get_bankname(c, bank_id):
    c.execute('''SELECT bank.name AS bank_name
               FROM account
               INNER JOIN bank ON account.bank_id = bank.id
               WHERE account.id = ?''', (bank_id,))
    return c.fetchone()[0]


@db_connection
def get_data_from_table(c, table_name, row_name, row_id):
    c.execute(f"SELECT {table_name} FROM {row_name} WHERE id = ? ", (row_id,))
    return c.fetchone()[0]


@db_connection
def transfer_money(c, sender_id, receiver_id, sent_currency, sent_amount, transfer_time=None):
    # берем ключи из апишки с курсом валют (подсказка 'USD': 1)
    currency_dict = get_curency_data()
    # смотрим есть ли заданая валюта в дикте курса валют
    validate.validate_field_value('sent_currency', sent_currency,  dict.keys(currency_dict))
    print('valid current success')

    # вытаскиваем нужные данные для заполнения таблицы транзакций
    bank_sender_name = get_bankname(sender_id)
    bank_receiver_name = get_bankname(receiver_id)
    sender_amount = get_data_from_table('Amount', 'Account', sender_id)
    receiver_amount = get_data_from_table('Amount', 'Account', receiver_id)
    sender_currency = get_data_from_table('Currency', 'Account', sender_id)
    receiver_currency = get_data_from_table('Currency', 'Account', receiver_id)
    sent_am_in_receiver_cur = sent_amount
    sent_am_in_sender_cur = sent_amount
    sender_am_in_sent_cur = sender_amount

    # проверяем валюты у отправителя
    if sender_currency != sent_currency:
        sender_am_in_sent_cur = convert_currency(currency_dict, sender_currency, sent_currency, sender_amount)
        print('sender_am_in_sent_cur', sender_am_in_sent_cur)
        sent_am_in_sender_cur = convert_currency(currency_dict, sent_currency, sender_currency, sent_amount)
    # проверяем достаточно ли денег на счету
    if sender_am_in_sent_cur <= sent_amount:
        raise ValueError('not enough money in the account')
    # проверяем валюты у получателя
    if receiver_currency != sent_currency:
        sent_am_in_receiver_cur = convert_currency(currency_dict, sent_currency, receiver_currency, sent_amount)

    # проверяем наличие времени
    transfer_time = validate.add_transaction_time(transfer_time)

    new_sender_amount = sender_amount - sent_am_in_sender_cur
    new_receiver_amount = receiver_amount + sent_am_in_receiver_cur

    # меняем значения суммы у юзеров
    change_something('Account', sender_id, 'amount', new_sender_amount)
    change_something('Account', receiver_id, 'amount', new_receiver_amount)

    # заполняем таблицу
    c.execute(
        '''INSERT INTO BankTransaction(bank_sender_name, account_sender_id, bank_receiver_name, account_receiver_id, 
        sent_currency, sent_amount, datetime) VALUES(?,?,?,?,?,?,?)''',
        (bank_sender_name, sender_id, bank_receiver_name, receiver_id, sent_currency, sent_amount, transfer_time,))

    return 'success'
