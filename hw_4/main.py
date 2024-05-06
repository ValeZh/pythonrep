import argparse
import api
import initial_db_setup

initial_db_setup.create_database()
parser = argparse.ArgumentParser()
parser.add_argument('--bank_path', type=str)
parser.add_argument('--user_path', type=str)
parser.add_argument('--account_path', type=str)
parser.add_argument('--table_name', type=str)
parser.add_argument('--row_id', type=int)
parser.add_argument('--column', type=str)
parser.add_argument('--value', type=str)
parser.add_argument('--delete_user', type=int)
parser.add_argument('--delete_bank', type=int)
parser.add_argument('--delete_account', type=int)
parser.add_argument('--sender_id', type=int)
parser.add_argument('--receiver_id', type=int)
parser.add_argument('--sent_currency', type=str)
parser.add_argument('--sent_amount', type=int)
parser.add_argument('--time', type=str)
args = parser.parse_args()



#чтоб можно было выполнять несколько функций
if args.bank_path:
    api.add_bank_by_file(args.bank_path)
if args.account_path:
    api.add_account_by_file(args.account_path)
if args.user_path:
    api.add_user_by_file(args.user_path)
if args.table_name and args.row_id and args.column and args.value:
    api.change_something(args.table_name, args.row_id, args.column, args.value)
if args.delete_user:
    print(api.delete_row_from_user(args.delete_user))
if args.delete_account:
    print(api.delete_row_from_account(args.delete_account))
if args.delete_bank:
    print(api.delete_row_from_bank(args.delete_bank))
if args.sender_id and args.receiver_id and args.sent_currency and args.sent_amount:
    api.transfer_money(args.sender_id, args.receiver_id, args.sent_currency, args.sent_amount)
if args.sender_id and args.receiver_id and args.sent_currency and args.sent_amount and args.time:
    api.transfer_money(args.sender_id, args.receiver_id, args.sent_currency, args.sent_amount, args.time)

#api.add_account_by_file(args.account_path)
"""
parser = argparse.ArgumentParser()
#group = parser.add_mutually_exclusive_group()
parser.add_argument('--bankname', type=str, nargs="+")
parser.add_argument('--user_full_name', type=str, nargs="+")
parser.add_argument('--birthday', type=str, nargs="+")
parser.add_argument('--accounts', type=str, nargs="+")
#group.add_argument('--csvpath', type=str)
args = parser.parse_args()

if args.bankname:
    print(args.bankname)
    "python main.py --bankname TestBank "
    print(api.add_bank(args.bankname))
elif args.user_full_name and args.birthday  and args.accounts :
    print(api.add_user(args.user_full_name, args.birthday, args.accounts))

test = ['Lena Zhelezo', '13.01.2005', 1]
print(api.add_user(test[0], test[1], test[2]))
"""

