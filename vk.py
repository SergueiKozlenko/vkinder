import requests as requests
from datetime import datetime


class Vk:
    STATUS = {0: '— не указано',
              1: '— не женат (не замужем)',
              2: '— встречается',
              3: '— помолвлен(-а)',
              4: '— женат (замужем)',
              5: '— всё сложно',
              6: '— в активном поиске',
              7: '— влюблен(-а)',
              8: '— в гражданском браке'
              }

    url = 'https://api.vk.com/method/'

    def __init__(self, vk_token, version):
        """Конструктор класса Vk.
        Примет токен аккаунта Vk, номер версии.
        """
        self.token = vk_token
        self.version = version
        self.params = {
            'access_token': self.token,
            'v': self.version
        }

    @staticmethod
    def get_top_photos(items, top):
        """Примет список объектов фотографий пользователя Vk.
            Возвратит топ три фото по количеству лайков и комментариев в формате {'file_name', 'url'}.
            """
        top_3_photos = []
        file_name_list = []
        sorted_items = sorted(items, key=lambda i: i['likes']['count'] + i['comments']['count'], reverse=True)[:top]
        for item in sorted_items:
            likes = item['likes']['count']
            comments = item['comments']['count']
            file_name = f"{likes + comments}.jpg"
            if file_name in file_name_list:
                file_name = f"{str(likes + comments)}{str(item['date'])}.jpg"
            url = item['sizes'][-1]['url']
            file_name_list.append(file_name)
            top_3_photos.append({'file_name': file_name, 'url': url})
        return top_3_photos

    def get_criteria(self, users_info):
        """Примет dict users_info с информацией о пользователе Vk.
        Возвратит dict с критериями поиска в формате:
        {'first_name', 'sex', 'sex_title', 'age_from', 'age_to', city_id', 'city_title',
        'country_id', 'status_id', 'status_title'}.
        """
        users_age = datetime.now().year - datetime.strptime(users_info['bdate'], "%d.%m.%Y").year
        status_id = int(users_info['status_id']) if users_info['status_id'] else 0
        return {'first_name': users_info['first_name'],
                'sex': 1 if users_info['sex'] == 2 else 2,
                'sex_title': 'женщина' if users_info['sex'] == 2 else 'мужчина',
                'age_from': users_age,
                'age_to': users_age,
                'city_id': users_info['city_id'],
                'city_title': users_info['city_title'],
                'country_id': users_info['country_id'],
                'status_id': status_id,
                'status_title': self.STATUS[status_id]
                }

    def get_cities(self, city_query, country_id):
        """Примет название искомого города city_query, id страны country_id.
        С помощью метода VK API getCities возвратит dict с найденными городами в формате: {'id', 'title'} и
        список списков для клавиатуры бота в формате: ['id-region'] если регион указан и ['title-region'] - если нет.
        """
        get_cities_url = self.url + 'database.getCities'
        get_cities_params = {
            'country_id': country_id,
            'need_all': 0,
            'q': city_query
        }
        response = requests.get(get_cities_url, params={**self.params, **get_cities_params})
        count = response.json()['response']['count']
        cities = response.json()['response']['items']
        if count != 0:
            city_key = [[f"{city['id']}-{city['region'] if 'region' in city.keys() else city['title']}"]
                        for city in cities if city_query.lower() == city['title'].lower()]
            city_dict = {f"{city['id']}": city['title']
                         for city in cities if city_query.lower() == city['title'].lower()}
        else:
            city_key = []
            city_dict = {}
        return city_dict, city_key

    def get_user_info(self, user_id):
        """Примет id пользователя Vk.
        Возвратит информацию о пользователе в формате:
        {'sex', 'bdate', 'city_id', 'city_title', 'country_id', 'status_id', 'first_name'}.
        """
        users_info_url = self.url + 'users.get'
        users_info_params = {
            'user_ids': user_id,
            'fields': 'sex, bdate, city, relation, country'
        }
        response = requests.get(users_info_url, params={**self.params, **users_info_params})
        if response.status_code == 200 and 'error' not in response.json().keys():
            info = response.json()['response'][0]
            sex = info['sex']
            bdate = info['bdate']
            city_id = info['city']['id']
            city_title = info['city']['title']
            country_id = info['country']['id']
            relation = info['relation'] if 'relation' in info.keys() else 0
            first_name = info['first_name']
            return {'sex': sex,
                    'bdate': bdate,
                    'city_id': city_id,
                    'city_title': city_title,
                    'country_id': country_id,
                    'status_id': relation,
                    'first_name': first_name
                    }

        else:
            print(response.json()['error']['error_msg'])
            return

    def search_users(self, criteria, viewed_list, black_list):
        """Примет criteria - критерии поиска, viewed_list - список уже найденных id,
        black_list - черный список id пользователей Vk.
        Найдет помощью метода VK API users.search и возвратит список id пользователей
        с открытым профилем, имеющих фотографии, попадающих в критерии поиска и не находящихся
        в списках viewed_list и black_list.
        """
        search_list = viewed_list
        users_search_url = self.url + 'users.search'
        users_search_params = {'has_photo': 1,
                               'sex': criteria['sex'],
                               'age_from': criteria['age_from'],
                               'age_to': criteria["age_to"],
                               'city': criteria["city_id"],
                               'status': criteria['status_id'],
                               'sort': 0
                               }
        response = requests.get(users_search_url, params={**self.params, **users_search_params})

        items = response.json()['response']['items']
        list_users_id = [item['id'] for item in items if item['is_closed'] is not True
                         and item['id'] not in search_list and item['id'] not in black_list]
        return len(list_users_id), list_users_id

    def get_photos(self, owner_id, album_id=None):
        """Примет ID пользователя Vk и ID альбома, по умолчанию album_id='profile'.
        Возвратит список значений 'items' объекта response метода VK API photos.get.
        """
        users_photos_url = self.url + 'photos.get'
        users_photos_params = {
            'owner_id': owner_id,
            'album_id': 'profile' if album_id is None else album_id,
            'extended': 1
        }
        items = []
        response = requests.get(users_photos_url, params={**self.params, **users_photos_params})
        try:
            items = response.json()['response']['items']
        except KeyError:
            print(response.json()['error']['error_msg'])
        return items
