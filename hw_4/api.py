import requests
import csv
import validate
from db_con_decor import db_connection
import os
from dotenv import load_dotenv, find_dotenv
import logging
from consts import URL
from datetime import datetime
import random

formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
my_logger = logging.getLogger('CustomLogger')
my_handler = logging.FileHandler('file.log')
my_handler.setFormatter(formatter)
my_logger.setLevel(logging.INFO)
my_logger.addHandler(my_handler)

load_dotenv(find_dotenv())


# получает дикт из валют и их значений относительно доллара
def get_curency_data():
    # .env
    # dotenv lib

    response = requests.get(URL.format(os.getenv('API_KEY')))
    if response.status_code == requests.codes.ok:
        data = response.json()
        #сделать логами
        my_logger.info("data_get successfully")
        my_logger.info(data['data'])
        return data['data']
    my_logger.error("data_get failure")
    return None


# читает цсв файл переобразовывая в дикт
def read_csv_to_dict(file_path):
    with open(file_path, 'r') as file:
        return list(csv.DictReader(file))


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


def unpack_data(data):
    keys = list(data.keys())
    return [data[key] for key in keys] if len(keys) > 1 else data[keys[0]]

#{ filler_date: [{}, {} ]}
#{ "row1": {}, "row2": {} }
# заполняет таблицу банк
@db_connection
def add_bank(cur, **kwargs):
    data = unpack_data(kwargs)
    my_logger.info(data)
    # распаковать лист диктов
    my_logger.info(data)
    cur.executemany("INSERT INTO Bank(name) VALUES(:Name)", data)  # :param_name, :param_name2
    my_logger.info("Bank added successfully.")


# заполняет таблицу юзер
@db_connection
def add_user(cur, **kwargs):
    data = unpack_data(kwargs)
    my_logger.info(data)
    for i in data:
        i["name"] = validate.validate_user_full_name(i["user_name"])[0]
        i["surname"] = validate.validate_user_full_name(i["user_name"])[1]
    cur.executemany("INSERT INTO User(name,surname,birth_day,accounts) VALUES(:name ,:surname,:birthday,:accounts)",
                    data)
    my_logger.info("User added successfully.")

def unpack_to_string(data):
    result = ''
    for tup in data:
        for item in tup:
            result += str(item) + ','
    return result.rstrip(',')
#
# заполняет таблицу аккаунт

def set_accounts(cur, data):
    for i in data:
        cur.execute("SELECT id FROM Account WHERE user_id = ?", (i["user_id"],))
        numb_of_acc = cur.fetchall()  # Извлекаем значение из курсора
        account_str = unpack_to_string(numb_of_acc)
        my_logger.info(account_str)
        cur.execute("UPDATE User SET Accounts = ? WHERE id = ?", (account_str, i["user_id"],))

@db_connection
def add_account(cur, **kwargs):
    data = unpack_data(kwargs)
    my_logger.info(data)
    validate.valid_acc(data)
    cur.executemany('''INSERT INTO Account(user_id, type, account_number, bank_id, currency, amount, status) 
            VALUES(:user_id,:type,:account_number,:bank_id,:currency,:amount,:status)''',
                    data)
    set_accounts(cur, data)
    my_logger.info("account added successfully.")

#update row in bd
@db_connection
def update_row(c, table_name, row_id, column, value):
    c.execute(f"UPDATE {table_name} SET {column} = ? WHERE id = ?", (value, row_id, ))
    return "success"


@db_connection
def delete_row(cur, row_id, fnc):
    match fnc:
        case "User":
            cur.execute("DELETE FROM Account WHERE user_id = ?", (row_id,))
            cur.execute("DELETE FROM User WHERE id = ?", (row_id,))
        case "Bank":
            cur.execute("DELETE FROM Account WHERE bank_id = ?", (row_id,))
            cur.execute("DELETE FROM Bank WHERE id = ?", (row_id,))
        case "Account":
            cur.execute("DELETE FROM Account WHERE id = ?", (row_id,))
    my_logger.info(f"{fnc} delete successfully.")
    return "success"


# она просто очищает таблицы в бд
@db_connection
def clear_table(cur, table_name):
    cur.execute(f"DELETE FROM {table_name}")
    return 'success'


def add_table_by_file(path, table_name):
    data = read_csv_to_dict(path)
    match table_name:
        case "Bank":
            add_bank(table_filler=data)
        case "User": 
            add_user(table_filler=data)
        case "Account":
            add_account(table_filler=data)


def convert_currency(currency_values, orig_currency, conv_currency, amount):
    return round((amount / currency_values[orig_currency]) * currency_values[conv_currency], 2)

# достать банкнейм
@db_connection
def get_bankname(cur, id_user):
    bank_id = get_data_from_table(table_name ="Account", row_name="bank_id",row_id= id_user)
    my_logger.info("get_bankname successfully.")
    return get_data_from_table(table_name = "Bank",row_name="name",  row_id = bank_id)


@db_connection
def get_data_from_table(cur,  row_name, table_name, row_id):
    cur.execute(f"SELECT {row_name} FROM {table_name} WHERE id = ? ", (row_id,))
    return cur.fetchone()[0]


@db_connection
def transfer_money(c, sender_id, receiver_id, sent_amount, transfer_time=None):
    currency_dict = get_curency_data()
    my_logger.info('valid current success')
    # вытаскиваем нужные данные для заполнения таблицы транзакций
    bank_sender_name = get_bankname(sender_id)
    bank_receiver_name = get_bankname( receiver_id)
    sender_amount = get_data_from_table("Amount", "Account", sender_id)
    receiver_amount = get_data_from_table("Amount", "Account", receiver_id)
    sender_currency = get_data_from_table("Currency", "Account", sender_id)
    receiver_currency = get_data_from_table("Currency", "Account", receiver_id)
    sent_am_in_sender_cur = sent_amount

    if sender_amount <= sent_amount:
        raise ValueError('not enough money in the account')
    if receiver_currency != sender_currency:
        sent_am_in_sender_cur = convert_currency(currency_dict, receiver_currency, sender_currency, sent_amount)

    # проверяем наличие времени
    transfer_time = validate.add_transaction_time(transfer_time)

    new_sender_amount = sender_amount - sent_am_in_sender_cur
    new_receiver_amount = receiver_amount + sent_am_in_sender_cur

    # меняем значения суммы у юзеров
    update_row('Account', sender_id, 'amount', round(new_sender_amount,2))
    update_row('Account', receiver_id, 'amount', round(new_receiver_amount,2))

    # вынести функцией
    # заполняем таблицу
    c.execute(
        '''INSERT INTO BankTransaction(bank_sender_name, account_sender_id, bank_receiver_name, account_receiver_id, 
        sent_currency, sent_amount, datetime) VALUES(?,?,?,?,?,?,?)''',
        (bank_sender_name, sender_id, bank_receiver_name, receiver_id, sender_currency, sent_amount, transfer_time,))
    my_logger.info("success")
    return "success"


@db_connection
def select_random_users_with_discounts(cursor):
    cursor.execute("SELECT Id FROM User")
    all_users = cursor.fetchall()
    random_users = random.sample(all_users, min(10, len(all_users)))  # Randomly select up to 10 users
    user_discounts = {}
    for user_id in random_users:
        discount = random.choice([25, 30, 50])  # Randomly choose discount
        user_discounts[user_id[0]] = discount
        my_logger.info(user_discounts)
        my_logger.info("select_random_users_with_discounts success")
    return user_discounts


@db_connection
def user_with_highest_amount(cursor):
    cursor.execute('''
        SELECT User_id
        FROM Account
        ORDER BY Amount DESC
        LIMIT 1
    ''')
    user_id = cursor.fetchone()[0]
    name = get_data_from_table("name","User", user_id)
    my_logger.info(name)
    my_logger.info("user_with_highest_amount success")
    return name


@db_connection
def bank_with_biggest_capital(cursor):
    currency_dict = get_curency_data()
    # Извлекаем все записи из таблицы Account
    cursor.execute("SELECT Bank_id, Currency, Amount FROM Account")
    accounts = cursor.fetchall()

    # Создаем словарь для хранения суммарного капитала для каждого банка в долларах
    bank_capital = {}

    # Заполняем словарь данными из таблицы Account
    for bank_id, currency, amount in accounts:
        amount_in_usd = convert_currency(currency_dict, currency, 'USD', amount)
        if bank_id in bank_capital:
            bank_capital[bank_id] += amount_in_usd
        else:
            bank_capital[bank_id] = amount_in_usd

    # Находим банк с наибольшим капиталом
    max_capital_bank_id = max(bank_capital, key=bank_capital.get)

    # Возвращаем ID банка с наибольшим капиталом
    return max_capital_bank_id


@db_connection
def bank_serving_oldest_client(cursor):
    # Извлекаем все записи из таблицы User
    cursor.execute("SELECT Id, Birth_day FROM User")
    users = cursor.fetchall()

    # Извлекаем все записи из таблицы Account
    cursor.execute("SELECT User_id, Bank_id FROM Account")
    accounts = cursor.fetchall()

    # Находим самого старого пользователя
    oldest_user_id = None
    oldest_birth_day = datetime.max

    for user_id, birth_day in users:
        birth_date = datetime.strptime(birth_day, '%Y-%m-%d')
        if birth_date < oldest_birth_day:
            oldest_birth_day = birth_date
            oldest_user_id = user_id

    # Находим банк, которому принадлежит самый старый пользователь
    for user_id, bank_id in accounts:
        if user_id == oldest_user_id:
            return bank_id


@db_connection
def print_table(cursor, table_name):
    cursor.execute(f"PRAGMA table_info({table_name})")
    column_names = [row[1] for row in cursor.fetchall()]
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    print(", ".join(column_names))
    for row in rows:
        print(", ".join(map(str, row)))


@db_connection
def bank_with_highest_unique_users(cursor):
    # Создаем словарь для хранения количества уникальных пользователей для каждого банка
    unique_users_by_bank = {}

    # Выбираем все транзакции из таблицы BankTransaction
    cursor.execute("SELECT Bank_sender_name, Account_sender_id FROM BankTransaction")
    transactions = cursor.fetchall()

    # Подсчитываем количество уникальных пользователей для каждого банка
    for bank_name, account_id in transactions:
        if bank_name not in unique_users_by_bank:
            unique_users_by_bank[bank_name] = set()
        unique_users_by_bank[bank_name].add(account_id)

    # Находим банк с наибольшим количеством уникальных пользователей
    bank_with_highest_users = max(unique_users_by_bank.items(), key=lambda x: len(x[1]))

    return bank_with_highest_users[0]

@db_connection
def delete_users_with_incomplete_info(cursor):
    cursor.execute("SELECT id FROM User WHERE Name IS NULL OR Surname IS NULL OR Birth_day IS NULL")
    deleted_user_id = cursor.fetchall()
    cursor.execute("DELETE FROM Account WHERE User_id = ?", deleted_user_id)
    return "Deletion complete"


 