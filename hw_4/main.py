import argparse
import api
import initial_db_setup


def init_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--add_path', type=str)
    parser.add_argument('--table_name', type=str)
    parser.add_argument('--row_id', type=int)
    parser.add_argument('--column', type=str)
    parser.add_argument('--value', type=str)
    parser.add_argument('--delete_row_id', type=int)
    parser.add_argument('--sender_id', type=int)
    parser.add_argument('--receiver_id', type=int)
    parser.add_argument('--sent_currency', type=str)
    parser.add_argument('--sent_amount', type=int)
    parser.add_argument('--time', type=str)
    parser.add_argument('--clear_table', type=str)
    parser.add_argument('--random_disc', type=str)
    args = parser.parse_args()

    return args


def do_func_with_args(args):
    # чтоб можно было выполнять несколько функций
    if args.add_path and args.table_name:
        api.add_table_by_file(args.add_path, args.table_name)
    if args.table_name and args.row_id and args.column and args.value:
        api.update_row(args.table_name, args.row_id, args.column, args.value)
    if args.clear_table:
        api.clear_table(args.clear_table)
    if args.delete_row_id and args.table_name:
        api.delete_row(args.delete_row_id ,args.table_name)
    if args.sender_id and args.receiver_id and args.sent_amount:
        api.transfer_money(args.sender_id, args.receiver_id, args.sent_amount)
    if args.sender_id and args.receiver_id and args.sent_amount and args.time:
        api.transfer_money(args.sender_id, args.receiver_id, args.sent_amount, args.time)
    if args.random_disc:
        print(api.select_random_users_with_discounts())

    print(api.user_with_highest_amount())
    # Пример использования
    print(api.bank_serving_oldest_client())
    print(api.bank_with_biggest_capital())
    print(api.bank_with_highest_unique_users())
    api.print_table("BankTransaction")



def main():
    initial_db_setup.create_database()
    do_func_with_args(init_args())


if __name__ == "__main__":
    main()
