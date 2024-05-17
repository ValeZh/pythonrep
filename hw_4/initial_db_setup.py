import sqlite3


def create_database(unique_name=True, unique_surname=True):
    # Establishing a connection to the database
    conn = sqlite3.connect('bank.db')
    c = conn.cursor()

    # Create table Bank
    c.execute('''CREATE TABLE IF NOT EXISTS Bank (
                 id INTEGER PRIMARY KEY,
                 name TEXT NOT NULL UNIQUE)''')

    # Create table BankTransaction
    c.execute('''CREATE TABLE IF NOT EXISTS BankTransaction (
                 id INTEGER PRIMARY KEY,
                 Bank_sender_name TEXT NOT NULL,
                 Account_sender_id INTEGER NOT NULL,
                 Bank_receiver_name TEXT NOT NULL,
                 Account_receiver_id INTEGER NOT NULL,
                 Sent_Currency TEXT NOT NULL,
                 Sent_Amount REAL NOT NULL,
                 Datetime TEXT)''')

    # Create table User
    name_uniq = "UNIQUE" if unique_name else ""
    surname_uniq = "UNIQUE" if unique_surname else ""
    c.execute(f'''CREATE TABLE IF NOT EXISTS User (
                 Id INTEGER PRIMARY KEY,
                 Name TEXT NOT NULL {name_uniq},
                 Surname TEXT NOT NULL {surname_uniq},
                 Birth_day TEXT,
                 Accounts INTEGER NOT NULL)''')

    # Create table Account
    c.execute('''CREATE TABLE IF NOT EXISTS Account (
                 Id INTEGER PRIMARY KEY,
                 User_id INTEGER NOT NULL,
                 Type TEXT NOT NULL,
                 Account_Number TEXT NOT NULL UNIQUE,
                 Bank_id INTEGER NOT NULL,
                 Currency TEXT NOT NULL,
                 Amount REAL NOT NULL,
                 Status TEXT)''')

    conn.commit()
    conn.close()
