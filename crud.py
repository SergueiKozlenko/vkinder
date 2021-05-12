from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from config import DATABASE_URI
from models import Base, User, UsersSearch, Favorite, BlackList
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

engine = create_engine(DATABASE_URI, pool_pre_ping=True)
Session = sessionmaker(bind=engine)


@contextmanager
def session_scope():
    """Обеспечивает область транзакций c серией операций."""
    session = Session()
    try:
        yield session
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print(e)
        pass
    finally:
        session.close()


def load_users():
    """Возвращает список id пользователей VK из таблицы users."""
    results = []
    with session_scope() as s:
        results = s.query(User.id).all()
    users = [value for value, in results]
    return users


def load_criteria(user_id):
    """Возвращает dict с критериями поиска пользователя user_id из таблицы users."""
    with session_scope() as s:
        user = s.query(User).filter(User.id == user_id).first()
        criteria = {'first_name': user.first_name,
                    'sex': user.sex,
                    'sex_title': user.sex_title,
                    'age_from': user.age_from,
                    'age_to': user.age_to,
                    'city_id': user.city_id,
                    'city_title': user.city_title,
                    'country_id': user.country_id,
                    'status_id': user.status_id,
                    'status_title': user.status_title}
    return criteria


def load_viewed_list(user_id):
    """Возвращает список id просмотренных пользователей VK в текущем поиске
    пользователя user_id из таблицы users.
    """
    results = []
    with session_scope() as s:
        results = s.query(UsersSearch.id).filter(UsersSearch.user_id == user_id).all()
    viewed_list = [value for value, in results]
    return viewed_list


def load_black_list(user_id):
    """Возвращает список id пользователей VK из таблицы black_list для пользователя user_id."""
    results = []
    with session_scope() as s:
        results = s.query(BlackList.id).filter(BlackList.user_id == user_id).all()
    black_list = [value for value, in results]
    return black_list


def load_favorite_list(user_id):
    """Возвращает список id пользователей VK из таблицы favorites для пользователя user_id."""
    results = []
    with session_scope() as s:
        results = s.query(Favorite.id).filter(Favorite.user_id == user_id).all()
    favorite_list = [value for value, in results]
    return favorite_list


def update_sex(user):
    """Обновляет значение столбца sex таблицы users для объекта класса User."""
    with session_scope() as s:
        db_user = s.query(User).filter(User.id == user.id).one()
        db_user.sex = user.criteria['sex']
        db_user.sex_title = user.criteria['sex_title']


def update_age(user):
    """Обновляет значения столбцов age_from, age_to таблицы users для объекта класса User."""
    with session_scope() as s:
        db_user = s.query(User).filter(User.id == user.id).one()
        db_user.age_from = user.criteria['age_from']
        db_user.age_to = user.criteria['age_to']


def update_city(user):
    """Обновляет значения столбцов city_id, city_title таблицы users для объекта класса User."""
    with session_scope() as s:
        db_user = s.query(User).filter(User.id == user.id).one()
        db_user.city_id = user.criteria['city_id']
        db_user.city_title = user.criteria['city_title']


def update_status(user):
    """Обновляет значения столбцов status_id, status_title таблицы users для объекта класса User."""
    with session_scope() as s:
        db_user = s.query(User).filter(User.id == user.id).one()
        db_user.status_id = user.criteria['status_id']
        db_user.status_title = user.criteria['status_title']


def insert_user(user):
    """Добавляет информацию об экземпляре класса User в таблицу users."""
    new_user = User(
        id=user.id,
        first_name=user.first_name,
        max_number=user.max_number,
        sex=user.criteria['sex'],
        sex_title=user.criteria['sex_title'],
        age_from=user.criteria['age_from'],
        age_to=user.criteria['age_to'],
        city_id=user.criteria['city_id'],
        city_title=user.criteria['city_title'],
        country_id=user.criteria['country_id'],
        status_id=user.criteria['status_id'],
        status_title=user.criteria['status_title']
    )
    with session_scope() as s:
        s.add(new_user)


def insert_users_search(user):
    """Добавляет список id просмотренных пользователей VK в текущем поиске
    объекта класса User в таблицу users_search.
    """
    list_for_load = [item for item in user.viewed_list if item not in user.loaded_list]
    for viewed_id in list_for_load:
        users_search = UsersSearch(
            id=viewed_id,
            user_id=user.id
        )
        with session_scope() as s:
            s.add(users_search)
        user.loaded_list.append(viewed_id)


def insert_favorite(user, favorite_user_id):
    """Добавляет id пользователя VK и ID объекта класса User в таблицу favorites."""
    favorite = Favorite(
        id=favorite_user_id,
        user_id=user.id
    )
    with session_scope() as s:
        s.add(favorite)


def insert_black_user(user, black_list_user_id):
    """Добавляет id пользователя VK и ID объекта класса User в таблицу users_search."""
    black_list = BlackList(
        id=black_list_user_id,
        user_id=user.id
    )
    with session_scope() as s:
        s.add(black_list)
        s.query(UsersSearch).filter(UsersSearch.id == black_list_user_id and
                                    UsersSearch.user_id == user.id).delete()


def empty_users_search(user_id):
    """Удаляет из таблицы users_search все записи о просмотренных пользователях VK
    в текущем поиске пользователя user_id.
     """
    with session_scope() as s:
        s.query(UsersSearch).filter(UsersSearch.user_id == user_id).delete()


def recreate_database():
    """Удаляет и создает базу данных vkinder."""
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

# recreate_database()
