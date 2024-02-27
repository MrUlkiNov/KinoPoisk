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
    markup.add(button_low)
    bot.send_message(message.chat.id, "Пожалуйста, выберите одну из команд:\n/low "
                                      "- Выбрать старые фильмы с высоким рейтингом", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text.lower() == '/low')
def low(message):
    bot.send_message(message.chat.id, 'Напишите количество фильмов: ')
    bot.register_next_step_handler(message, get_count_and_send_low_films)


@bot.message_handler(func=lambda message: message.text.lower() == 'low')
def get_count_and_send_low_films(message):
    try:
        count = int(message.text.strip())
        films = client_window('low', count)
        for film in films:
            bot.send_photo(message.chat.id, film[1], caption=film[0])
    except ValueError:
        bot.send_message(message.chat.id, "Некорректное количество. Введите целое число.")


bot.polling(none_stop=True)
