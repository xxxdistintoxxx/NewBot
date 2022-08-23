from random import randrange
import os
from dotenv import load_dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from tableSearch import find_user, insert_user, change_user, user_info, find_user2, change_status2
from addFoundUser import add_user, user_in_db
from userData import check_user_data
from create_database import create_db

class Vk:
    def __init__(self):
        create_db()
        load_dotenv('tokens.env')
        self.interface_token = os.getenv('VK_COMMUNITY_TOKEN_FULL')
        self.search_token = os.getenv('USER_TOKEN')
        self.interface_vk = vk_api.VkApi(token=self.interface_token)
        self.search_vk = vk_api.VkApi(token=self.search_token)
        self.longpoll = VkLongPoll(self.interface_vk)
        self.vk_session = self.search_vk.get_api()
        self.age = False
        self.sex = False
        self.town = False
        self.stat = False



    def write_text_message(self, user_id, message):
        self.interface_vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})


    def send_photo_message(self, user_id, name, surname, users_id, photos):
        text = f'Человек найден ✅\nИмя: {name}\nФамилия: {surname}\nСсылка на профиль: vk.com/id{users_id}'

        self.interface_vk.method("messages.send", {"user_id": user_id, "message": text, "attachment": photos, 'random_id': randrange(10 ** 7)})


    def normalize_request(self, string):
        string = string.lower()
        string = string.strip()
        return string


    def search(self, user_id):
        _, status, status2, age, sex, town, stat = user_info(user_id)
        sex = 3 - int(sex)
        stat = int(stat)
        age = int(age)
        result = self.vk_session.users.search(sort=0, count=1000, fields='deactivated, is_closed, counters, sex', hometown=town, sex=sex, status=stat, age_from=age - 3, age_to=age + 3, has_photo=1, )
        for i in result['items']:
            if not i['is_closed']:
                nums = self.vk_session.users.get(user_ids=i['id'], fields='counters')[0]['counters']
                id = self.vk_session.users.get(user_ids=i['id'], fields='counters')[0]['id']
                photo_amount = nums['photos']
                if photo_amount >= 3 and not user_in_db(id):
                    photos = self.vk_session.photos.getProfile(owner_id=id)['items']
                    list_of_photos = []
                    result2 = []
                    name = i['first_name']
                    surname = i['last_name']
                    for i in photos:
                        list_of_photos.append(i['id'])
                    for i in list_of_photos:
                        information = self.vk_session.photos.getById(photos=f'{id}_{i}', extended=1)
                        amout_of_likes = information[0]['likes']
                        link = information[0]['orig_photo']['url']
                        result2.append({'photo_id': i, 'user_id': id, 'likes': amout_of_likes['count'], 'link': link})
                    result2.sort(key=lambda i: i['likes'], reverse=True)
                    result2 = result2[0:3]
                    link_list = [i['link'] for i in result2]
                    print(result)
                    if len(result2) < 3:
                        continue
                    photo_string = f'photo{result2[0]["user_id"]}_{result2[0]["photo_id"]},photo{result2[1]["user_id"]}_{result2[1]["photo_id"]},photo{result2[2]["user_id"]}_{result2[2]["photo_id"]}'
                    return name, surname, photo_string, id, link_list
        return None, None, None, None, None

    def start(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    request = event.text
                    user_id = event.user_id
                    result = find_user(user_id)
                    user_data = check_user_data(user_id)
                    if not result:
                        print('new user')
                        self.write_text_message(event.user_id, f'Привет 👋\nЯ бот, который находит похожих людей')
                        insert_user(user_id)

                        self.write_text_message(event.user_id, f'Загрузка данных из профиля для поиска...')
                        if not user_data or '' in list(user_data.values()):
                            if user_data['age'] != '':
                                change_user(user_id, 1, 'age', user_data['age'])
                            if user_data['sex'] != '':
                                change_user(user_id, 1, 'sex', user_data['sex'])
                            if user_data['city'] != '':
                                change_user(user_id, 1, 'town', user_data['city'])
                            if user_data['stat'] != '':
                                change_user(user_id, 1, 'stat', user_data['stat'])
                            self.write_text_message(event.user_id,
                                                    f'Так как у тебя в профиле находятся не все данные,\n необходимые для поиска, или профиль закрытый,\n то тебе надо пройти небольшой опрос, для того, чтобы я смог осуществить корректный поиск')
                            self.write_text_message(event.user_id, 'Для продолжения введите любой символ')

                        else:

                            change_user(user_id, 2, 'age', user_data['age'])
                            change_user(user_id, 2, 'sex', user_data['sex'])
                            change_user(user_id, 2, 'town', user_data['city'])
                            change_user(user_id, 2, 'stat', user_data['stat'])
                            self.write_text_message(event.user_id, f'Все данные успешно загружены из профиля ✔')
                            self.write_text_message(event.user_id, f'Запускаю поиск...')
                            name, surname, photos, users_id, links_list = self.search(user_id)
                            self.write_text_message(event.user_id, f'Результаты:')
                            if name is None:
                                self.write_text_message(event.user_id,
                                                        'К сожалению пользователи не найдены 😕\nДля следующего поиска введите любой символ')
                            else:
                                self.send_photo_message(event.user_id, name, surname, users_id, photos)
                                add_user(self.age, self.sex, self.town, self.stat, name, surname, links_list[0],
                                         links_list[1], links_list[2], users_id)

                                self.write_text_message(event.user_id, 'Для следующего поиска введите любой символ')

                    elif result == 2:
                        print('old user with all data')
                        self.write_text_message(event.user_id, f'Все данные успешно загружены ✔')
                        self.write_text_message(event.user_id, f'Запускаю поиск...')
                        name, surname, photos, users_id, links_list = self.search(user_id)
                        self.write_text_message(event.user_id, f'Итак, результаты:')
                        if name is None:
                            self.write_text_message(event.user_id,
                                                    'К сожалению пользователи не найдены 😕\nДля следующего поиска введите любой символ')
                        else:
                            self.send_photo_message(event.user_id, name, surname, users_id, photos)
                            add_user(self.age, self.sex, self.town, self.stat, name, surname, links_list[0],
                                     links_list[1], links_list[2], users_id)

                            self.write_text_message(event.user_id, 'Для следующего поиска введите любой символ')

                    elif result == 1:
                        print('not enough data')
                        resultx = find_user2(user_id)
                        print(resultx)
                        if resultx == 1:
                            if not user_data or user_data['age'] == '':
                                self.write_text_message(event.user_id, f'Сколько тебе лет?')
                                change_status2(user_id, 2)
                            elif not user_data or user_data['sex'] == '':
                                change_status2(user_id, 3)
                                self.write_text_message(event.user_id, f'Какого ты пола?\n(1 - женского\n2 - мужского)')
                            elif not user_data or user_data['city'] == '':
                                change_status2(user_id, 4)
                                self.write_text_message(event.user_id, f'В каком городе ты живешь?')
                            elif not user_data or user_data['stat'] == '':
                                change_status2(user_id, 5)
                                self.write_text_message(event.user_id,
                                                        f'Какое у тебя семейное положение?\n(1 - не в браке\n2 - встречаешься\n3 - помолвлен\n4 - в браке\n5 - всё сложно\n6 - в активном поиске\n7 - влюблен\n8 - в гражданском браке)')
                            else:
                                change_status2(user_id, 6)

                        elif resultx == 2:
                            try:
                                age = int(request)
                                change_user(user_id, 1, 'age', age)
                                self.age = age
                                if not user_data or user_data['sex'] == '':
                                    change_status2(user_id, 3)
                                    self.write_text_message(event.user_id, f'Какого ты пола?\n(1 - женского\n2 - мужского)')
                                elif not user_data or user_data['city'] == '':
                                    change_status2(user_id, 4)
                                    self.write_text_message(event.user_id, f'В каком городе ты живешь?')
                                elif not user_data or user_data['stat'] == '':
                                    change_status2(user_id, 5)
                                    self.write_text_message(event.user_id, f'Какое у тебя семейное положение?\n(1 - не в браке\n2 - встречаешься\n3 - помолвлен\n4 - в браке\n5 - всё сложно\n6 - в активном поиске\n7 - влюблен\n8 - в гражданском браке)')
                                else:
                                    change_status2(user_id, 6)
                            except ValueError:
                                print('this 1')

                        elif resultx == 3:
                            if request == '1' or request == '2':
                                sex = int(request)
                                change_user(user_id, 1, 'sex', sex)
                                self.sex = sex
                                if not user_data or user_data['city'] == '':
                                    change_status2(user_id, 4)
                                    self.write_text_message(event.user_id, f'В каком городе ты живешь?')
                                elif not user_data or user_data['stat'] == '':
                                    change_status2(user_id, 5)
                                    self.write_text_message(event.user_id, f'Какое у тебя семейное положение?\n(1 - не в браке\n2 - встречаешься\n3 - помолвлен\n4 - в браке\n5 - всё сложно\n6 - в активном поиске\n7 - влюблен\n8 - в гражданском браке)')
                                else:
                                    change_status2(user_id, 6)

                            else:
                                self.write_text_message(event.user_id, f'Введи 1 или 2')

                        elif resultx == 4:
                            town = request
                            change_user(user_id, 1, 'town', town)
                            self.town = town
                            if not user_data or user_data['stat'] == '':
                                change_status2(user_id, 5)
                                self.write_text_message(event.user_id, f'Какое у тебя семейное положение?\n(1 - не в браке\n2 - встречаешься\n3 - помолвлен\n4 - в браке\n5 - всё сложно\n6 - в активном поиске\n7 - влюблен\n8 - в гражданском браке)')
                            else:
                                change_status2(user_id, 6)

                        elif resultx == 5:
                            try:
                                request = int(request)
                                if request >= 1 and request <= 8:
                                    stat = request
                                    change_user(user_id, 1, 'stat', stat)
                                    self.stat = stat
                                    self.write_text_message(event.user_id, f'Все данные загружены, запускаю поиск')
                                    self.write_text_message(event.user_id, f'Итак, результаты:')
                                    name, surname, photos, users_id, links_list = self.search(user_id)
                                    change_user(user_id, 2, '', '')
                                    if name is None:
                                        self.write_text_message(event.user_id, 'К сожалению пользователи не найдены 😕\nДля следующего поиска введите любой символ')
                                    else:
                                        self.send_photo_message(event.user_id, name, surname, users_id, photos)
                                        add_user(self.age, self.sex, self.town, self.stat, name, surname, links_list[0], links_list[1], links_list[2], users_id)

                                        self.write_text_message(event.user_id,'Для следующего поиска введите любой символ')
                                else:
                                    self.write_text_message(event.user_id, f'Введи цифру от 1 до 8')
                            except ValueError:
                                print('this 2')
                        resultx = find_user2(user_id)
                        if resultx == 6:
                            self.write_text_message(event.user_id, f'Все данные загружены, запускаю поиск')
                            name, surname, photos, users_id, links_list = self.search(user_id)
                            change_user(user_id, 2, '', '')
                            if name is None:
                                self.write_text_message(event.user_id,
                                                        'К сожалению пользователи не найдены 😕\nДля следующего поиска введите любой символ')
                            else:
                                self.send_photo_message(event.user_id, name, surname, users_id, photos)
                                add_user(self.age, self.sex, self.town, self.stat, name, surname, links_list[0],
                                         links_list[1], links_list[2], users_id)

                                self.write_text_message(event.user_id, 'Для следующего поиска введите любой символ')



