import logging
import requests
import csv
import os
from copy import deepcopy

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
        self.file_out_name = des_fold_path + '/' + f_name + '.csv'
        self.data = self.download_data()
        self.make_dir_output_file(des_fold_path)
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
        return data_dicts

    def make_dir_output_file(self,des_fold_path):
        logging.info('make_dir')
        os.makedirs(des_fold_path)

    def make_output_file(self, gender = 'male'):
        save_output = []

        for row in self.data:
            if row['gender'] == gender:
                save_output.append(deepcopy(row))
        print(type(save_output))
        # with open(self.file_out_name, 'wb') as csv_output:
        #     writer = csv.DictWriter(csv_output, fieldnames=csv_reader)

    def delete_data_file(self):
        path = 'D:\WinUsers\Lera\Documents\summerlabs\pythonrep\lab 3\file.log'
        if os.path.isfile(path):
            os.remove(path)
        else:
            print('Path is not a file')



# print('optional positional argument -- log_level')
# log_lev = input()
# 3 provide following parmetrs (взять один инпут и стрингой записать кучу переменных и их потом распарсить - надо потом попробовать)
print('Destination folder ')#D:\WinUsers\Lera\Documents\summerlabs\pythonrep\lab 3\fortry
folder_path = input()
print('Filename ')
inp_file_name = input()
# print('gender to filter the data by')
# gender_filt = input()
# print('number of rows to filter by')
# numb_of_filter = input()

output_file = Data_Humans(folder_path, inp_file_name)
output_file.make_output_file()

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
