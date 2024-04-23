import sqlite3

def create_database(unique_constraint):
    # Устанавливаем соединение с базой данных
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()

    # Создаем таблицу Bank
    c.execute('''CREATE TABLE IF NOT EXISTS Bank (
                 id INTEGER PRIMARY KEY,
                 name TEXT NOT NULL UNIQUE)''')

    # Создаем таблицу BankTransaction
    c.execute('''CREATE TABLE IF NOT EXISTS BankTransaction (
                 id INTEGER PRIMARY KEY,
                 Bank_sender_name TEXT NOT NULL,
                 Account_sender_id INTEGER NOT NULL,
                 Bank_receiver_name TEXT NOT NULL,
                 Account_receiver_id INTEGER NOT NULL,
                 Sent_Currency TEXT NOT NULL,
                 Sent_Amount REAL NOT NULL,
                 Datetime TEXT)''')

    # Создаем таблицу User
    if unique_constraint:
        c.execute('''CREATE TABLE IF NOT EXISTS User (
                     Id INTEGER PRIMARY KEY,
                     Name TEXT NOT NULL,
                     Surname TEXT NOT NULL,
                     Birth_day TEXT,
                     Accounts TEXT NOT NULL)''')

    # Создаем таблицу Account
    c.execute('''CREATE TABLE IF NOT EXISTS Account (
                 Id INTEGER PRIMARY KEY,
                 User_id INTEGER NOT NULL,
                 Type TEXT NOT NULL,
                 Account_Number TEXT NOT NULL UNIQUE,
                 Bank_id INTEGER NOT NULL,
                 Currency TEXT NOT NULL,
                 Amount REAL NOT NULL,
                 Status TEXT)''')

    # Фиксируем изменения и закрываем соединение
    conn.commit()
    conn.close()


