import sys
from unittest.mock import MagicMock, patch, mock_open, call
import pytest
import requests
from functools import wraps


from api import unpack_to_string, convert_currency, format_data_string, unpack_data
import pytest
import requests
from functools import wraps

def test_unpack_to_string():
    input_data = [(1, 2, 3), (4, 5), (6,)]
    actual = unpack_to_string(input_data)
    expected = '1,2,3,4,5,6'
    assert actual == expected

def test_convert_currency():
    input_data_1 = {'AUD': 1.5087302415, 'BGN': 1.7944802113, 'BRL': 5.1709607454, 'CAD': 1.3662601591, 'CHF': 0.9142001532,
     'CNY': 7.2410307379, 'CZK': 22.7015437907, 'DKK': 6.880361225, 'EUR': 0.9215801687, 'GBP': 0.7851001494,
     'HKD': 7.8098112804, 'HRK': 6.6462708211, 'HUF': 353.9114355311, 'IDR': 15972.272064036, 'ILS': 3.657970377,
     'INR': 82.9986356329, 'ISK': 138.25410507, 'JPY': 156.989784703, 'KRW': 1363.8085527748, 'MXN': 16.7282428767,
     'MYR': 4.7111009312, 'NOK': 10.5840419142, 'NZD': 1.6331801746, 'PHP': 58.1784177311, 'PLN': 3.912080408,
     'RON': 4.5850908988, 'RUB': 89.5966276992, 'SEK': 10.6642017923, 'SGD': 1.3488202508, 'THB': 36.635135533,
     'TRY': 32.2610938602, 'USD': 1, 'ZAR': 18.4172320138}
    input_data_2 = 'USD'
    input_data_3 = 'EUR'
    input_data_4 = 500
    actual = convert_currency(input_data_1, input_data_2, input_data_3, input_data_4 )
    expected = 460.79
    assert actual == expected

def test_string_elements():
    data = [{'a': 23, 'b': 34, 'c': 90}, {'d': 90, 'f': 78, 'g': 54}]
    expected = ('a, b, c', ':a, :b, :c')
    actual = format_data_string(data)
    assert actual == expected

def test_unpack_data():
    input_data = {'name': 'Alice', 'age': 30, 'city': 'Wonderland'}
    expected_result = ['Alice', 30, 'Wonderland']
    result = unpack_data(input_data)
    assert list(result) == expected_result



@patch('api.get_currency_data', return_value={'CNY': 7.2410307379,'USD': 1 })
@patch('api.get_data_by_id', return_value=['Bank1', 'Bank2',400,300,'USD','CNY'])
@patch('api.account_valid', return_value=[540.70, '2024-05-29 17:58:41.245018'])
@patch('api.update_row')
@patch('api.insert_transaction')
def test_transfer_money(mock_f_1, mock_f_2, mock_f_3, mock_f_4, mock_f_5):
    from api import transfer_money
    sender_id = 1
    receiver_id = 3
    sent_amount = 900
    result = transfer_money(sender_id, receiver_id, sent_amount)
    expected_call_func_dict = {'get_currency_data': 1,
                               'get_data_by_id': 2,
                               'account_valid': 1,
                               'update_row': 1,
                               'insert_transaction': 1}
    result_call_func_dict = {'get_currency_data': mock_f_1.call_count,
                             'get_data_by_id': mock_f_2.call_count,
                             'account_valid': mock_f_3.call_count,
                             'update_row': mock_f_4.call_count,
                             'insert_transaction': mock_f_5.call_count}
    assert result == "success"
    assert expected_call_func_dict == result_call_func_dict

def test_set_accounts():
    from api import set_accounts
    cursor = MagicMock()
    data = [{'user_id': '1', 'type': 'credit', 'account_number': 'ID--dcd-123568744-',
             'bank_id': '3', 'currency': 'USD', 'amount': '1000', 'status': 'gold'},
            {'user_id': '3', 'type': 'debit', 'account_number': 'ID--xyz-987654-uvw',
             'bank_id': '2', 'currency': 'USD', 'amount': '500', 'status': 'silver'}]
    set_accounts(cursor, data)
    result = cursor.mock_calls
    expected = [call.execute('SELECT id FROM Account WHERE user_id = ?', ('1',)),
                 call.fetchall(),
                 call.fetchall().__iter__(),
                 call.execute('UPDATE User SET Accounts = ? WHERE id = ?', ('', '1')),
                 call.execute('SELECT id FROM Account WHERE user_id = ?', ('3',)),
                 call.fetchall(),
                 call.fetchall().__iter__(),
                 call.execute('UPDATE User SET Accounts = ? WHERE id = ?', ('', '3'))]
    assert result == expected

@patch('validate.valid_currency_amount', return_value= True)
@patch('api.convert_currency', return_value= 450)
@patch('validate.add_transaction_time', return_value = '2024-05-29 17:58:41.245018')
def test_account_valid(mock_f_1, mock_f_2, mock_f_3):
    from api import account_valid
    result = account_valid(400,300,'USD','CNY',
                           {'CNY': 7.2410307379,'USD': 1 },'2023-05-11 12:33:12.245018')
    expected = (450, '2024-05-29 17:58:41.245018')
    expected_call_func_dict = {'valid_currency_amount': 1, 'convert_currency': 1, 'add_transaction_time': 1}
    result_call_func_dict = {'valid_currency_amount': mock_f_1.call_count,
                             'convert_currency': mock_f_2.call_count, 'add_transaction_time': mock_f_3.call_count}

    print(mock_f_1.call_count)
    assert expected == result
    assert expected_call_func_dict == result_call_func_dict

"""
@patch('api.select_id_from_user', return_value= [(4,), (1,), (3,), (5,), (2,)])
@patch('api.select_id_from_user', return_value=[(4,), (1,), (3,), (5,), (2,)])
def test_select_random_users_with_discounts():
"""

'''
#sys.modules['db_con_decor'] = MagicMock()

def mock_db_connection(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        c = MagicMock()
        result = func(c, *args, **kwargs)

    return wrapper

patch('db_con_deco.db_connection', mock_db_connection).start()

def test_update_row():
    from api import update_row
    cur = MagicMock()
    res = update_row(cur, "User", 1, None, "BUIXGSCG")
    assert res == "success"
    #cur.mock_calls)
'''