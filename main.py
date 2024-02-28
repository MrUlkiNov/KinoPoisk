import telebot
from config import BOT_TOKEN
from telebot import types
from api import client_window

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start', 'hello'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет {}! Я виртуальный ассистент. Я отвечу на ваши вопросы о компании, "
                                      "нашей продукции, помогу сделать заказ. Какой у вас вопрос?".format(
        message.from_user.first_name))
    show_sort_buttons(message)


@bot.message_handler(func=lambda message: message.text.lower() == 'привет')
def hello(message):
    bot.send_message(message.chat.id, "Привет {}! Я виртуальный ассистент. Я отвечу на ваши вопросы о компании, "
                                      "нашей продукции, помогу сделать заказ. Какой у вас вопрос?".format(
        message.from_user.first_name))
    show_sort_buttons(message)


def show_sort_buttons(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_low = types.KeyboardButton("/low")
    button_high = types.KeyboardButton('/high')
    button_custom = types.KeyboardButton("/custom")
    markup.add(button_low, button_high, button_custom)
    bot.send_message(message.chat.id, "Пожалуйста, выберите одну из команд:\n/low "
                                      "- Выбрать старые фильмы с высоким рейтингом\n/high - Выбрать новые фильмы с "
                                      "популярным рейтингом\n/custom - Выбрать фильмы по вашему указанному диапазону дат", reply_markup=markup)


user_state = {}

@bot.message_handler(func=lambda message: message.text.lower() in ['/low', '/high'])
def get_count_and_send_films(message):
    sort_type = 'low' if message.text.lower() == '/low' else 'high'

    bot.send_message(message.chat.id, 'Напишите количество фильмов: ')
    bot.register_next_step_handler(message, lambda msg: process_count_and_send_films(msg, sort_type))


@bot.message_handler(func=lambda message: message.text.lower() == "/custom")
def get_custom_year_films(message):
    bot.send_message(message.chat.id, "Напишите год или диапазон годов для поиска фильмов: ")
    bot.register_next_step_handler(message, save_custom_year)


def save_custom_year(message):
    user_state[message.chat.id] = message.text
    bot.send_message(message.chat.id, "Год сохранен. Теперь напишите количество фильмов:")
    bot.register_next_step_handler(message, lambda msg: process_count_and_send_films(msg, 'custom'))


def process_count_and_send_films(message, sort_type):
    try:
        count = int(message.text.strip())
        custom_year = user_state.get(message.chat.id, "0000")
        films = client_window(sort_type, count, custom_year)
        for film in films:
            bot.send_photo(message.chat.id, film[1], caption=film[0])
    except ValueError:
        bot.send_message(message.chat.id, "Некорректное количество. Введите целое число.")
    except IndexError:
        bot.send_message(message.chat.id, 'Вы ввели неправильный год')


bot.polling(none_stop=True)
