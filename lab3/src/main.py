import argparse
from data_humans import DataHumans


"""
main.py --destination_folder='D:\WinUsers\Lera\Documents\summerlabs\pythonrep\lab3\strang2 ' --file_name=fyufyff2 --gender_filt=male
"""


# использовать argparse
parser = argparse.ArgumentParser()
parser.add_argument("--destination_folder", type=str, required=True)
parser.add_argument("--file_name", type=str, required=True)
parser.add_argument("-g", "--gender_filt", type=str)
parser.add_argument("-n", "--numb_of_rows_filt", type=int)
parser.add_argument("--log_level", type=str)
args = parser.parse_args()

import pdb

pdb.set_trace()

output_file = DataHumans(args.destination_folder, args.file_name)
if args.numb_of_rows_filt is True:
    output_file.delete_rows_for_filt(args.numb_of_rows_filt)
else:
    output_file.filter_by_gender(args.gender_filt)

output_file.add_fields_to_file()
output_file.file_replace()
user_data = output_file.struct_data()
output_file.make_dir_for_decade(user_data)
output_file.remove_data_before()
output_file.for_logging_struct()


# output_file.zip_maker()

# log_lev = input()
# print('Destination folder new ')  # D:\WinUsers\Lera\Documents\summerlabs\pythonrep\lab3\strang
# folder_path = input()
# print('Filename ')
# inp_file_name = input()
#
# output_file = DataHumans(folder_path, inp_file_name)
# print('do you want filter by rows or gender')
# answer = input()
# if answer == 'gender':
#     print('print gender')
#     output_file.filter_by_gender(input())
# if answer == 'rows':
#     print('print numb of delete rows')
#     output_file.delete_rows_for_filt(int(input()))
