import collections
import requests
import csv
from datetime import datetime
from copy import deepcopy


# from collections import Counter


class Films:
    def __init__(self, page):
        self.header = {
            "accept": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzMTI3NGFmYTRlNTUyMjRjYzRlN2Q0NmNlMTNkOTZjOSIsInN1YiI6IjVkNmZhMWZmNzdjMDFmMDAxMDU5NzQ4OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.lbpgyXlOXwrbY0mUmP-zQpNAMCw_h-oaudAJB6Cn5c8"
        }
        self.page = page
        self.films = []
        self.genres = []
        self.fetch_data()
        self.fetch_genre()

    def fetch_data(self):
        for i in range(1, int(self.page) + 1):
            respons = requests.get(
                f'https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&sort_by=popularity.desc&page={i}',
                headers=self.header)  # возвращает json с данными
            self.films.extend(respons.json()['results'])

    def fetch_genre(self):
        genres_resp = requests.get('https://api.themoviedb.org/3/genre/movie/list?language=en', headers=self.header)
        self.genres = genres_resp.json()

    def give_all_data(self):
        return self.films

    def give_data_with_index_3_19(self):
        x = slice(3,19,4)
        return self.films[x]

    def the_most_popular(self):# использовать max lst
        most_popular_film = max(self.films, key=lambda x:x['popularity'])['original_title']
        return most_popular_film

    def finde_name_from_discription(self, word = 'planet'):# use comprehension
        lst_with_word = [f['original_title'] for f in self.films if word in f['overview'] ] # f['original_title'] значение котовые возвращается ( for f in self.films) обычный цикл (if word in f['overview']) если выполняется условие lst_with_word.append(f)????
        return lst_with_word


    def collection_of_genres(self):  # use comprehension
        answer = {tuple(f['genre_ids']) for f in self.films }
        return answer

    def delete_film_with_genre(self, id_genre_del):# comprehension или iter, не очень поняла зачем iter
        result = [f for f in self.films if int(id_genre_del) not in f['genre_ids']]
        return result

    def popular_genres(self):
        lst_for_count = [f for f in self.films for ids in f['genre_ids']]
        cnt = collections.Counter(lst_for_count)
        lst_result = [g for g in range(3)]
        for g in self.genres:# взять id + name я не знаю как по другому
            if g['id'] == cnt.most_common(3)[0][0] or g['id'] == cnt.most_common(3)[1][0] or g['id'] == \
                    cnt.most_common(3)[2][0]:
                print(g['name'])

        print(cnt.most_common(3))
        return cnt.most_common(3)


    def group_films_by_genres(self):
        group_films1 = {(f['original_title'],k['original_title']) for f in self.films for k in self.films if list(set(f['genre_ids']) & set(k['genre_ids'])) != []}
        return group_films1


    def copy_data_with_22(self):# deepcopy
        copy_data = deepcopy(self.films)
        for f in copy_data:
            f['genre_ids'][0] = 22
        return copy_data

    def make_collection(self, sort):
        result_lst_dic = []
        buff_dict = {} # named tuple
        for f in self.films:
            title = f['original_title']
            popular = format(f['popularity'], '.1f')
            score = int(f['vote_average'])
            str = f['release_date']
            # vvv = date(0, 2 ,2)
            day = datetime.strptime(str, '%Y-%m-%d').date()
            # f'{str}', '%m-%d-%Y').date()
            buff_dict.update({'Title': title, 'Popularity': popular, 'Score': score, 'Last_day_in_cinema': day})
            unchanged_buff_dic = deepcopy(buff_dict)
            result_lst_dic.append(unchanged_buff_dic)
        print(result_lst_dic)
#        if sort == 1:
#            sorted_list = sorted(result_lst_dic, key=lambda x: x['Score'], x['Popularity'])# сортировка по 2 полям
#        print(sorted_list)
#        return (sorted_list)

    def csv_file_maker(self, coll_dict):
        with open('lab2.txt', mode='w') as csv_file:
            fieldnames = ['Title', 'Popularity', 'Score', 'Last_day_in_cinema']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
#            for d in coll_dict:
#                writer.writerow(d)


# import pdb;pdb.set_trace()
page = input()
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
#print(f'8.	Names of most popular genres with numbers of time they appear in the data {answer.popular_genres()}')
# 9 answer
print(f'9.	Collection of film titles grouped in pairs by common genres{answer.group_films_by_genres()}')
# 10 answer
print(f'10.	Return initial data and copy of initial data where first id in list of film genres was replaced with 22 {answer.copy_data_with_22()}')
# 11 answer
dict_coll = answer.make_collection(2)
# 12 answer
answer.csv_file_maker(dict_coll)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
# print(type(data))
