import telebot
from telebot import types

# Создайте файл config.py и поместите туда TOKEN
# Далее все будет корректно работать
import inc.config as cnf

from inc.parsing.main_script import get_card
import inc.parsing.case_video as cnf_vid

from inc.transfer.main_script_transfer import CryptoConverter, UserDB
import inc.transfer.config_for_transfer as cnf_val
from exception.exception import CASEError, SortingError, ConvertionExceprion

# ''' Присваеваем боту токен '''
bot = telebot.TeleBot(cnf.TOKEN)

DB = UserDB()

@bot.message_handler(commands=['start', 'help'])
def start_or_help(message: telebot.types.Message):

    ''' Обработка команд /start и /help '''

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    bat1 = types.KeyboardButton('/videocard')
    bat1 = types.KeyboardButton('/set')
    markup.add(bat1)
    text = 'Добрый день \n Что вас интересует? \n\n ' \
           'Поиск видеокарты - "/videocard \n\n"' \
           'Валюта - /set \n'


    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(commands=['set'])
def set(message: telebot.types.Message):

    ''' Выодит кнопки для команды: "/videocard" '''

    markup = telebot.types.InlineKeyboardMarkup()
    for val, form in cnf_val.KEYS.items():
        button = telebot.types.InlineKeyboardButton(text=val, callback_data=f'val1 {form}')
        markup.add(button)

    bot.send_message(chat_id=message.chat.id,
                     text='Выберите валюту, из которой будем конвертировать',
                     reply_markup=markup)

    markup = telebot.types.InlineKeyboardMarkup()
    for val, form in cnf_val.KEYS.items():
        button = telebot.types.InlineKeyboardButton(text=val, callback_data=f'val2 {form}')
        markup.add(button)

    bot.send_message(chat_id=message.chat.id,
                     text='Выберите валюту, в которую будем конвертировать',
                     reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def get_value(call):

    ''' Функция команды: /set '''
    ''' Реакция на изменения валюты '''

    t, st = call.data.split()
    user_id = call.message.chat.id
    if t == 'val1':
        DB.change_from(user_id, st)
    if t == 'val2':
        DB.change_too(user_id, st)

    pair = DB.get_pair(user_id)
    bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=f'Теперь конвертируем из {pair[0]} в {pair[1]}')

@bot.message_handler(content_types=['text', ])
def get_values(message: telebot.types.Message):

    ''' Функция команды: /set '''
    ''' Вывод цены валюты '''

    pair = DB.get_pair(message.chat.id)
    values = [*pair, message.text.strip()]
    try:

        total = CryptoConverter.convert(values)

    except ConvertionExceprion as c:
        bot.send_message(message.chat.id, f'Ошибка пользователя. \n{c}')
    except Exception as e:
        bot.send_message(message.chat.id, f'Не удалось обработать команду\n{e}')
    else:
        text = f'{values[2]} {values[0]} -- {round(total, 2)} {values[1]}'
        bot.send_message(message.chat.id, text)

@bot.message_handler(content_types=['text', ])
def get_menu(message: telebot.types.Message):

    ''' Выодит кнопки для команды: "/videocard" '''

    if message.text == '/videocard':

        ''' Функция для поиска видеокарт '''

        keyboard = types.InlineKeyboardMarkup()
        try:
            # Данный блок выводит кнопки с чипсетами видеокарт для выбора пользователям
            for k, i in cnf_vid.CASE_NVIDIA.items():
                key = types.InlineKeyboardButton(text=k, callback_data=i)
                keyboard.add(key)
        except Exception:
            raise CASEError('Ошибка в CASE_NVIDIA')
        bot.send_message(message.chat.id, text='Что вам нужно?', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def get_menu_2(call):

    ''' Функция ответа на комадну /videocard '''

    mess = call.data[3:]
    carts = get_card(mess)
    bot.send_message(call.message.chat.id, text='Вот что я нашел по вашему запросу:')
    try:
        for cart in carts:
            for name, value in cart.items():
                if name == 'Название:':
                    TEXT_TITLE = f'{name} {value}'
                elif name == 'Ссылка:':
                    # keyboard = types.InlineKeyboardMarkup()
                    # url_button = types.InlineKeyboardButton(text=name, url=value)
                    # keyboard.add(url_button)
                    # bot.send_message(call.message.chat.id, text=name, reply_markup=keyboard)
                    LINK = f'{name} {value}'

                elif name == 'Цена:':
                    PRICE = f'{name} {value}'
                    bot.send_message(call.message.chat.id, text=f'{TEXT_TITLE} \n {PRICE} \n {LINK}')
    except Exception:
        raise SortingError('Что то пошло не так, ошибка в сортироке...')

# ''' Запускаем бота в работу '''
bot.polling(none_stop=True, interval=0)
