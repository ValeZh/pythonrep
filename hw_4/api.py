import requests
import csv
import validate
from db_con_decor import db_connection
import os
from dotenv import load_dotenv, find_dotenv
import logging
from consts import URL
from datetime import datetime, timedelta
import random
from collections import Counter, defaultdict


formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s')
my_logger = logging.getLogger('CustomLogger')
my_handler = logging.FileHandler('file.log')
my_handler.setFormatter(formatter)
my_logger.setLevel(logging.INFO)
my_logger.addHandler(my_handler)

load_dotenv(find_dotenv())


# gets dict from currencies and their values relative to the dollar
def get_currency_data():
    response = requests.get(URL.format(os.getenv('API_KEY')))
    if response.status_code == requests.codes.ok:
        data = response.json()
        # make logs
        my_logger.info("data_get successfully")
        my_logger.info(data['data'])
        return data['data']
    my_logger.error("data_get failure")
    return None


# reads csv file converted to dict
def read_csv_to_dict(file_path):
    with open(file_path, 'r') as file:
        return list(csv.DictReader(file))


def unpack_data(data):
    return data.values()


def format_data_string(data):
    print(data)
    formatted_string = ', '.join(f'{item}' for item in dict.keys(data[0]))
    formatted_string_colon = ', '.join(f':{item}' for item in dict.keys(data[0]))
    return formatted_string, formatted_string_colon


@db_connection
def add_generic_by_path(cur, path, table_name):
    data = read_csv_to_dict(path)
    print(data)
    data = validate.username_validate(data)
    column, form_column = format_data_string(data)
    cur.executemany(f"INSERT INTO {table_name}({column}) VALUES({form_column})", data)
    if table_name == "Account":
        data = validate.valid_acc(data)
        data = validate.validate_account_number(data)
        set_accounts(cur, data)
    my_logger.info(f"{table_name} added successfully.")


def unpack_to_string(data):
    result = ''
    for tup in data:
        for item in tup:
            result += str(item) + ','
    return result.rstrip(',')


# fills the table account
def set_accounts(cur, data):
    for i in data:
        # import pdb;pdb.set_trace()
        cur.execute("SELECT id FROM Account WHERE user_id = ?", (i["user_id"],))
        numb_of_acc = cur.fetchall()
        account_str = unpack_to_string(numb_of_acc)
        my_logger.info(account_str)
        cur.execute("UPDATE User SET Accounts = ? WHERE id = ?", (account_str, i["user_id"],))


# update row in bd
@db_connection
def update_row(c, table_name, row_id, column, value):
    c.execute(f"UPDATE {table_name} SET {column} = ? WHERE id = ?", (value, row_id, ))
    return "success"


@db_connection
def delete_generic(cur, row_id, table_name, second_table=None):
    if second_table:
        cur.execute(f"DELETE FROM Account WHERE {table_name.lower()}_id = ?", (row_id,))
    cur.execute(f"DELETE FROM {table_name} WHERE id = ?", (row_id,))
    my_logger.info(f"{table_name} delete successfully.")
    return "success"


def delete_row(row_id, table_name):
    match table_name:
        case "User":
            delete_user(row_id)
        case "Bank":
            delete_bank(row_id)
        case "Account":
            delete_account(row_id)


def delete_user(row_id):
    delete_generic(row_id, 'User', True)


def delete_bank(row_id):
    delete_generic(row_id, 'Bank', True)


def delete_account(row_id):
    delete_generic(row_id, 'Account', False)


# it just clears the tables in the database
@db_connection
def clear_table(cur, table_name):
    cur.execute(f"DELETE FROM {table_name}")
    return 'success'


def convert_currency(currency_values, orig_currency, conv_currency, amount):
    return round((amount / currency_values[orig_currency]) * currency_values[conv_currency], 2)


def get_bankname(id_user):
    bank_id = get_data_from_table(table_name="Account", col_name="bank_id", row_id=id_user)
    my_logger.info("get_bankname successfully.")
    return get_data_from_table(table_name="Bank", col_name="name", row_id=bank_id)


@db_connection
def get_data_from_table(cur, col_name, table_name, row_id):
    cur.execute(f"SELECT {col_name} FROM {table_name} WHERE id = ? ", (row_id,))
    return cur.fetchone()[0]


@db_connection
def insert_transaction(cur, bank_sender_name, sender_id, bank_receiver_name,
                       receiver_id, sender_currency, sent_amount, transfer_time):
    cur.execute('''
    INSERT INTO BankTransaction
    (bank_sender_name, account_sender_id, 
    bank_receiver_name, account_receiver_id, 
    sent_currency, sent_amount, datetime) 
    VALUES(?,?,?,?,?,?,?)''',
                (bank_sender_name, sender_id,
                 bank_receiver_name, receiver_id,
                 sender_currency, sent_amount, transfer_time,))


def account_valid(sender_amount, sent_amount, sender_currency, receiver_currency, currency_dict, transfer_time):
    if validate.valid_currency_amount(sender_amount, sent_amount, sender_currency, receiver_currency):
        sent_amount = convert_currency(currency_dict, receiver_currency, sender_currency, sent_amount)
    transfer_time = validate.add_transaction_time(transfer_time)
    return sent_amount, transfer_time

def get_data_by_id(sender_id, receiver_id):
    bank_sender_name = get_bankname(sender_id)
    bank_receiver_name = get_bankname(receiver_id)
    sender_amount = get_data_from_table("Amount", "Account", sender_id)
    receiver_amount = get_data_from_table("Amount", "Account", receiver_id)
    sender_currency = get_data_from_table("Currency", "Account", sender_id)
    receiver_currency = get_data_from_table("Currency", "Account", receiver_id)
    return bank_sender_name, bank_receiver_name, sender_amount, receiver_amount, sender_currency, receiver_currency

def transfer_money(sender_id, receiver_id, sent_amount, transfer_time=None):
    currency_dict = get_currency_data()
    my_logger.info('valid current success')

    # тестировать количество вызовов функции
    # pull the necessary data to fill the transaction table
    (bank_sender_name, bank_receiver_name, sender_amount, receiver_amount,
     sender_currency, receiver_currency) = get_data_by_id(sender_id, receiver_id)

    sent_amount, transfer_time = account_valid(sender_amount, sent_amount, sender_currency, receiver_currency,
                                               currency_dict, transfer_time)

    new_sender_amount = round(sender_amount - sent_amount, 2)
    new_receiver_amount = round(receiver_amount + sent_amount, 2)

    # change the sum values of the users
    update_row("Account", sender_id, "amount", new_sender_amount)
    update_row("Account", receiver_id, "amount", new_receiver_amount)

    # fill the table
    insert_transaction(bank_sender_name, sender_id, bank_receiver_name, receiver_id,
                       sender_currency, sent_amount, transfer_time)
    my_logger.info("success")
    return "success"

@db_connection
def select_id_from_user(cursor):
    cursor.execute("SELECT Id FROM User")
    return cursor.fetchall()

def select_random_users_with_discounts():
    all_users = select_id_from_user()

    random_users = random.sample(all_users, min(10, len(all_users)))  # Randomly select up to 10 users
    print(random_users)
    user_discounts = {}
    # comprehension use
    for user_id in random_users:
        discount = random.choice([25, 30, 50])  # Randomly choose discount
        user_discounts[user_id[0]] = discount
        #########################################
        my_logger.info(user_discounts)
        my_logger.info("select_random_users_with_discounts success")
    return user_discounts

@db_connection
def select_for_user_with_highest_amount(cursor):
    cursor.execute('''
        SELECT User_id
        FROM Account
        ORDER BY Amount DESC
        LIMIT 1
    ''')
    return cursor.fetchone()[0]



def user_with_highest_amount():
    user_id = select_for_user_with_highest_amount()
    print(user_id)
    name = get_data_from_table("name", "User", user_id)
    my_logger.info(name)
    my_logger.info("user_with_highest_amount success")
    return name

@db_connection
def select_for_bank_with_biggest_capital(cursor):
    cursor.execute("SELECT Bank_id, Currency, Amount FROM Account")
    return cursor.fetchall()


def bank_with_biggest_capital():
    currency_dict = get_currency_data()
    # Extract all records from the Account table
    accounts = select_for_bank_with_biggest_capital()
    # Create a dictionary to store total capital for each bank in dollars
    bank_capital = {}

    # Create a dictionary to store the total capital for each bank in dollars
    for bank_id, currency, amount in accounts:
        amount_in_usd = convert_currency(currency_dict, currency, 'USD', amount)
        if bank_id in bank_capital:
            bank_capital[bank_id] += amount_in_usd
        else:
            bank_capital[bank_id] = amount_in_usd

    # Find the bank with the most capital
    max_capital_bank_id = max(bank_capital, key=bank_capital.get)
    my_logger.info(f"max capital bank id {max_capital_bank_id}")
    my_logger.info("bank_with_biggest_capital success")
    return max_capital_bank_id

@db_connection
def select_for_bank_serving_oldest_client(cursor):
    cursor.execute("SELECT Id, Birth_day FROM User")
    users = cursor.fetchall()

    cursor.execute("SELECT User_id, Bank_id FROM Account")
    accounts = cursor.fetchall()
    return users, accounts

def bank_serving_oldest_client():
    users, accounts = select_for_bank_serving_oldest_client()
    oldest_user = min(users, key=lambda user: datetime.strptime(user[1], '%Y-%m-%d'))
    oldest_user_id = oldest_user[0]
    # Create a list of user_ids from the accounts
    user_ids = [user_id for user_id, _ in accounts]
    # Find the index of the oldest_user_id
    index = user_ids.index(oldest_user_id)

    return accounts[index][1]


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
def select_for_bank_with_highest_unique_users(cursor):
    cursor.execute("SELECT Bank_sender_name, Account_sender_id FROM BankTransaction")
    return cursor.fetchall()

# bank_2 : set(acc1 acc2)
def bank_with_highest_unique_users():
    transactions = select_for_bank_with_highest_unique_users()
    print(transactions)
    unique_users_by_bank = defaultdict(set)

    for bank_name, account_id in transactions:
        unique_users_by_bank[bank_name].add(account_id)

    unique_user_counts = Counter({bank: len(users) for bank, users in unique_users_by_bank.items()})

    bank_with_highest_users = unique_user_counts.most_common(1)[0]

    return bank_with_highest_users[0]

@db_connection
def select_for_delete_users_with_incomplete_info(cursor):
    cursor.execute("SELECT id FROM User WHERE Name IS NULL OR Surname IS NULL OR Birth_day IS NULL")
    return cursor.fetchall()


def delete_users_with_incomplete_info():
    result = select_for_delete_users_with_incomplete_info()
    for i in result:
        deleted_user_id = result[0]
        delete_user(deleted_user_id)

    return "Deletion complete"

@db_connection
def select_for_get_user_transactions(c, user_id, start_date_str, end_date_str):
    c.execute('''
    SELECT * FROM BankTransaction
    WHERE (Account_sender_id = ? OR Account_receiver_id = ?)
    AND Datetime BETWEEN ? AND ?
    ''', (user_id, user_id, start_date_str, end_date_str))
    return c.fetchall()


def get_user_transactions(user_id):
    # Calculate the date three months ago from today
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    # Convert dates to string format for SQL query
    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')
    return select_for_get_user_transactions(user_id, start_date_str, end_date_str)

 