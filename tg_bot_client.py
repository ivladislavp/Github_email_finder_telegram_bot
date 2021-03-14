import requests, telebot, time

tkn = 'your_bot_token_here'
bot = telebot.TeleBot(tkn)


# Функция осуществляет запрос к апи гитхаб, на выходе отображает список публичных действий юзера
# Нас интересуют только коммиты, в них есть email автора коммита. Выгружаем коммиты, удаляем повторяющиеся

def email_finder(nick):
    rawlist, newlist = [], []

    # Делаем запрос на гитхаб, в запрос подставляем ник из входящего сообщения

    url = f'https://api.github.com/users/{nick}/events/public'
    r = requests.get(url)
    url_status = r.status_code

    # Проверка существования адреса
    # Если пользователь найден - идем дальше по циклу, иначе выходим

    if url_status == 200:
        print('status 200 - OK')

        # Если пользователь найден, но возвращается пустой массив, то у юзера нет коммитов
        # Выходим из цикла с сообщением "Невозможно найти почту"

        if not r.json():
            return 'Пользователь найден. Невозможно найти email.'

    elif url_status == 404:
        return 'Юзер с таким ником не найден'
    else:
        print('Неизвестная ошибка')
        return 'Неизвестная ошибка'

    # Поиск и выгрузка коммитов

    for element in r.json():
        if element['type'] == 'PushEvent':
            for commit in element['payload']['commits']:
                # Наполняем список всеми почтами из коммитов пользователя
                email = commit['author']['email']
                rawlist.append(email)
    f_list = 'Найдены электронные ящики: \n'

    # Удаляем повторы из списка и форматируем новый список

    for i in rawlist:
        if i not in newlist:
            newlist.append(i)
    for element in newlist:
        f_list = f_list + element + '\n'

    return f_list

    # Телеграм бот


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет, я помогу тебе найти email пользователя гитхаб'
                                      'по его нику. Отправь мне ник пользователя и, если он существует, '
                                      'я найду его почту')


# Любое сообщение боту - это запрос на поиск по нику на гитхаб
# В качестве ответа отправляется результат выполнения функции email_finder

@bot.message_handler(content_types=['text'])
def send_text(message):

    bot.send_message(message.chat.id, email_finder(message.text))

# Чтобы бот не падал

while True:
    try:
        print('Слушаю сообщения...')
        bot.infinity_polling(True)

    except Exception as e:
        print('Я упал')
        time.sleep(15)
