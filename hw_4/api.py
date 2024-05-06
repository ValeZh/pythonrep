import sqlite3
import requests
import csv
import datetime

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


# разобраться и переделать
def read_csv_to_dict(file_path):
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        data_dict = [row for row in reader]
    return data_dict


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
def equal_length_lists(d):
    lengths = {len(lst) for lst in d.values()}
    return len(lengths) == 1


@db_connection
def add_bank(c, bank_data):
    # Add bank to the database
    for bank in bank_data:
        c.execute("INSERT INTO Bank(name) VALUES(?)", (bank,))
    return "Bank added successfully."


@db_connection
def read_data_from_file(previous_output):
    with open(previous_output, "r", encoding="utf-8") as file:
        print("read data success")
        return list(csv.DictReader(file))


@db_connection
def add_user(c, user_name, birthday, accounts):
    for i in range(len(user_name)):
        name = str.split(user_name[i])[0]
        surname = str.split(user_name[i])[1]
        c.execute("INSERT INTO User(name,surname,birth_day,accounts) VALUES(?,?,?,?)",
                  (name, surname, f"{birthday[i]}", accounts[i],))
        print(f"user {name} {surname} added success")
    return 'success'


@db_connection
def add_account_to_db(c, user_id, user_type, acc_numb, bank_id, currency, amount, status):
    for i in range(len(user_id)):
        c.execute("INSERT INTO Account(user_id, type, account_number, bank_id, currency, amount, status) VALUES(?,?,?,?,?,?,?)",
                    (user_id[i], user_type[i], acc_numb[i], bank_id[i], currency[i], amount[i], status[i]))
        # Получаем количество счетов для текущего пользователя
        c.execute("SELECT COUNT(*) FROM Account WHERE user_id = ?", (user_id[i],))
        numb_of_acc = c.fetchone()[0]  # Извлекаем значение из курсора
        # забабахать сюда функцию
        c.execute("UPDATE User SET Accounts = ? WHERE id = ?", (numb_of_acc, user_id[i]))
    return 'success'


@db_connection
def change_something(c, table_name, row_id, column, value):
    c.execute(f"UPDATE {table_name} SET {column} = ? WHERE id = ?", (value, row_id))
    return 'success'


@db_connection
def delete_row_from_account(c, row_id):
    c.execute(f"DELETE FROM Account WHERE id = ?", (row_id,))
    return 'success'


@db_connection
def delete_row_from_user(c, row_id):
    # забабахать сюда функцию
    c.execute(f"DELETE FROM Account WHERE User_id = ?", (row_id, ))
    c.execute(f"DELETE FROM User WHERE id = ?", (row_id,))
    return 'success'


@db_connection
def delete_row_from_bank(c, row_id):
    # забабахать сюда функцию
    c.execute(f"DELETE FROM Account WHERE Bank_id = ?", (row_id,))
    c.execute(f"DELETE FROM Bank WHERE id = ?", (row_id,))
    return 'success'


@db_connection
def clear_table(c, table_name):
    c.execute("DELETE * FROM {}".format(table_name))
    return 'success'


def add_account_by_file(path):
    data = merge_dicts(read_csv_to_dict(path))
    add_account_to_db(data["user_id"], data["type"], data["account_number"], data["bank_id"], data["currency"], data["amount"], data["status"])
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
def transfer_money(c, sender_id, receiver_id, sent_currency, sent_amount, transfer_time=0):
    # берем ключи из апишки с курсом валют (подсказка 'USD': 1)
    currency_dict = get_curency_data()
    print()
    #смотрим есть ли заданая валюта в дикте курса валют
    if not (any(item == sent_currency for item in dict.keys(currency_dict))):
        print('Error sent_currency')
        return 'Error sent_currency'
    print('valid current success')

    c.execute('''SELECT bank.name AS bank_name
              FROM account
              INNER JOIN bank ON account.bank_id = bank.id
              WHERE account.id = ?''', (sender_id,))

    bank_sender_name = c.fetchone()[0]
    c.execute('''SELECT bank.name AS bank_name
                 FROM account
                 INNER JOIN bank ON account.bank_id = bank.id
                 WHERE account.id = ?''', (receiver_id,))
    bank_receiver_name = c.fetchone()[0]

    print(bank_sender_name)
    print(bank_receiver_name)
    print('select bank success')

    c.execute("SELECT Amount FROM Account WHERE id IN (? , ?)", (sender_id, receiver_id,))
    result = c.fetchall()
    sender_amount = result[0][0]
    receiver_amount = result[1][0]
    print('select amount success')

    c.execute("SELECT Currency From Account WHERE id IN (?, ?)", (sender_id, receiver_id,))
    result = c.fetchall()
    sender_currency = result[0][0]
    receiver_currency = result[1][0]
    print('select Currency success')

    sent_am_in_receiver_cur = sent_amount
    sent_am_in_sender_cur = sent_amount
    sender_am_in_sent_cur = 0
    receiver_am_in_sent_cur = 0
    #вынести в функцию
    if sender_currency != sent_currency:
        sender_am_in_sent_cur = convert_currency(currency_dict, sender_currency, sent_currency, sender_amount)
        print('sender_am_in_sent_cur', sender_am_in_sent_cur)
        sent_am_in_sender_cur = convert_currency(currency_dict, sent_currency, sender_currency, sent_amount)
    if sender_am_in_sent_cur < sent_amount:
        print('not enough money in the account')
        return 'not enough money in the account'


    if receiver_currency != sent_currency:
        sent_am_in_receiver_cur = convert_currency(currency_dict, sent_currency, receiver_currency, sent_amount)
        print(sent_am_in_receiver_cur)


    if transfer_time == 0:
        transfer_time = datetime.datetime.today()

    print(sender_amount)
    print(sent_am_in_sender_cur)
    new_sender_amount = sender_amount - sent_am_in_sender_cur
    print("new_sender_amount", new_sender_amount)
    new_receiver_amount = receiver_amount + sent_am_in_receiver_cur
    print("new_receiver_amount",new_receiver_amount)

    change_something('Account', sender_id, 'amount', new_sender_amount)
    change_something('Account', receiver_id, 'amount', new_receiver_amount)

    c.execute("INSERT INTO BankTransaction(bank_sender_name, account_sender_id, bank_receiver_name, account_receiver_id, sent_currency, sent_amount, datetime) VALUES(?,?,?,?,?,?,?)",
              (bank_sender_name, sender_id, bank_receiver_name, receiver_id, sent_currency, sent_amount, transfer_time,))

    return 'success'

    # узнать кол во дененег и валюту у человека на акаунте
    # если валюта у отправителя и получателя разные то конвертировать валюту отправителя и получателя и сохранить в переменных
    # сравнивать с отправляемой если меньше уходить из функции
    # при отправлении
    # заполнить таблицу транзакций
    # отнять у отправтеля деньги в таблице аккаунт
    # прибавить деньги у получателя

