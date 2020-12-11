import telebot
import json
import requests
from telebot import types

token = '1459161586:AAHUgwDTqa-IMm5KJD-Hh3bRm01rJ0TtuPc'
bot = telebot.TeleBot(token)
token_ya = 'dict.1.1.20201210T104723Z.308567fc9aedf8f7.9a02e5033bb6b2e7b497a2624c7aae86a37a5de5'
base_url = 'dictionary.yandex.net/api/v1/dicservice.json/lookup?'


@bot.message_handler(commands=['start','help'])
def start_command(message):
    bot.send_message(message.chat.id, 'Привет, я переводчик. Начнем?')


@bot.message_handler(content_types=['text'])
def ask_translation(message):
    if 'не' in message.text.lower() or 'no' in message.text.lower():
        bot.send_message(message.chat.id, 'Ну что ж, в другой раз!')
        bot.register_next_step_handler(message, start_command)
    else:
        keyboard = types.InlineKeyboardMarkup()
        key_ruen = types.InlineKeyboardButton(text='С русского на английский', callback_data='ru-en')
        keyboard.add(key_ruen)
        key_enru = types.InlineKeyboardButton(text='С английского на русский', callback_data='en-ru')
        keyboard.add(key_enru)
        bot.send_message(message.from_user.id, text='Как будем переводить?', reply_markup=keyboard)
        bot.register_next_step_handler(message, prepare_answer)  # следующий шаг – функция ask_word


@bot.message_handler(content_types=['text'])
def prepare_answer(message):
    URL = 'https://{base_url}key={token_ya}&lang={lang}&text={text}'.format(base_url=base_url, token_ya=token_ya, lang=lang, text=message.text.lower())
    # данные, которые мы взяли по ссылке, преобразуем строку в словарь
    global data
    data = json.loads(requests.get(URL).text)
    # если код ошибки не пуст, выводим сообщение, иначе продолжаем работу со словарем
    if data.get('code') is not None:
        bot.send_message(message.from_user.id, error_code())
    else:
        # вытягиваем элемент с ключом 'def', это список из 1 элемента
        global list
        list = data.get('def')
        # если список пуст, слово не найдено, иначе продолжаем работу со списком
        if len(list) == 0:
            bot.send_message(message.from_user.id, text='Я ничего не нашел для тебя :(')
        else:
            word_extraction()
            bot.send_message(message.from_user.id, answer)


# обработчик кнопок, где call.data это callback_data, которую мы указали при объявлении кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    global lang
    if call.data == 'ru-en':
        lang = 'ru-en'
        bot.send_message(call.message.chat.id, 'Какое слово будем переводить?')
    elif call.data == 'en-ru':
        lang = 'en-ru'
        bot.send_message(call.message.chat.id, 'Какое слово будем переводить?')

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
        error = 'Операция выполнена успешно, но что-то пошло не так'
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



