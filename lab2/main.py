import requests

class Films:
    def __init__(self , data, genres):
        print(data['results'])
        self.data = data
        self.films = data['results']
        self.genres = genres['genres']

    def give_all_data(self):
        print(data['results'])

    def give_data_with_index_3_19(self):
        for i in range(3, 19, 4):
            print(self.films[i])

    def the_most_popular(self):
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

    def finde_name_from_discription(self, word):
        film_ind_lst = []
        index = 0
        for f in self.films:
            if word in f['overview']:
                film_ind_lst.append(index)
            index += 1

        print('5.	Names of titles which has in description key words which a user put as parameters')
        for answ in film_ind_lst:
            print(self.films[answ]['original_title'])

    def collection_of_genres(self):
        answer = set()
        for f in self.films:
            answer.add(tuple(f['genre_ids']))

        print('6.	Unique collection of present genres (the collection should not allow inserts)')
        print(answer)

    def delete_film_with_genre(self, id_genre_del):
        ind = 0
        result = []
        for f in self.films:
            if id_genre_del in f['genre_ids']:
                next()
            else:
                result.append(f)

        print('7.	Delete all movies with user provided genre')
        print(result)

'''
    def popular_genres(self):
        dict_times_genres = {}
        for g in self.genres:
        dict_times_genres.update({g['id']}:0)
        print(dict_times_genres)

'''




headers = {
"accept": "application/json",
"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIzMTI3NGFmYTRlNTUyMjRjYzRlN2Q0NmNlMTNkOTZjOSIsInN1YiI6IjVkNmZhMWZmNzdjMDFmMDAxMDU5NzQ4OSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.lbpgyXlOXwrbY0mUmP-zQpNAMCw_h-oaudAJB6Cn5c8"
} # токен для авторизации
respons = requests.get('https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&sort_by=popularity.desc&page=1', headers=headers)  # возвращает json с данными
genres_resp = requests.get('https://api.themoviedb.org/3/genre/movie/list?language=en', headers=headers)
print(respons.json())
print(genres_resp.json())
genre_data = genres_resp.json()
data = respons.json()
print(data.keys())
# import pdb;pdb.set_trace()
answer = Films(data, genre_data)

# 2 answer
answer.give_all_data()
# 3 answers
answer.give_data_with_index_3_19()
# 4 answer
answer.the_most_popular()
# 5 answer
#word = input()
#answer.finde_name_from_discription(word)
# 6 answer
answer.collection_of_genres()
# 7 answer
#id_genre = input()
#answer.delete_film_with_genre(id_genre)
# 8 answer
# answer.popular_genres()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
#print(type(data))