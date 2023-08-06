from unittest.mock import patch, MagicMock, mock_open
import pytest
import os

# import main
from src.data_humans import my_max
from src.data_humans import DataHumans

dest_folder = r'D:\WinUsers\Lera\Documents\summerlabs\pythonrep\lab3\tests\tmp_data'
dest_fname = 'test_file.csv'

test_dict_1 = [{'gender': 'male',
                'name.title': 'Mr',
                'name.first': 'Holger',
                'name.last': 'Bonke',
                'location.street.number': '8694',
                'location.street.name': 'Anlooerweg',
                'location.city': 'Vrouwenpolder',
                'location.state': 'Groningen',
                'location.country': 'Netherlands',
                'location.postcode': '9781 MD',
                'location.coordinates.latitude': '-62.2010',
                'location.coordinates.longitude': '93.8340',
                'location.timezone.offset': '-9:00',
                'location.timezone.description': 'Alaska',
                'email': 'holger.bonke@example.com',
                'login.uuid': 'ed26e7aa-c2db-42b8-aad8-cbf3e8cf0a4f',
                'login.username': 'orangepanda569',
                'login.password': 'nemesis',
                'login.salt': 'mi6O7psA',
                'login.md5': 'e4773fb9eb296d9efbd9cc06ac43efdc',
                'login.sha1': 'a6dadd6d86b90cec81d4e6b9718dc18df51c6999',
                'login.sha256': '7d8cb9b03278b896bfb5f9139eca7b11bc9ea7ebc9c7daa91d36e1ba138283f5',
                'dob.date': '1987-08-12T12:51:08.522Z',
                'dob.age': '35',
                'registered.date': '2004-06-24T05:13:43.431Z',
                'registered.age': '19',
                'phone': '(0426) 577993',
                'cell': '(06) 47418893',
                'id.name': 'BSN',
                'id.value': '09860997',
                'picture.large': 'https://randomuser.me/api/portraits/men/53.jpg',
                'picture.medium': 'https://randomuser.me/api/portraits/med/men/53.jpg',
                'picture.thumbnail': 'https://randomuser.me/api/portraits/thumb/men/53.jpg',
                'nat': 'NL',
                'global_index': 1},

               {'gender': 'female',
                'name.title': 'Ms',
                'name.first': 'Ilona',
                'name.last': 'Halonen',
                'location.street.number': '4450',
                'location.street.name': 'Hämeenkatu',
                'location.city': 'Ii',
                'location.state': 'Kainuu',
                'location.country': 'Finland',
                'location.postcode': '42502',
                'location.coordinates.latitude': '-32.9030',
                'location.coordinates.longitude': '-90.1288',
                'location.timezone.offset': '-9:00',
                'location.timezone.description': 'Alaska',
                'email': 'ilona.halonen@example.com',
                'login.uuid': '171d8eee-d30f-4237-81ba-06091d1f9b71',
                'login.username': 'ticklishcat122',
                'login.password': 'septembe',
                'login.salt': 'VPHdDe9e',
                'login.md5': '9153999ad1b5e4466e77cecc0b854fbc',
                'login.sha1': '74c3181c14e8e73cd2dd200b705fbe860a0d9f54',
                'login.sha256': '296029ad86c5b7f00999fc2e83a177e94d2cf8529cc75b1964562822d35e120d',
                'dob.date': '1995-03-15T20:05:36.185Z',
                'dob.age': '28',
                'registered.date': '2013-09-07T14:03:08.075Z',
                'registered.age': '9',
                'phone': '08-835-597',
                'cell': '047-008-48-89',
                'id.name': 'HETU',
                'id.value': 'NaNNA050undefined',
                'picture.large': 'https://randomuser.me/api/portraits/women/19.jpg',
                'picture.medium': 'https://randomuser.me/api/portraits/med/women/19.jpg',
                'picture.thumbnail': 'https://randomuser.me/api/portraits/thumb/women/19.jpg',
                'nat': 'FI', 'global_index': 2}]

test_dict_1 = [{'gender': 'male', 'name.title': 'Monsieur', 'name.first': 'Mario', 'name.last': 'Lefebvre',
                'location.street.number': '6527', 'location.street.name': 'Avenue Joliot Curie',
                'location.city': 'Bleienbach', 'location.state': 'Valais', 'location.country': 'Switzerland',
                'location.postcode': '9995', 'location.coordinates.latitude': '-56.8855',
                'location.coordinates.longitude': '-170.4571', 'location.timezone.offset': '+3:30',
                'location.timezone.description': 'Tehran', 'email': 'mario.lefebvre@example.com',
                'login.uuid': '214e5463-6545-4c3b-8830-b0c120afc472', 'login.username': 'whiteswan503',
                'login.password': 'connie', 'login.salt': 'RQp2tXb2', 'login.md5': '05297d0c0ec2257d00a360f51d3e1944',
                'login.sha1': '5e8d7eb1f827bb17083bc4e8390e1f79d205fc9f',
                'login.sha256': '0d7a8cda0dc1501a066951cad9fd6d07f8721f8e1f98bb5e047ed36be228f487',
                'dob.date': '06/21/95',
                'dob.age': '28', 'registered.date': '12-10-12T11:56:27', 'registered.age': '10',
                'phone': '078 315 40 76',
                'cell': '078 795 90 57', 'id.name': 'AVS', 'id.value': '756.3769.0130.17',
                'picture.large': 'https://randomuser.me/api/portraits/men/67.jpg',
                'picture.medium': 'https://randomuser.me/api/portraits/med/men/67.jpg',
                'picture.thumbnail': 'https://randomuser.me/api/portraits/thumb/men/67.jpg', 'nat': 'CH',
                'global_index': 1},
               {'gender': 'male', 'name.title': 'Mr', 'name.first': 'Benjamin', 'name.last': 'Taylor',
                'location.street.number': '7777', 'location.street.name': 'Balmoral St', 'location.city': 'St. George',
                'location.state': 'New Brunswick', 'location.country': 'Canada', 'location.postcode': 'I8S 9F7',
                'location.coordinates.latitude': '32.3391', 'location.coordinates.longitude': '-171.0365',
                'location.timezone.offset': '+9:30', 'location.timezone.description': 'Adelaide, Darwin',
                'email': 'benjamin.taylor@example.com', 'login.uuid': '3bfad79c-7be0-4237-a0ac-aa00273632f2',
                'login.username': 'sadduck100', 'login.password': 'abgrtyu', 'login.salt': 'VYeIV5tQ',
                'login.md5': '33bd33956731741ad6148344aae674e7',
                'login.sha1': '40ddf3a1c785539eb5ad0cea9835ae6b4b9ef870',
                'login.sha256': '34330c585760496bf51cd590cf1bb6b4afa8005bea36969ba6ca80921599171b',
                'dob.date': '12/08/44',
                'dob.age': '78', 'registered.date': '12-13-04 , 07:24:16', 'registered.age': '18',
                'phone': 'M24 F02-2688',
                'cell': 'I83 J35-9426', 'id.name': 'SIN', 'id.value': '005768908',
                'picture.large': 'https://randomuser.me/api/portraits/men/59.jpg',
                'picture.medium': 'https://randomuser.me/api/portraits/med/men/59.jpg',
                'picture.thumbnail': 'https://randomuser.me/api/portraits/thumb/men/59.jpg', 'nat': 'CA',
                'global_index': 2}]
path_dict = {'90-th': {'Switzerland': [{'gender': 'male', 'name.title': 'Monsieur', 'name.first': 'Mario', 'name.last': 'Lefebvre', 'location.street.number': '6527', 'location.street.name': 'Avenue Joliot Curie', 'location.city': 'Bleienbach', 'location.state': 'Valais', 'location.country': 'Switzerland', 'location.postcode': '9995', 'location.coordinates.latitude': '-56.8855', 'location.coordinates.longitude': '-170.4571', 'location.timezone.offset': '+3:30', 'location.timezone.description': 'Tehran', 'email': 'mario.lefebvre@example.com', 'login.uuid': '214e5463-6545-4c3b-8830-b0c120afc472', 'login.username': 'whiteswan503', 'login.password': 'connie', 'login.salt': 'RQp2tXb2', 'login.md5': '05297d0c0ec2257d00a360f51d3e1944', 'login.sha1': '5e8d7eb1f827bb17083bc4e8390e1f79d205fc9f', 'login.sha256': '0d7a8cda0dc1501a066951cad9fd6d07f8721f8e1f98bb5e047ed36be228f487', 'dob.date': '06/21/95', 'dob.age': '28', 'registered.date': '12-10-12T11:56:27', 'registered.age': '10', 'phone': '078 315 40 76', 'cell': '078 795 90 57', 'id.name': 'AVS', 'id.value': '756.3769.0130.17', 'picture.large': 'https://randomuser.me/api/portraits/men/67.jpg', 'picture.medium': 'https://randomuser.me/api/portraits/med/men/67.jpg', 'picture.thumbnail': 'https://randomuser.me/api/portraits/thumb/men/67.jpg', 'nat': 'CH', 'global_index': 1}]}, '40-th': {'Canada': [{'gender': 'male', 'name.title': 'Mr', 'name.first': 'Benjamin', 'name.last': 'Taylor', 'location.street.number': '7777', 'location.street.name': 'Balmoral St', 'location.city': 'St. George', 'location.state': 'New Brunswick', 'location.country': 'Canada', 'location.postcode': 'I8S 9F7', 'location.coordinates.latitude': '32.3391', 'location.coordinates.longitude': '-171.0365', 'location.timezone.offset': '+9:30', 'location.timezone.description': 'Adelaide, Darwin', 'email': 'benjamin.taylor@example.com', 'login.uuid': '3bfad79c-7be0-4237-a0ac-aa00273632f2', 'login.username': 'sadduck100', 'login.password': 'abgrtyu', 'login.salt': 'VYeIV5tQ', 'login.md5': '33bd33956731741ad6148344aae674e7', 'login.sha1': '40ddf3a1c785539eb5ad0cea9835ae6b4b9ef870', 'login.sha256': '34330c585760496bf51cd590cf1bb6b4afa8005bea36969ba6ca80921599171b', 'dob.date': '12/08/44', 'dob.age': '78', 'registered.date': '12-13-04 , 07:24:16', 'registered.age': '18', 'phone': 'M24 F02-2688', 'cell': 'I83 J35-9426', 'id.name': 'SIN', 'id.value': '005768908', 'picture.large': 'https://randomuser.me/api/portraits/men/59.jpg', 'picture.medium': 'https://randomuser.me/api/portraits/med/men/59.jpg', 'picture.thumbnail': 'https://randomuser.me/api/portraits/thumb/men/59.jpg', 'nat': 'CA', 'global_index': 2}]}}

def setup():
    pass


def teardown():
    if os.path.exists(dest_folder + '\\' + dest_fname):
        os.remove(dest_folder + '\\' + dest_fname)


def test_my_max():
    assert my_max(1, 2) == 2
    assert my_max(1, 2) != 1


@patch('src.data_humans.DataHumans.download_data', return_value=test_dict_1)
def test_DataHumans_init(mock_download_data):
    dh = DataHumans(dest_folder, dest_fname)
    """
        def __init__(self, des_fold_path, f_name="output.csv"):
    self.data_file = "../lab3.csv"
    self.des_fold_path = des_fold_path
    self.previous_output = f_name + ".csv"
    self.file_out_name = os.path.join(des_fold_path, f"{f_name}.csv")
    self.data = self.download_data()
    logging.info("Made class : set 	Destination folder and  Filename  ")
    """

    assert dh.data_file == "../lab3.csv"
    assert dh.des_fold_path == dest_folder
    # assert dh.


@patch('src.data_humans.DataHumans.download_data', return_value=test_dict_1)
def test_numbering_rows(mock_download_data):
    input_param_idx = 1
    input_pram_val = {}
    dh = DataHumans(dest_folder, dest_fname)
    dh.numbering_rows(input_param_idx, input_pram_val)
    assert input_pram_val.get('global_index') is not None
    assert input_pram_val.get('global_index') == input_param_idx


@patch('src.data_humans.DataHumans.download_data', return_value=test_dict_1)
@patch('csv.DictReader', return_value={'test': 1})
def test_read_data_from_file(mock_download_data, mock_DictReader):
    dh = DataHumans(dest_folder, dest_fname)
    with patch("builtins.open", mock_open(read_data="data")) as mock_file:
        res = dh.read_data_from_file()
        mock_file.assert_called_with(dh.previous_output, "r", encoding="utf-8")
        assert res == ['test']


@patch('src.data_humans.DataHumans.download_data', return_value=test_dict_1)
def test_add_fields_to_file(mock_download_data):
    dh = DataHumans(dest_folder, dest_fname)
    assert dh.data == test_dict_1

    dh.numbering_rows = MagicMock()
    dh.current_time_for_file = MagicMock()
    dh.change_name_title = MagicMock()
    dh.convert_datatime = MagicMock()

    dh.add_fields_to_file()
    assert dh.numbering_rows.call_count == len(test_dict_1)
    assert dh.current_time_for_file.call_count == len(test_dict_1)
    assert dh.change_name_title.call_count == len(test_dict_1)
    assert dh.convert_datatime.call_count == len(test_dict_1) * 2


@patch('src.data_humans.DataHumans.download_data', return_value=test_dict_1)
def test_change_name_title(mock_download_data):
    dh = DataHumans(dest_folder, dest_fname)

    row = {"name.title": "Mrs"}
    dh.change_name_title(row)
    assert row["name.title"] == "missis"
    row = {"name.title": "Ms"}
    dh.change_name_title(row)
    assert row["name.title"] == "mister"
    row = {"name.title": "Madame"}
    dh.change_name_title(row)
    assert row["name.title"] == "mademoiselle"


@patch('src.data_humans.DataHumans.download_data', return_value=test_dict_1)
def test_struct_data(mock_download_data):
    expected_data = str(path_dict)

    dh = DataHumans(dest_folder, dest_fname)
    expect = dh.struct_data()
    assert str(expect) == expected_data

# @patch('src.data_humans.DataHumans.download_data', return_value=test_dict_1)
# def test_make_dir_for_decade(mock_download_data, path_dict):
#     dh = DataHumans(dest_folder, dest_fname)
#     dh.make_name_of_file = MagicMock()
#     with patch("builtins.open", mock_open(read_data="data")) as mock_file:
#         res = dh.read_data_from_file()
#         mock_file.assert_called_with(dh.previous_output, "r", encoding="utf-8")
#         assert res == ['test']