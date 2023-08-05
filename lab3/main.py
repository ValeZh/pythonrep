import logging
import requests
import csv
import os
from datetime import datetime, timedelta
from statistics import mean
import collections
import shutil
import argparse

logging.basicConfig(filename='file.log',
                    level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

class DataHumans:
    def __init__(self, des_fold_path, f_name='output.csv'):
        self.data_file = 'lab3.csv'
        self.des_fold_path = des_fold_path
        self.previous_output = f_name + '.csv'
        self.file_out_name = os.path.join(des_fold_path, f'{f_name}.csv')
        self.data = self.download_data()
        logging.info('Made class : set 	Destination folder and  Filename  ')

    def download_data(self):
        logging.info('1. Downloading data')
        respons = requests.get('https://randomuser.me/api/?results=5000&format=csv')
        with open(self.data_file, mode='w', encoding='utf-8') as file:
            file.write(respons.text)  # context manager
        with open(self.data_file, 'r', encoding='utf-8') as file:
            data_dicts = list(csv.DictReader(file))
        logging.info(f'downloading correct ,len of file{len(data_dicts)}')
        return data_dicts

    def add_to_output_file(self, save_output):
        with open(self.previous_output, 'w', encoding='utf-8') as csv_output:
            writer = csv.DictWriter(csv_output, fieldnames=save_output[0].keys())
            writer.writeheader()
            writer.writerows(save_output)
            logging.info('add_to_output_file correct')

    def filter_by_gender(self, gender='male'):
        logging.info('filter by gender')
        self.data = [row for row in self.data if row['gender'] == gender]
        self.add_to_output_file(self.data)

    def delete_rows_for_filt(self, numb_of_rows=4900):
        logging.info('delete rows filter')
        if numb_of_rows < 5000:
            self.data = self.data[:numb_of_rows]
        else:
            print('too big numb')
        self.add_to_output_file(self.data)

    def read_data_from_file(self):
        logging.info('4. Read the file and filter data ')
        with open(self.previous_output, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
        return [row for row in csv_reader]

    def numbering_rows(self, idx, value):
        logging.info('5.1 add global_index ')
        value['global_index'] = idx

    def current_time_for_file(self, row):
        logging.info('5.2 add current time')
        hourt, minutet = map(int, row['location.timezone.offset'].split(':'))
        cur_time = datetime.now() + timedelta(hours=hourt, minutes=minutet)
        row['location.timezone.offset'] = cur_time.strftime('%m-%d-%y , %H:%M:%S')

    def change_name_title(self, row):
        logging.info('5.3 change_name_title')
        # match/case
        if row['name.title'] == 'Mrs':
            row['name.title'] = 'missis'
        elif row['name.title'] == 'Ms':
            row['name.title'] = 'mister'
        elif row['name.title'] == 'Madame':
            row['name.title'] = 'mademoiselle'

    def convert_datatime(self, row, name_row, parse_type, output_type):
        logging.info('convert datatime')
        first_data = datetime.strptime(row[name_row], parse_type)
        output_time = first_data.strftime(output_type)
        row[name_row] = output_time

    def add_fields_to_file(self):
        for idx, row in enumerate(self.data):
            self.numbering_rows(idx, row)
            self.current_time_for_file(row)
            self.change_name_title(row)
            self.convert_datatime(row, 'registered.date', '%Y-%m-%dT%H:%M:%S.%fZ', '%m-%d-%y , %H:%M:%S')
            self.convert_datatime(row, 'dob.date', '%Y-%m-%dT%H:%M:%S.%fZ', '%m/%d/%y')

    def file_replace(self):
        logging.info('7. Move initial file to the destination folder')
        if not os.path.exists(self.file_out_name):
            os.makedirs(self.des_fold_path, mode=777)
        os.replace(self.previous_output, self.file_out_name)

    def struct_data(self):
        logging.info('8.Rearrange the data to form such structure')
        user = {}
        for i in self.data:
            buff = i['dob.date'].split('/')
            decade = f'{int((int(buff[2])) / 10) * 10}-th'
            country = i['location.country']

            user.setdefault(decade, {})  # {страны}
            user[decade].setdefault(country, [])
            user[decade][country].append(i)

        return user

    def the_most_old(self, user):  # использовать max lst
        return max([int(f['dob.age']) for f in user])

    def average_year_of_reg(self, user):
        return int(mean([int(inp['registered.age']) for inp in user]))

    def popular_genres(self, user_data):
        lst_for_count = [f['id.name'] for f in user_data]
        return collections.Counter(lst_for_count).most_common(1)[0][0]

    def make_name_of_file(self, basic_path, user_data):
        return f'{basic_path}\\max_age_{str(self.the_most_old(user_data))}_avg_registered_{str(self.average_year_of_reg(user_data))}_ popular_id_{str(self.popular_genres(user_data))}_user_data_{str(user_data[0]["global_index"])}.csv'

    def make_dir_for_decade(self, user_data):
        logging.info('9. 10 . make dir for decade')
        for i in user_data:
            for c in user_data[i]:
                basic_path = f'{self.des_fold_path}\\{i}\\{c}'
                os.makedirs(basic_path)  # f-string \\ make variable//make func
                with open(self.make_name_of_file(basic_path, user_data[i][c]), 'w', encoding='utf-8') as csv_output:
                    writer = csv.DictWriter(csv_output, fieldnames=user_data[i][c][0].keys())
                    writer.writeheader()
                    writer.writerows(user_data[i][c])

    def remove_data_before(self):
        logging.info('12.	Remove the data before 1960-th')
        lsdir = os.listdir(self.des_fold_path)
        for file in lsdir:
            list_t = file.split('-')
            if list_t[0] != self.previous_output and (((int(list_t[0])) // 10) in range(3, 6)):
                shutil.rmtree(os.path.join(self.des_fold_path, file))  # os.path.join

    def for_logging_struct(self):
        logging.info('12 logging data in struct')
        tree = list(os.walk(self.des_fold_path, topdown=True, onerror=None, followlinks=False))
        initial_numb = len(tree[0][0].split('\\'))
        for i in tree:
            numb_of_pass = len(i[0].split('\\')) - initial_numb
            x = '\t' * numb_of_pass
            logging.info(('\t' * (numb_of_pass - 1)) + (i[0].split("\\")[-1]))
            logging.info(f'{x}{i[2]}')

    def zip_maker(self):
        logging.info('14 make zip')
        shutil.make_archive(self.des_fold_path, 'zip', '/lab3')


# использовать argparse
parser = argparse.ArgumentParser()
parser.add_argument('destination_folder', type=str)
parser.add_argument('file_name', type=str)
parser.add_argument('-g', '--gender_filt', type=str)
parser.add_argument('-n', '--numb_of_rows_filt', type=int)
parser.add_argument('--log_level', type=str)
args = parser.parse_args()
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



