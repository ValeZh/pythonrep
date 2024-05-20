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
    keys = list(data.keys())
    return [data[key] for key in keys] if len(keys) > 1 else data[keys[0]]


# { filler_date: [{}, {} ]}
# { "row1": {}, "row2": {} }
# fills the table bank
@db_connection
def add_bank(cur, **kwargs):
    data = unpack_data(kwargs)
    my_logger.info(data)
    # unpack the mass of dicts
    my_logger.info(data)
    cur.executemany("INSERT INTO Bank(name) VALUES(:Name)", data)  # :param_name, :param_name2
    my_logger.info("Bank added successfully.")


# fills the table user
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


# fills the table account
def set_accounts(cur, data):
    for i in data:
        cur.execute("SELECT id FROM Account WHERE user_id = ?", (i["user_id"],))
        numb_of_acc = cur.fetchall()
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


# update row in bd
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


# it just clears the tables in the database
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


def get_bankname(id_user):
    bank_id = get_data_from_table(table_name="Account", row_name="bank_id", row_id=id_user)
    my_logger.info("get_bankname successfully.")
    return get_data_from_table(table_name="Bank", row_name="name",  row_id=bank_id)


@db_connection
def get_data_from_table(cur,  row_name, table_name, row_id):
    cur.execute(f"SELECT {row_name} FROM {table_name} WHERE id = ? ", (row_id,))
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


def transfer_money(sender_id, receiver_id, sent_amount, transfer_time=None):
    currency_dict = get_currency_data()
    my_logger.info('valid current success')
    # pull the necessary data to fill the transaction table
    bank_sender_name = get_bankname(sender_id)
    bank_receiver_name = get_bankname(receiver_id)
    sender_amount = get_data_from_table("Amount", "Account", sender_id)
    receiver_amount = get_data_from_table("Amount", "Account", receiver_id)
    sender_currency = get_data_from_table("Currency", "Account", sender_id)
    receiver_currency = get_data_from_table("Currency", "Account", receiver_id)
    sent_am_in_sender_cur = sent_amount

    if sender_amount <= sent_amount:
        raise ValueError("not enough money in the account")
    if receiver_currency != sender_currency:
        sent_am_in_sender_cur = convert_currency(currency_dict, receiver_currency, sender_currency, sent_amount)

    # check the time
    transfer_time = validate.add_transaction_time(transfer_time)

    new_sender_amount = sender_amount - sent_am_in_sender_cur
    new_receiver_amount = receiver_amount + sent_am_in_sender_cur

    # change the sum values of the users
    update_row("Account", sender_id, "amount", round(new_sender_amount, 2))
    update_row("Account", receiver_id, "amount", round(new_receiver_amount, 2))

    # fill the table
    insert_transaction(bank_sender_name, sender_id, bank_receiver_name, receiver_id,
                       sender_currency, sent_amount, transfer_time)
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
    name = get_data_from_table("name", "User", user_id)
    my_logger.info(name)
    my_logger.info("user_with_highest_amount success")
    return name


@db_connection
def bank_with_biggest_capital(cursor):
    currency_dict = get_currency_data()
    # Extract all records from the Account table
    cursor.execute("SELECT Bank_id, Currency, Amount FROM Account")
    accounts = cursor.fetchall()

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
def bank_serving_oldest_client(cursor):
    cursor.execute("SELECT Id, Birth_day FROM User")
    users = cursor.fetchall()

    cursor.execute("SELECT User_id, Bank_id FROM Account")
    accounts = cursor.fetchall()

    # Find the oldest user
    oldest_user_id = None
    oldest_birth_day = datetime.max

    for user_id, birth_day in users:
        birth_date = datetime.strptime(birth_day, '%Y-%m-%d')
        if birth_date < oldest_birth_day:
            oldest_birth_day = birth_date
            oldest_user_id = user_id

    # Find the bank that owns the oldest user
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
    # Create a dictionary to store the number of unique users for each bank
    unique_users_by_bank = {}

    # Select all transactions from the BankTransaction table
    cursor.execute("SELECT Bank_sender_name, Account_sender_id FROM BankTransaction")
    transactions = cursor.fetchall()

    # Count the number of unique users for each bank
    for bank_name, account_id in transactions:
        if bank_name not in unique_users_by_bank:
            unique_users_by_bank[bank_name] = set()
        unique_users_by_bank[bank_name].add(account_id)

    # Find the bank with the unique users
    bank_with_highest_users = max(unique_users_by_bank.items(), key=lambda x: len(x[1]))

    return bank_with_highest_users[0]


@db_connection
def delete_users_with_incomplete_info(cursor):
    while True:
        cursor.execute("SELECT id FROM User WHERE Name IS NULL OR Surname IS NULL OR Birth_day IS NULL")
        result = cursor.fetchone()
        if result is None:
            break
        deleted_user_id = result[0]
        cursor.execute("DELETE FROM Account WHERE User_id = ?", (deleted_user_id,))
        cursor.execute("DELETE FROM User WHERE id = ?", (deleted_user_id,))
    return "Deletion complete"


@db_connection
def get_user_transactions(c, user_id):

    # Calculate the date three months ago from today
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)

    # Convert dates to string format for SQL query
    start_date_str = start_date.strftime('%Y-%m-%d %H:%M:%S')
    end_date_str = end_date.strftime('%Y-%m-%d %H:%M:%S')

    query = '''
    SELECT * FROM BankTransaction
    WHERE (Account_sender_id = ? OR Account_receiver_id = ?)
    AND Datetime BETWEEN ? AND ?
    '''
    c.execute(query, (user_id, user_id, start_date_str, end_date_str))
    return c.fetchall()
 