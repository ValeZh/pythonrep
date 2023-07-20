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
        for i in range(1, int(self.page)):
            respons = requests.get(
                f'https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&sort_by=popularity.desc&page={i}',
                headers=self.header)  # возвращает json с данными
            self.films.extend(respons.json()['results'])

    def fetch_genre(self):
        genres_resp = requests.get('https://api.themoviedb.org/3/genre/movie/list?language=en', headers=self.header)
        self.genres = genres_resp.json()

    def give_all_data(self):
        return self.films

    # def give_data_with_index_3_19(self):
    #     for i in range(3, 19, 4):#slicing
    #         print(self.films[i])

    def the_most_popular(self):# использовать max lst
        popularity_id = 0
        maximum_film = 0

        print(len(self.films))
        for f in range(len(self.films)):
            if maximum_film < int(self.films[f]['popularity']):
                maximum_film = int(self.films[f]['popularity'])
                popularity_id = f
                print(popularity_id)
                print(maximum_film)

        print(f"4.Name of the most popular title {self.films[popularity_id]['original_title']}")

    def finde_name_from_discription(self, word):# use comprehension
        film_ind_lst = []
        index = 0
        for f in self.films:
            if word in f['overview']:
                film_ind_lst.append(index)
            index += 1

        print('5.	Names of titles which has in description key words which a user put as parameters')
        for answ in film_ind_lst:
            print(self.films[answ]['original_title'])

    def collection_of_genres(self):  # use comprehension
        answer = set()
        for f in self.films:
            answer.add(tuple(f['genre_ids']))

        print('6.	Unique collection of present genres (the collection should not allow inserts)')
        print(answer)
        return answer

    def delete_film_with_genre(self, id_genre_del):# comprehension илиilter
        result = []
        for f in self.films:
            if id_genre_del not in f['genre_ids']:
                result.append(f)

        print('7.	Delete all movies with user provided genre')
        print(result)
        return result

    def popular_genres(self):
        lst_for_count = []
        for f in self.films:#comprehension
            for ids in f['genre_ids']:
                lst_for_count.append(ids)
        cnt = collections.Counter(lst_for_count)

        for g in self.genres:# взять id + name
            if g['id'] == cnt.most_common(3)[0][0] or g['id'] == cnt.most_common(3)[1][0] or g['id'] == \
                    cnt.most_common(3)[2][0]:
                print(g['name'])

        print(cnt.most_common(3))

    def group_films_by_genres(self):
        group_dict = {g['id']: [] for g in self.genres}
        for f in self.films:# [фильм1, фильм2] - пары по жанру
            for g in f['genre_ids']:
                buff = group_dict[g]
                buff.append(f['original_title'])
                group_dict.update({g: buff})
        print(group_dict)

    def copy_data_with_22(self):# deepcopy
        copy_data = self.films

        for f in copy_data:
            f['genre_ids'][0] = 22
        print(copy_data)
        print(self.films)
        return (copy_data)

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
        if sort == 1:
            sorted_list = sorted(result_lst_dic, key=lambda x: x['Score'], x['Popularity'])# сортировка по 2 полям
        print(sorted_list)
        return (sorted_list)

    def csv_file_maker(self, coll_dict):
        with open('lab2.txt', mode='w') as csv_file:
            fieldnames = ['Title', 'Popularity', 'Score', 'Last_day_in_cinema']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()
            for d in coll_dict:
                writer.writerow(d)


# import pdb;pdb.set_trace()
page = input()
answer = Films(page)

# 2 answer
answer.give_all_data()
# 3 answers
#answer.give_data_with_index_3_19()
# 4 answer
#answer.the_most_popular()
# 5 answer
# word = input()
# answer.finde_name_from_discription(word)
# 6 answer
#answer.collection_of_genres()
# 7 answer
# id_genre = input()
# answer.delete_film_with_genre(id_genre)
# 8 answer
#answer.popular_genres()
# 9 answer
#answer.group_films_by_genres()
# 10 answer
answer.copy_data_with_22()
# 11 answer
dict_coll = answer.make_collection(2)
# 12 answer
answer.csv_file_maker(dict_coll)
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
# print(type(data))
