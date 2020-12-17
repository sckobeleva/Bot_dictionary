import telebot
import json
import requests
from telebot import types

token = '1459161586:AAHUgwDTqa-IMm5KJD-Hh3bRm01rJ0TtuPc'
bot = telebot.TeleBot(token)
token_ya = 'dict.1.1.20201210T104723Z.308567fc9aedf8f7.9a02e5033bb6b2e7b497a2624c7aae86a37a5de5'
base_url = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup?'
# здесь обнуляем language, чтобы при перезапуске бота он просил заново выбрать язык, а не валился с ошибками
language = {}

@bot.message_handler(commands=['start'])
def start_command(message):
    # здесь обнуляем language, чтобы далее проверить, что пользователь выбрал язык на клавиатуре, а не просто начал ввод
    global language
    language = {}
    hello_and_help = 'Привет, я переводчик!\n\nЯ умею переводить с русского на иностранный и наоборот.\n\n' \
                     'У меня есть несколько словарей. Выбери один из них, и я буду использовать его по умолчанию.\n\n' \
                     'Сменить словарь можно:\n' \
                     '- командами /change, /start, /help;\n' \
                     '- промотав переписку до приветственного сообщения;\n' \
                     '- очистив историю в этом чате.'
    keyboard = show_keyboard()
    bot.send_message(message.chat.id, text=hello_and_help, reply_markup=keyboard)


@bot.message_handler(commands=['help'])
def help_command(message):
    help = 'Привет, я переводчик! В своей работе я использую API сервиса Яндекс.Словарь. ' \
           'Если в результате поиска ты видишь ошибку или неточность перевода, то виноват, скорее всего, не я :) \n\n' \
            'Я умею переводить с русского на иностранный и наоборот. Это значит, что ты можешь писать свой запрос ' \
            'как на русском, так и на выбранном иностранном языке. \n\n' \
            'У меня есть несколько словарей. Выбери один из них, и я буду использовать его по умолчанию до следующей смены языка.\n\n' \
            'Сменить словарь можно:\n' \
                '- командами /change, /start, /help;\n' \
                '- промотав переписку до приветственного сообщения;\n' \
                '- очистив историю в этом чате.\n\n' \
           'Иногда я могу попросить тебя выбрать язык заново. Значит, в этом появилась техническая необходимость. ' \
           'Спасибо за понимание!'
    keyboard = show_keyboard()
    bot.send_message(message.chat.id, text=help, reply_markup=keyboard)

@bot.message_handler(commands=['change'])
def change_command(message):
    # здесь обнуляем language, чтобы далее проверить, что пользователь выбрал язык на клавиатуре, а не просто начал ввод
    global language
    language = {}
    keyboard = show_keyboard()
    bot.send_message(message.chat.id, text='Выбери словарь:', reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def prepare_answer(message):
    # если language пуст, значит, пользователь не выбрал язык, просим его об этом
    if len(language) == 0:
        keyboard = show_keyboard()
        bot.send_message(message.chat.id, text='Сначала выбери словарь:', reply_markup=keyboard)
    # иначе продолжаем работу
    else:
        global lang
        # если слово на кириллице, присваиваем соответствующее значение из словаря language
        if check_cyrillic(message.text) is True:
            lang = language['native']
        # иначе - тоже
        else:
            lang = language['foreign']
        # формируем ссылку для получения данных
        URL = '{base_url}key={token_ya}&lang={lang}&text={text}'.format(base_url=base_url, token_ya=token_ya, lang=lang, text=message.text.lower())
        # данные, которые мы взяли по ссылке, преобразуем в словарь
        global data
        data = json.loads(requests.get(URL).text)
        # если код ошибки не пуст, выводим сообщение об ошибке, иначе продолжаем работу с данными
        if data.get('code') is not None:
            bot.send_message(message.from_user.id, error_code())
        else:
            # вытягиваем элемент с ключом 'def', это список из 1 элемента
            global list
            list = data.get('def')
            # если список пуст, то слово не найдено, иначе продолжаем работу со списком
            if len(list) == 0:
                bot.send_message(message.from_user.id, text='Я ничего не нашел для тебя :(')
            else:
                word_extraction()
                bot.send_message(message.from_user.id, answer)


# создаем и выводим клавиатуру
def show_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    key_en = types.InlineKeyboardButton(text='English', callback_data='English')
    keyboard.add(key_en)
    key_fr = types.InlineKeyboardButton(text='Français', callback_data='Français')
    #keyboard.add(key_fr)
    key_de = types.InlineKeyboardButton(text='Deutsch', callback_data='Deutsch')
    keyboard.row(key_fr, key_de)
    key_it = types.InlineKeyboardButton(text='Italiano', callback_data='Italiano')
    #keyboard.add(key_it)
    key_es = types.InlineKeyboardButton(text='Español', callback_data='Español')
    keyboard.row(key_it, key_es)
    key_tr = types.InlineKeyboardButton(text='Türkçe', callback_data='Türkçe')
    #keyboard.add(key_tr)
    key_pl = types.InlineKeyboardButton(text='Polski', callback_data='Polski')
    keyboard.row(key_tr, key_pl)
    return keyboard


# обработчик кнопок, где call.data это callback_data, которую мы указали при объявлении кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global language
    if call.data == 'English':
        language = {'native': 'ru-en', 'foreign': 'en-ru'}
    elif call.data == 'Français':
        language = {'native': 'ru-fr', 'foreign': 'fr-ru'}
    elif call.data == 'Deutsch':
        language = {'native': 'ru-de', 'foreign': 'de-ru'}
    elif call.data == 'Italiano':
        language = {'native': 'ru-it', 'foreign': 'it-ru'}
    elif call.data == 'Español':
        language = {'native': 'ru-es', 'foreign': 'es-ru'}
    elif call.data == 'Türkçe':
        language = {'native': 'ru-tr', 'foreign': 'tr-ru'}
    elif call.data == 'Polski':
        language = {'native': 'ru-pl', 'foreign': 'pl-ru'}
    bot.send_message(call.message.chat.id, 'Какое слово будем переводить?')


# определяем, отправленное слово на кириллице или нет
def check_cyrillic(word):
    if u'\u0400' <= word <=u'\u04FF':
        return True
    else:
        return False


# извлекаем слова и формируем в красивый вид
def word_extraction():
    # вытягиваем единственный элемент, это словарь с ключами 'text', 'pos', 'gen', 'anm', 'tr'
    dictionary = list[0]
    # вытягиваем элемент с ключом 'tr', это список из словарей
    translation = dictionary.get('tr')
    global answer
    answer = ''
    n = 1
    # перебираем список словарей, извлекаем из каждого значение ключа 'text'
    for i in translation:
        answer += str(n) + '. ' + str.capitalize(i.get('text'))
        n += 1
        # если есть элемент с ключом 'syn', то извлекаем синонимы, это список словарей
        if i.get('syn') is not None:
            synonyms = i.get('syn')
            # перебираем список словарей, извлекаем из каждого значение ключа 'text'
            answer += ', ' + str(', '.join([j.get('text') for j in synonyms])) + '\n'
        if i.get('mean') is not None:
            meanings = i.get('mean')
            # перебираем список словарей, извлекаем из каждого значение ключа 'text'
            answer += ' (' + str(', '.join([j.get('text') for j in meanings])) + ')\n'
        else:
            answer = answer + '\n'


# выводим сообщение об ошибке в соответствии с кодом
def error_code():
    if data.get('code') == 200:
        error = 'Операция выполнена успешно, но что-то пошло не так...'
    elif data.get('code') == 401:
        error = 'Ключ API невалиден'
    elif data.get('code') == 402:
        error = 'Ключ API заблокирован'
    elif data.get('code') == 403:
        error = 'Превышено суточное ограничение на количество запросов'
    elif data.get('code') == 413:
        error = 'Превышен максимальный размер текста'
    elif data.get('code') == 501:
        error = 'Заданное направление перевода не поддерживается'
    return error


if __name__ == '__main__':
    bot.infinity_polling()



