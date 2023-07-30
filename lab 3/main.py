import logging
import requests
import csv
import os
from copy import deepcopy
from datetime import datetime, date, time, timedelta
import time as t
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
    def __init__(self, des_fold_path,f_name = 'output.csv'):
        self.data_file = 'lab3.csv'
        self.des_fold_path = des_fold_path
        self.previous_output = f_name + '.csv'
        self.file_out_name = des_fold_path + "\\" + f_name + '.csv'
        self.data = self.download_data()
        # self.make_dir_output_file(des_fold_path)
        print(self.file_out_name)

    def download_data(self):
        logging.info('download_data')
        respons = requests.get('https://randomuser.me/api/?results=5000&format=csv')
        open(self.data_file , mode='w', encoding='utf-8').write(respons.text)
        data_dicts = []
        with open(self.data_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                data_dicts.append(row)
            print(type(row))
        print(len(data_dicts))
        return data_dicts



    def add_to_output_file(self ,save_output):
        with open(self.previous_output, 'w', encoding='utf-8') as csv_output:
            writer = csv.DictWriter(csv_output, fieldnames=save_output[0].keys())
            writer.writeheader()
            writer.writerows(save_output)

    def filter_by_gender(self, gender = 'male'):
        save_output = []
        for row in self.data:
            print(type(row))
            if row['gender'] == gender:
                save_output.append(deepcopy(row))
        print('type of save_output[0]')
        print(save_output[0])
        self.add_to_output_file(save_output)

    def delete_rows_for_filt(self, numb_of_rows = 4900):
        if numb_of_rows < 5000:
            buf_list = self.data.copy()
            del buf_list[0:numb_of_rows]
            print(len(buf_list))
        else:
            print('too big numb')

        self.add_to_output_file(buf_list)

    def read_data_from_file(self):
        data_dicts = []
        with open(self.previous_output, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                data_dicts.append(row)
        return data_dicts
    def numbering_rows(self):
        self.data = self.read_data_from_file()
        counter = 1
        for row in self.data:
            row['global_index'] = counter
            counter += 1
        print(self.data)
        print(len(self.data))

    def current_time_for_file(self):
        for row in self.data:
            print(row['location.timezone.offset'])
            list_t = row['location.timezone.offset'].split(':')
            hourt = int(list_t[0])
            minutet = int(list_t[1])
            cur_time = datetime.now() + timedelta(hours= hourt, minutes=minutet)
            print(cur_time)
            row['location.timezone.offset'] = cur_time.strftime('%m-%d-%y , %H:%M:%S')
            print(row['location.timezone.offset'])

    def change_name_title(self):
        for row in self.data:
            if row['name.title'] == 'Mrs':
                row['name.title'] = 'missis'
            elif row['name.title'] == 'Ms':
                row['name.title'] = 'mister'
            elif row['name.title'] == 'Madame':
                row['name.title'] = 'mademoiselle'
        print(self.data)

    def convert_datatime(self, name_row, parse_type, output_type):
        for row in self.data:
            first_data = datetime.strptime(row[name_row], parse_type)
            print(type(first_data))
            output_time = first_data.strftime(output_type)
            print(output_time)
            row[name_row] = output_time


    def add_fields_to_file(self):
        self.numbering_rows()
        self.current_time_for_file()
        self.change_name_title()
        self.convert_datatime('registered.date', '%Y-%m-%dT%H:%M:%S.%fZ', '%m-%d-%y , %H:%M:%S')
        self.convert_datatime('dob.date', '%Y-%m-%dT%H:%M:%S.%fZ', '%m/%d/%y')
        print(self.data)

    def file_replace(self):
        if os.path.exists(self.file_out_name) == False:
            os.makedirs(self.des_fold_path, mode=777)
            os.replace(self.previous_output, self.file_out_name)
        else:
            self.file_out_name = 'D:\WinUsers\Lera\Documents\summerlabs\pythonrep\lab 3\ ' + self.previous_output + '.csv'
            os.replace(self.previous_output, self.file_out_name)

    def struct_data(self):
        user = {}
        for i in self.data:
            buff = i['dob.date'].split('/')
            decade = f'{(int(buff[2]) // 10) * 10}-th'
            user.setdefault(decade, {})#{страны}

            country = i['location.country']
            user[decade].setdefault(country, [])
            user[decade][country].append(i)
        print(user)
        return(user)

    def the_most_old(self, user):  # использовать max lst
        return max([f['dob.age'] for f in user])

    def average_year_of_reg(self, user):
        return mean([int(inp['registered.age']) for inp in user])

    def popular_genres(self, user_data):
        lst_for_count = [f['id.name'] for f in user_data ]
        return collections.Counter(lst_for_count).most_common(1)[0][0]

    def make_dir_for_decade(self, user_data):
        print(type(user_data))
        for i in user_data:
            print(user_data[i])
            os.makedirs(self.des_fold_path + '\\' + i)
            for c in user_data[i]:
                print(c)
                os.makedirs(self.des_fold_path + '\\' + i + '\\' + c)
                # for user in user_data[i][c]:
                with open(self.des_fold_path + '\\' + i + '\\' + c + '\\' + 'max_age_' + str(self.the_most_old(user_data[i][c])) + '_avg_registered_' + str(self.average_year_of_reg(user_data[i][c])) + '_ popular_id_'+ str(self.popular_genres(user_data[i][c])) + '_user_data_' + str(user_data[i][c][0]['global_index']) + '.csv', 'w', encoding='utf-8') as csv_output:
                    writer = csv.DictWriter(csv_output, fieldnames=user_data[i][c][0].keys())
                    writer.writeheader()
                    writer.writerows(user_data[i][c])
                    logging.info(self.des_fold_path + '\\' + i + '\\' + c + '\\' + 'max_age_' + str(self.the_most_old(user_data[i][c])) + '_avg_registered_' + str(self.average_year_of_reg(user_data[i][c])) + '_ popular_id_'+ str(self.popular_genres(user_data[i][c])) + '_user_data_' + str(user_data[i][c][0]['global_index']))


    def remove_data_before(self):
        lsdir = os.listdir(self.des_fold_path)
        print('fweubfcuewi')
        for file in lsdir:
            list_t = file.split('-')
            if ((int(list_t[0]))//10) in range(3,6):
                # print(self.des_fold_path + '\\' + file)
                shutil.rmtree(self.des_fold_path + '\\' + file)

    # def for_logging_struct(self):
    #     print(os.walk(self.des_fold_path))

    def zip_maker(self):
        print(shutil.make_archive(self.des_fold_path, 'zip', 'D:\WinUsers\Lera\Documents\summerlabs\pythonrep\lab 3'))

# os.walk() for logs
    # def write_file_in_strange_structure(self):
    #     with open('structured_file.txt', 'w', encoding='utf-8') as txt_file:
            # writer = csv.DictWriter(csv_output, fieldnames=save_output[0].keys())
            # writer.writeheader()
            # writer.writerows(save_output)

    # def make_dir_output_file(self,des_fold_path):
    #     logging.info('make_dir')
    #     os.makedirs(des_fold_path)


# def delete_data_file(self):
    #     path = 'D:\WinUsers\Lera\Documents\summerlabs\pythonrep\lab 3\file.log'
    #     if os.path.isfile(path):
    #         os.remove(path)
    #     else:
    #         print('Path is not a file')



# print('optional positional argument -- log_level')
# log_lev = input()
# 3 provide following parmetrs (взять один инпут и стрингой записать кучу переменных и их потом распарсить - надо потом попробовать)
print('Destination folder new ')#D:\WinUsers\Lera\Documents\summerlabs\pythonrep\lab 3\strang
folder_path = input()
print('Filename ')
inp_file_name = input()
# print('gender to filter the data by')
# gender_filt = input()
# print('number of rows to filter by')
# numb_of_filter = input()
#filt_type = input()
output_file = Data_Humans(folder_path, inp_file_name)
# if type(filt_type) == str
#output_file.filter_by_gender()
output_file.delete_rows_for_filt()
output_file.add_fields_to_file()
# user_data = output_file.file_replace()
user_data = output_file.struct_data()
output_file.make_dir_for_decade(user_data)
output_file.remove_data_before()
# output_file.for_logging_struct()
output_file.zip_maker()
