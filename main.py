import re
from vk_api.longpoll import VkLongPoll, VkEventType
import crud
from buttons import start_button, continue_button, change_criteria_button
from patterns import age_pattern, city_pattern, id_city_pattern, status_pattern, id_reply_pattern
from vk import Vk
from vk_bot import VkBot
from user import User
from config import VK_TOKEN, VK_BOT_TOKEN


def clear_current_search_data(user, step=None):
    user.viewed_list.clear()
    user.loaded_list.clear()
    crud.empty_users_search(user.id)
    user.count_loaded = 0
    if step == 1:
        user.count_to_load = 0


def main():
    vk = Vk(VK_TOKEN, '5.130')
    vk_bot = VkBot(VK_BOT_TOKEN)

    start_key = vk_bot.get_keyboard(start_button)
    continue_key = vk_bot.get_keyboard(continue_button)
    change_criteria_key = vk_bot.get_keyboard(change_criteria_button)

    database_users = crud.load_users()
    users = []
    city_dict = {}
    criteria = {}

    long_poll = VkLongPoll(vk_bot.session)
    for event in long_poll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()

                if request == "привет":
                    flag = 0
                    for user_id in database_users:
                        if user_id == event.user_id:
                            criteria = crud.load_criteria(event.user_id)
                            flag = 1
                            break
                    if flag == 0:
                        info = vk.get_user_info(event.user_id)
                        user = User(event.user_id, vk.get_criteria(info))
                        users.append(user)
                        crud.insert_user(user)
                        user.count_to_load, target_users = vk.search_users(user.criteria, user.viewed_list,
                                                                           user.black_list)
                        vk_bot.send_message(event.user_id, f"привет {user.first_name}, "
                                                           f"нашел для тебя {user.count_to_load} пользователей\n ")
                        vk_bot.send_message(event.user_id, user.display_criteria())
                        vk_bot.send_message(event.user_id, "сделай выбор:", start_key)
                    elif flag == 1:
                        user = User(event.user_id, criteria)
                        user.viewed_list = crud.load_viewed_list(event.user_id)
                        user.loaded_list = user.viewed_list.copy()
                        user.black_list = crud.load_black_list(event.user_id)
                        user.favorite_list = crud.load_favorite_list(event.user_id)
                        user.count_to_load, target_users = vk.search_users(user.criteria, [], user.black_list)
                        user.count_loaded = len(user.viewed_list) if user.viewed_list else 0
                        users.append(user)

                        if user.count_not_viewed() > 0 and user.count_loaded > 0:
                            vk_bot.send_message(event.user_id, f"привет {user.first_name}, продолжим?\n"
                                                               f"осталось {user.count_not_viewed()} пользователей\n"
                                                               f"\n{user.display_criteria()}\n", continue_key)
                        else:
                            clear_current_search_data(user)
                            vk_bot.send_message(event.user_id, f"привет {user.first_name}, искать снова?\n"
                                                               f"нашел {user.count_to_load} пользователей\n"
                                                               f"\n{user.display_criteria()}\n", start_key)
                else:
                    for user in users:
                        if request in ('начать поиск', 'продолжить поиск'):
                            if user.id == event.user_id:
                                count, target_users = vk.search_users(user.criteria, user.viewed_list, user.black_list)
                                if request == 'начать поиск':
                                    user.count_to_load = count
                                    vk_bot.send_message(event.user_id, f"нашел {user.count_to_load} пользователей")
                                else:
                                    vk_bot.send_message(event.user_id, f"осталось {count} пользователей")
                                vk_bot.send_message(event.user_id, "загружаю...")

                                for i, target_user in enumerate(target_users):
                                    photos = vk.get_photos(target_user)
                                    top_3_photos = vk.get_top_photos(photos, 3)
                                    attachments = vk_bot.get_attachments(top_3_photos)
                                    vk_bot.send_message(event.user_id, f"https://vk.com/id{str(target_user)}",
                                                        None, attachments)
                                    user.viewed_list.append(target_user)
                                    if i == user.max_number - 1:
                                        break
                                crud.insert_users_search(user)
                                user.count_loaded = len(user.loaded_list)

                                if user.count_not_viewed() > 0:
                                    vk_bot.send_message(event.user_id,
                                                        f"осталось {user.count_not_viewed()} пользователей"
                                                        f"\nсделай выбор:", continue_key)
                                else:
                                    clear_current_search_data(user, 1)
                                    vk_bot.send_message(event.user_id, "сделай выбор:", start_key)

                        elif request == 'изменить параметры':
                            if user.id == event.user_id:
                                vk_bot.send_message(event.user_id, f"{user.display_criteria()}\n"
                                                                   "сделай выбор:", change_criteria_key)

                        elif request == 'пол':
                            if user.id == event.user_id:
                                user.change_sex()
                                crud.update_sex(user)
                                clear_current_search_data(user, 1)
                                vk_bot.send_message(event.user_id, f"пол изменен\n"
                                                                   f"{user.display_criteria()}", start_key)
                                count, target_users = vk.search_users(user.criteria, user.viewed_list, user.black_list)
                                vk_bot.send_message(event.user_id, f"нашел {count} пользователей")

                        elif request == 'возраст':
                            if user.id == event.user_id:
                                vk_bot.send_message(event.user_id, "введите возраст в формате '30-35'")

                        elif re.match(re.compile(age_pattern), request):
                            if user.id == event.user_id:
                                age_from, age_to = re.match(re.compile(age_pattern), request).groups()
                                user.change_age(age_from, age_to)
                                crud.update_age(user)
                                clear_current_search_data(user, 1)
                                count, target_users = vk.search_users(user.criteria, user.viewed_list, user.black_list)
                                vk_bot.send_message(event.user_id, f"возраст изменен\n{user.display_criteria()}",
                                                    start_key)
                                vk_bot.send_message(event.user_id, f"нашел {count} пользователей")

                        elif request == 'город':
                            if user.id == event.user_id:
                                vk_bot.send_message(event.user_id, "введите город в формате 'г Москва'")

                        elif re.match(re.compile(city_pattern), request):
                            if user.id == event.user_id:
                                city_query = re.match(re.compile(city_pattern), request).groups()[0]
                                city_dict, city_key = vk.get_cities(city_query, user.criteria['country_id'])
                                if len(city_key) > 0:
                                    city_key = vk_bot.get_keyboard({'buttons': city_key})
                                    vk_bot.send_message(event.user_id, "подтвердите выбор:", city_key)
                                else:
                                    vk_bot.send_message(event.user_id, "город не найден", change_criteria_key)

                        elif re.match(re.compile(id_city_pattern), request):
                            if user.id == event.user_id:
                                city_id = re.match(re.compile(id_city_pattern), request).groups()[0]
                                user.change_city(city_id, city_dict[city_id])
                                crud.update_city(user)
                                clear_current_search_data(user, 1)
                                user.count_to_load, target_users = vk.search_users(user.criteria, user.viewed_list,
                                                                                   user.black_list)
                                vk_bot.send_message(event.user_id, f"город изменен\n{user.display_criteria()}",
                                                    start_key)
                                vk_bot.send_message(event.user_id, f"нашел {user.count_to_load} пользователей")

                        elif request == 'статус':
                            if user.id == event.user_id:
                                vk_bot.send_message(event.user_id, user.STATUS_LABEL)

                        elif re.match(re.compile(status_pattern), request):
                            if user.id == event.user_id:
                                status = int(re.match(re.compile(status_pattern), request).groups()[0])
                                user.change_status(status)
                                crud.update_status(user)
                                clear_current_search_data(user, 1)
                                count, target_users = vk.search_users(user.criteria, user.viewed_list, user.black_list)
                                vk_bot.send_message(event.user_id, f"статус изменен\n{user.display_criteria()}",
                                                    start_key)
                                vk_bot.send_message(event.user_id, f"нашел {count} пользователей")

                        elif request == '+':
                            if user.id == event.user_id:
                                reply_message = vk_bot.get_reply_message(event.peer_id, event.user_id)
                                if re.match(re.compile(id_reply_pattern), reply_message):
                                    favorite_user_id = int(re.match(re.compile(id_reply_pattern),
                                                                    reply_message).groups()[0])
                                    if favorite_user_id not in user.favorite_list:
                                        crud.insert_favorite(user, favorite_user_id)
                                        user.favorite_list.append(favorite_user_id)
                                        vk_bot.send_message(event.user_id, f"пользователь добавлен в избранное",
                                                            continue_key)
                                    else:
                                        vk_bot.send_message(event.user_id, 'пользователь уже в списке',
                                                            continue_key)
                                else:
                                    vk_bot.send_message(event.user_id, "чтобы добавить в избранное, отправь '+' "
                                                                       "\nв ответе на сообщение со ссылкой "
                                                                       "на пользователя")

                        elif request == '-':
                            if user.id == event.user_id:
                                reply_message = vk_bot.get_reply_message(event.peer_id, event.user_id)
                                if re.match(re.compile(id_reply_pattern), reply_message):
                                    black_list_user_id = int(re.match(re.compile(id_reply_pattern),
                                                                      reply_message).groups()[0])
                                    if black_list_user_id not in user.black_list:
                                        crud.insert_black_user(user, black_list_user_id)
                                        user.black_list.append(black_list_user_id)
                                        user.clear_black_list_info(black_list_user_id)
                                        user.count_to_load, target_users = vk.search_users(user.criteria, [],
                                                                                           user.black_list)
                                        vk_bot.send_message(event.user_id, f"пользователь добавлен в черный список",
                                                            continue_key)
                                    else:
                                        vk_bot.send_message(event.user_id, 'пользователь уже в списке',
                                                            continue_key)
                                else:
                                    vk_bot.send_message(event.user_id, "чтобы добавить в черный список, отправь '-' "
                                                                       "\nв ответе на сообщение со ссылкой "
                                                                       "на пользователя")

                        elif request == 'черный список':
                            if user.id == event.user_id:
                                if user.black_list:
                                    for black_user in user.black_list:
                                        vk_bot.send_message(event.user_id, f"https://vk.com/id{str(black_user)}")
                                    vk_bot.send_message(event.user_id, 'сделай выбор', continue_key)
                                else:
                                    vk_bot.send_message(event.user_id, 'список пуст', continue_key)

                        elif request == 'избранное':
                            if user.id == event.user_id:
                                if user.favorite_list:
                                    for favorite_user in user.favorite_list:
                                        vk_bot.send_message(event.user_id, f"https://vk.com/id{str(favorite_user)}")
                                    vk_bot.send_message(event.user_id, 'сделай выбор', continue_key)
                                else:
                                    vk_bot.send_message(event.user_id, 'список пуст', continue_key)

                        else:
                            if user.id == event.user_id:
                                vk_bot.send_message(event.user_id, "не понял вашего ответа...")


if __name__ == "__main__":
    main()
