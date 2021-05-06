from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from random import randrange
import vk_api
from vk_api import VkUpload
import requests


class VkBot:
    BUTTONS_COLORS = {'blue': VkKeyboardColor.PRIMARY,
                      'red': VkKeyboardColor.NEGATIVE,
                      'white': VkKeyboardColor.SECONDARY,
                      'green': VkKeyboardColor.POSITIVE
                      }

    def __init__(self, vk_group_token):
        """Конструктор класса VkBot.
        Принимает токен аккаунта группы Vk.
        """
        self.session = vk_api.VkApi(token=vk_group_token)

    def get_keyboard(self, menu):
        """Возврашает объект класса VkKeyboard по заданным параметрам в menu."""
        keyboard = VkKeyboard(one_time=True, inline=False)
        for i, buttons_list in enumerate(menu['buttons']):
            if i != 0:
                keyboard.add_line()
            for k, button in enumerate(buttons_list):
                color = menu['colors'][i][k] if 'colors' in menu.keys() else 'blue'
                keyboard.add_button(button[0:40], self.BUTTONS_COLORS[color])
        return keyboard

    def send_message(self, user_id, message, keyboard=None, attachments=None):
        """Отправляет сообшение в чат пользователю с user_id методом messages.send vk api
        с заданными параметрами message, keyboard, attachments.
        """
        params = {'user_id': user_id,
                  'message': message,
                  'random_id': randrange(10 ** 7)
                  }
        if attachments is not None:
            params['attachment'] = ','.join(attachments)

        if keyboard is not None:
            params['keyboard'] = keyboard.get_keyboard()

        self.session.method('messages.send', params)

    def get_attachments(self, photos):
        """Создает и возврашает объект класса VkUpload с фотографиями photos."""
        attachments = []
        upload = VkUpload(self.session)
        for item in photos:
            image = requests.get(item['url'], stream=True)
            photo = upload.photo_messages(photos=image.raw)[0]
            attachments.append('photo{}_{}'.format(photo['owner_id'], photo['id']))
        return attachments

    def get_reply_message(self, peer_id, user_id):
        """Возврашает текст исходного сообщения по параметрам peer_id, user_id
        с помощью vk api метода messages.getHistory.
        """
        conversation = self.session.method('messages.getHistory', {'peer_id': peer_id, 'user_id': user_id,
                                                                   'count': 1, })['items'][0]
        reply_message = ''
        if 'reply_message' in conversation.keys():
            reply_message = conversation['reply_message']['text']
        return reply_message
