import argparse
from data_humans import DataHumans


"""
main.py --destination_folder='D:\WinUsers\Lera\Documents\summerlabs\pythonrep\lab3\strang2 ' --file_name=fyufyff2 --gender_filt=male
"""


# использовать argparse
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
parser.add_argument("destination_folder", type=str, required=True)
parser.add_argument("file_name", type=str, required=True)
group.add_argument("--gender_filt", type=str, required=True)
group.add_argument("--numb_of_rows_filt", type=int, required=True)
parser.add_argument("log_level", type=str)
args = parser.parse_args()

import pdb

pdb.set_trace()

output_file = DataHumans(args.destination_folder, args.file_name)
output_file.delete_rows_for_filt(args.numb_of_rows_filt) if args.numb_of_rows_filt else output_file.filter_by_gender(args.gender_filt)

output_file.add_fields_to_file()
output_file.file_replace()
user_data = output_file.struct_data()
output_file.make_dir_for_decade(user_data)
output_file.remove_data_before()
output_file.for_logging_struct()
# output_file.zip_maker()

