import initial_db_setup as init_db
import argparse
import sqlite3
import requests
import csv

def get_data():
    api_key = 'fca_live_bYExvWei85B5olF2iitYB6HunpYb8RYaZAw29iWt'
    url = f'https://api.freecurrencyapi.com/v1/latest?apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    print(data)
    return data


get_data()


