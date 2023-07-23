import logging
import requests
import csv

logging.basicConfig(filename='file.log',
                    level=logging.DEBUG,
                    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

logging.debug('Debug message')
logging.info('Info message')
logging.warning('Warning message')
logging.error('Error message')
logging.critical('Critical message')
logging.info('1 step')

respons = requests.get('https://randomuser.me/api/?results=5000&format=csv')
open('lab2.csv', mode='wb').write(respons.content)

# 3 provide following parmetrs (взять один инпут и стрингой записать кучу переменных и их потом распарсить - надо потом попробовать)
print('Destination folder ')
folder_path = input()
print('Filename ')
inp_file_name = input()
print('gender to filter the data by')
gender_filt = input()
print('number of rows to filter by')
numb_of_filter = input()
print('optional positional argument -- log_level')
log_lev = input()

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
