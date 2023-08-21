import collections
import requests
import csv
from datetime import datetime, timedelta
from copy import deepcopy



class Films:
    def __init__(self, numb_page):
        self.header = {
            'accept': 'application/json',
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzMTI3NGFmYTRlNTUyMjRjYzRlN2Q0NmNlMTNkOTZjOSIsInN1YiI6IjVkNmZhMWZmNzdjMDFmMDAxMDU5NzQ4OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.lbpgyXlOXwrbY0mUmP-zQpNAMCw_h-oaudAJB6Cn5c8'
        }
        self.page = numb_page
        self.films = []
        self.genres = []
        self.fetch_data()
        self.fetch_genre()

    def fetch_data(self):
        for i in range(1, self.page + 1):
            respons = requests.get(
                f'https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&sort_by=popularity.desc&page={i}',
                headers=self.header)
            self.films.extend(respons.json()['results'])

    def fetch_genre(self):
        genres_resp = requests.get('https://api.themoviedb.org/3/genre/movie/list?language=en', headers=self.header)
        self.genres = genres_resp.json()

    def give_all_data(self):
        return self.films

    def give_data_with_index_3_19(self):
        return self.films[3:19:4]

    def the_most_popular(self):
        return max(self.films, key=lambda x: x['popularity'])['original_title']

    def finde_name_from_discription(self, word='planet'):
        return [f['original_title'] for f in self.films if word in f['overview']]

    def collection_of_genres(self):
        return frozenset(n for f in self.films for n in f['genre_ids'])

    def delete_film_with_genre(self, id_genre_del):
        return [f for f in self.films if int(id_genre_del) not in f['genre_ids']]

    def popular_genres(self):
        lst_for_count = [ids for f in self.films for ids in f['genre_ids']]
        cnt = collections.Counter(lst_for_count).most_common(3)
        x = {i['id']: i['name'] for i in self.genres}
        most_genre = [(x[i[0]], i[1]) for i in cnt]
        return most_genre

    def group_films_by_genres(self):
        return {(f['original_title'], k['original_title']) for idx, f in enumerate(self.films) for k in self.films[idx:] if
                        set(f['genre_ids']) & set(k['genre_ids'])}

    @staticmethod
    def change_22_for_map(x):
        x['genre_ids'][0] = 22
        return x

    def copy_data_with_22(self):
        return list(map(self.change_22_for_map, deepcopy(self.films)))

    @staticmethod
    def make_dict(f):
        title = f['original_title']
        popular = format(f['popularity'], '.1f')
        score = int(f['vote_average'])
        realase = f['release_date']
        day = datetime.strptime(realase, '%Y-%m-%d') + timedelta(weeks=8)
        return {'Title': title, 'Popularity': popular, 'Score': score, 'Last_day_in_cinema': day}

    def make_collection(self):
        result_lst_dic = [self.make_dict(f) for f in self.films]
        print(result_lst_dic)
        sorted_list = sorted(result_lst_dic, key=lambda x: (x['Score'], x['Popularity']))
        print(sorted_list)
        return sorted_list

    @staticmethod
    def csv_file_maker(coll_dict):
        with open('lab2.txt', mode='w') as csv_file:
            fieldnames = ['Title', 'Popularity', 'Score', 'Last_day_in_cinema']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            writer.writerows(coll_dict)



print('Write number of page')
page = int(input())
answer = Films(page)

# 2 answer
print(f'2.	Give a user all data {answer.give_all_data()}')
# 3 answers
print(f'3.	All data about movies with indexes from 3 till 19 with step 4 {answer.give_data_with_index_3_19()}')
# 4 answer
print(f'4.	Name of the most popular title {answer.the_most_popular()}')
# 5 answer
word = input()
print(f'5.	Names of titles which has in description key words which a user put as parameters {answer.finde_name_from_discription(word)}')
# 6 answer
print(answer.collection_of_genres())
# 7 answer
id_genre = input()
print(f'7.	Delete all movies with user provided genre{answer.delete_film_with_genre(id_genre)}')
# 8 answer
print(f'8.	Names of most popular genres with numbers of time they appear in the data {answer.popular_genres()}')
# 9 answer
print(f'9.	Collection of film titles grouped in pairs by common genres{answer.group_films_by_genres()}')
# 10 answer
print(
    f'10.	Return initial data and copy of initial data where first id in list of film genres was replaced with 22 {answer.copy_data_with_22()}')
# 11 answer
dict_coll = answer.make_collection()
# 12 answer
answer.csv_file_maker(dict_coll)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
# print(type(data))
