import logging
import requests
import csv
import os
from datetime import datetime, timedelta
from statistics import mean
import collections
import shutil

logging.basicConfig(filename='file.log',
                    level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

logging.debug('Debug message')
logging.info('Info message')
logging.warning('Warning message')
logging.error('Error message')
logging.critical('Critical message')
logging.info('1 step')


class Data_Humans:
    def __init__(self, des_fold_path, f_name='output.csv'):
        self.data_file = 'lab3.csv'
        self.des_fold_path = des_fold_path
        self.previous_output = f_name + '.csv'
        self.file_out_name = des_fold_path + "\\" + f_name + '.csv'
        self.data = self.download_data()
        print(self.file_out_name)
        logging.info('Made class : set 	Destination folder and  Filename  ')

    def download_data(self):
        logging.info('1. Downloading data')
        respons = requests.get('https://randomuser.me/api/?results=5000&format=csv')
        open(self.data_file, mode='w', encoding='utf-8').write(respons.text)
        data_dicts = []
        with open(self.data_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                data_dicts.append(row)
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
        self.add_to_output_file([row for row in self.data if row['gender'] == gender])

    def delete_rows_for_filt(self, numb_of_rows=4900):
        logging.info('delete rows filter')
        if numb_of_rows < 5000:
            buf_list = self.data.copy()
            del buf_list[0:numb_of_rows]
            print(len(buf_list))
        else:
            print('too big numb')
        self.add_to_output_file(buf_list)

    def read_data_from_file(self):
        logging.info('4. Read the file and filter data ')
        # data_dicts = []
        with open(self.previous_output, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
        return[row for row in csv_reader]

    def numbering_rows(self):
        logging.info('5.1 add global_index ')
        self.data = self.read_data_from_file()
        counter = 1
        for row in self.data:
            row['global_index'] = counter
            counter += 1

    def current_time_for_file(self):
        logging.info('5.2 add current time')
        for row in self.data:
            list_t = row['location.timezone.offset'].split(':')
            hourt = int(list_t[0])
            minutet = int(list_t[1])
            cur_time = datetime.now() + timedelta(hours=hourt, minutes=minutet)
            row['location.timezone.offset'] = cur_time.strftime('%m-%d-%y , %H:%M:%S')

    def change_name_title(self):
        logging.info('5.3 change_name_title')
        for row in self.data:
            if row['name.title'] == 'Mrs':
                row['name.title'] = 'missis'
            elif row['name.title'] == 'Ms':
                row['name.title'] = 'mister'
            elif row['name.title'] == 'Madame':
                row['name.title'] = 'mademoiselle'

    def convert_datatime(self, name_row, parse_type, output_type):
        logging.info('convert datatime')
        for row in self.data:
            first_data = datetime.strptime(row[name_row], parse_type)
            output_time = first_data.strftime(output_type)
            row[name_row] = output_time

    def add_fields_to_file(self):
        self.numbering_rows()
        self.current_time_for_file()
        self.change_name_title()
        self.convert_datatime('registered.date', '%Y-%m-%dT%H:%M:%S.%fZ', '%m-%d-%y , %H:%M:%S')
        self.convert_datatime('dob.date', '%Y-%m-%dT%H:%M:%S.%fZ', '%m/%d/%y')

    def file_replace(self):
        logging.info('7. Move initial file to the destination folder')
        if os.path.exists(self.file_out_name) == False:
            os.makedirs(self.des_fold_path, mode=777)
            os.replace(self.previous_output, self.file_out_name)
        else:
            self.file_out_name = 'D:\WinUsers\Lera\Documents\summerlabs\pythonrep\lab 3\ ' + self.previous_output
            os.replace(self.previous_output, self.file_out_name)

    def struct_data(self):
        logging.info('8.Rearrange the data to form such structure')
        user = {}
        for i in self.data:
            buff = i['dob.date'].split('/')
            decade = f'{int((int(buff[2])) / 10) * 10}-th'
            user.setdefault(decade, {})  # {страны}

            country = i['location.country']
            user[decade].setdefault(country, [])
            user[decade][country].append(i)
        print(user)
        return user

    def the_most_old(self, user):  # использовать max lst
        print([int(f['dob.age']) for f in user])
        return max([int(f['dob.age']) for f in user])

    def average_year_of_reg(self, user):
        return int(mean([int(inp['registered.age']) for inp in user]))

    def popular_genres(self, user_data):
        lst_for_count = [f['id.name'] for f in user_data]
        return collections.Counter(lst_for_count).most_common(1)[0][0]

    def make_dir_for_decade(self, user_data):
        logging.info('9. 10 . make dir for decade')
        for i in user_data:
            os.makedirs(self.des_fold_path + '\\' + i)
            for c in user_data[i]:
                os.makedirs(self.des_fold_path + '\\' + i + '\\' + c)
                with open(self.des_fold_path + '\\' + i + '\\' + c + '\\' + 'max_age_' + str(
                        self.the_most_old(user_data[i][c])) + '_avg_registered_' + str(
                    self.average_year_of_reg(user_data[i][c])) + '_ popular_id_' + str(
                    self.popular_genres(user_data[i][c])) + '_user_data_' + str(
                    user_data[i][c][0]['global_index']) + '.csv', 'w', encoding='utf-8') as csv_output:
                    writer = csv.DictWriter(csv_output, fieldnames=user_data[i][c][0].keys())
                    writer.writeheader()
                    writer.writerows(user_data[i][c])

    def remove_data_before(self):
        logging.info('12.	Remove the data before 1960-th')
        lsdir = os.listdir(self.des_fold_path)
        for file in lsdir:
            list_t = file.split('-')
            if list_t[0] != self.previous_output and (((int(list_t[0])) // 10) in range(3, 6)):
                shutil.rmtree(self.des_fold_path + '\\' + file)

    def for_logging_struct(self):
        logging.info('12 logging data in struct')
        tree = list(os.walk(self.des_fold_path, topdown=True, onerror=None, followlinks=False))
        counter = 1
        buff = 1
        for i in tree[0][1]:
            logging.info('{\t')
            logging.info(f'\t{i}:')
            logging.info('\t\t{')
            for c in tree[counter][1]:
                logging.info(f'\t\t{c}:')
                logging.info('\t\t\t[')
                if c in tree[counter + buff][0]:
                    for f in tree[counter + buff][2]:
                        logging.info('\t\t\t\t' + f + '}')
                buff += 1
                logging.info('\t\t\t]')
            logging.info('\t\t}')
            counter += buff
            buff = 1
        logging.info('\n }')

    def zip_maker(self):
        logging.info('14 make zip')
        shutil.make_archive(self.des_fold_path, 'zip', '/lab3')


# print('optional positional argument -- log_level')
# log_lev = input()
print('Destination folder new ')  # D:\WinUsers\Lera\Documents\summerlabs\pythonrep\lab3\strang
folder_path = input()
print('Filename ')
inp_file_name = input()

output_file = Data_Humans(folder_path, inp_file_name)
print('do you want filter by rows or gender')
answer = input()
if answer == 'gender':
    print('print gender')
    output_file.filter_by_gender(input())
if answer == 'rows':
    print('print numb of delete rows')
    output_file.delete_rows_for_filt(int(input()))

output_file.add_fields_to_file()
output_file.file_replace()
user_data = output_file.struct_data()
output_file.make_dir_for_decade(user_data)
output_file.remove_data_before()
output_file.for_logging_struct()
# output_file.zip_maker()
