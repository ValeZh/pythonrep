from unittest.mock import patch, MagicMock, mock_open, call
import pytest
import os

# import main
from lab3.src.data_humans import DataHumans, my_max

DEST_FOLDER = r'D:\WinUsers\Lera\Documents\summerlabs\pythonrep\lab3\tests\tmp_data'
dest_fname = 'test_file.csv'

# test_dict_1 = [{'gender': 'male',
#                 'name.title': 'Mr',
#                 'name.first': 'Holger',
#                 'name.last': 'Bonke',
#                 'location.country': 'Netherlands',
#                 'dob.date': '1987-08-12T12:51:08.522Z',
#                 'dob.age': '35',
#                 'global_index': 1},
#
#                {'gender': 'female',
#                 'name.title': 'Ms',
#                 'name.first': 'Ilona',
#                 'name.last': 'Halonen',
#                 'location.country': 'Finland',
#                 'dob.date': '1995-03-15T20:05:36.185Z',
#                 'dob.age': '28',
#                  'global_index': 2}]

test_dict_1 = [{'gender': 'male',
                'name.title': 'Monsieur',
                'name.first': 'Mario',
                'name.last': 'Lefebvre',
                'location.country': 'Switzerland',
                'dob.date': '06/21/95',
                'dob.age': '28',
                'global_index': 1},
               {'gender': 'male',
                'name.title': 'Mr',
                'name.first': 'Benjamin',
                'name.last': 'Taylor',
                'location.country': 'Canada',
                'dob.date': '12/08/44',
                'dob.age': '78',
                'global_index': 2}]
path_dict = {'90-th': {'Switzerland': [
    {'gender': 'male',
     'name.title': 'Monsieur',
     'name.first': 'Mario',
     'name.last': 'Lefebvre',
     'location.country': 'Switzerland',
     'dob.date': '06/21/95',
     'dob.age': '28',
     'global_index': 1}]},
    '40-th': {'Canada': [
        {'gender': 'male',
         'name.title': 'Mr',
         'name.first': 'Benjamin',
         'name.last': 'Taylor',
        'location.country': 'Canada',
         'dob.date': '12/08/44',
         'dob.age': '78',
         'global_index': 2}]}}


def setup():
    pass


def teardown():
    if os.path.exists(DEST_FOLDER + '\\' + dest_fname):
        os.remove(DEST_FOLDER + '\\' + dest_fname)


@pytest.fixture(scope='function')
@patch('lab3.src.data_humans.DataHumans.download_data', return_value=test_dict_1)
def dh(mock_1=0):
    return DataHumans(DEST_FOLDER, dest_fname)


def test_my_max():
    assert my_max(1, 2) == 2
    assert my_max(1, 2) != 1


def test_data_humans_init(dh):
    expected = f'{DEST_FOLDER}\\{dest_fname}.csv'
    assert dh.file_out_name == expected
    # assert dh.


def test_numbering_rows(dh):
    input_param_idx = 1
    input_pram_val = {}
    dh.numbering_rows(input_param_idx, input_pram_val)
    assert input_pram_val.get('global_index') == input_param_idx


@patch('csv.DictReader', return_value={'test': 1})
def test_read_data_from_file(dh, mock_DictReader):
    with patch("builtins.open", mock_open(read_data="data")) as mock_file:
        res = dh.read_data_from_file()
        mock_file.assert_called_with(dh.previous_output, "r", encoding="utf-8")
        assert res == ['test']


def test_add_fields_to_file(dh):
    dh.numbering_rows = MagicMock()
    dh.current_time_for_file = MagicMock()
    dh.change_name_title = MagicMock()
    dh.convert_datatime = MagicMock()

    dh.add_fields_to_file()
    assert dh.change_name_title.mock_calls == [call(test_dict_1[0]), call(test_dict_1[1])]



@pytest.mark.parametrize('input_param, expected', [
    ({"name.title": "Mrs"}, {"name.title": "missis"}),
    ({"name.title": "Ms"}, {"name.title": "mister"}),
    ({"name.title": "Madame"}, {"name.title": "mademoiselle"})])
def test_change_name_title(dh, input_param, expected):
    dh.change_name_title(input_param)
    assert input_param == expected


def test_struct_data(dh):
    dh = DataHumans(DEST_FOLDER, dest_fname)
    actual = dh.struct_data()

    expected_data = path_dict
    assert actual == expected_data

