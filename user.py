class User:
    """ласса User.
       Примет ID пользователя VK, критерии поиска, максимальное количество загружаемых в чат профилей.
       """
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
    STATUS_LABEL = f"введите значение из списка в формате 'с 6':\n0 — не указано\n1 — не женат (не замужем)\n" \
                   f"2 — встречается\n3 — помолвлен(-а)\n4 — женат (замужем)\n5 — всё сложно\n6 — в активном поиске\n" \
                   f"7 — влюблен(-а)'\n8 — в гражданском браке"

    def __init__(self, user_id, criteria, max_number=None):
        """Конструктор класса User.
           Примет ID пользователя VK, критерии поиска, максимальное количество загружаемых в чат профилей.
           """
        self.id = user_id
        self.count_loaded = 0
        self.count_to_load = 0
        self.viewed_list = []
        self.loaded_list = []
        self.favorite_list = []
        self.black_list = []
        self.first_name = criteria['first_name']
        self.max_number = 5 if max_number is None else max_number
        self.criteria = criteria

    def count_not_viewed(self):
        """Возвратит количество незагруженных в чат профилей пользоватеей в текущем поиске"""
        return self.count_to_load - self.count_loaded

    def change_sex(self):
        """Изменит параметр поиска пол на противоположный в поле класса criteria"""
        self.criteria['sex_title'] = 'женщина' if self.criteria['sex'] == 2 else 'мужчина'
        self.criteria['sex'] = 1 if self.criteria['sex'] == 2 else 2
        return self.criteria

    def change_age(self, age_from, age_to):
        """Изменит параметры поиска возраста в поле класса criteria"""
        self.criteria['age_from'] = age_from
        self.criteria['age_to'] = age_to

    def change_city(self, city_id, city_title):
        """Изменит параметр поиска город в поле класса criteria"""
        self.criteria['city_id'] = int(city_id)
        self.criteria['city_title'] = city_title

    def change_status(self, status):
        """Изменит параметр поиска status - семейное положение, в поле класса criteria"""
        self.criteria['status_id'] = int(status)
        self.criteria['status_title'] = self.STATUS[status]

    def display_criteria(self):
        """Выведет на экран параметры поиска в заданном формате"""
        return f"что ищем:\n{self.criteria['sex_title']}\nвозраст от: {self.criteria['age_from']} " \
               f"до: {self.criteria['age_to']}\n" \
               f"город: {self.criteria['city_title']}\nстатус: {self.STATUS[self.criteria['status_id']]}"

    def clear_black_list_info(self, black_list_user_id):
        """Удалит пользователя из списка просмотров и закрузки в текущем поиске"""
        print('clear_black_list_info')
        if black_list_user_id in self.viewed_list:
            self.viewed_list.remove(black_list_user_id)
        if black_list_user_id in self.loaded_list:
            self.loaded_list.remove(black_list_user_id)
