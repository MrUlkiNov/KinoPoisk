import telebot
from config import BOT_TOKEN
from telebot import types
from api import client_window
from datetime import datetime

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
    button_history = types.KeyboardButton("/history")
    markup.add(button_low, button_high, button_custom, button_history)
    bot.send_message(message.chat.id, "Пожалуйста, выберите одну из команд:\n/low "
                                      "- Выбрать старые фильмы с высоким рейтингом\n/high - Выбрать новые фильмы с "
                                      "высоким рейтингом\n/custom - Выбрать фильмы по вашему указанному диапазону "
                                      "дат\n/history - Посмотреть историю последних запросов", reply_markup=markup)


user_state = {}


@bot.message_handler(func=lambda message: message.text.lower() in ['/low', '/high'])
def get_count_and_send_films(message):
    sort_type = 'low' if message.text.lower() == '/low' else 'high'
    bot.send_message(message.chat.id, 'Напишите количество фильмов: ')
    bot.register_next_step_handler(message, lambda msg: process_count_and_send_films(msg, sort_type))


history = {}


@bot.message_handler(func=lambda message: message.text.lower() == '/history')
def show_history(message):
    user_name = message.from_user.first_name
    user_history = history.get(user_name, [])

    if not user_history:
        bot.send_message(message.chat.id, "История запросов пуста.")
        return

    history_text = "История ваших запросов:\n"
    for entry in user_history:
        history_text += f"Дата: {entry['date']}\n" \
                        f"Тип сортировки: {entry['sort_type']}\n" \
                        f"Количество фильмов: {entry['count']}\n"
        history_text += f"Год(ы): {entry['year']}\n\n" if entry['year'] != "0000" else ""

    bot.send_message(message.chat.id, history_text)


@bot.message_handler(func=lambda message: message.text.lower() == '/custom')
def get_custom_year_films(message):
    bot.send_message(message.chat.id, "Напишите год или диапазон годов для поиска фильмов: ")
    bot.register_next_step_handler(message, lambda msg: save_custom_year(msg))


def save_custom_year(message):
    custom_year = message.text.strip()
    bot.send_message(message.chat.id, "Год сохранен. Теперь напишите количество фильмов:")
    bot.register_next_step_handler(message, lambda msg: process_count_and_send_films(msg, 'custom', custom_year))


def process_count_and_send_films(message, sort_type, custom_year="0000"):
    user_name = message.from_user.first_name
    try:
        count = int(message.text.strip())
        films = client_window(sort_type, count, custom_year)
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "date": current_date,
            "sort_type": sort_type,
            "count": count,
            "year": custom_year
        }
        user_history = history.get(user_name, [])
        user_history.append(entry)
        history[user_name] = user_history

        for film in films:
            bot.send_photo(message.chat.id, film[1], caption=film[0])
    except ValueError:
        bot.send_message(message.chat.id, "Некорректное количество. Введите целое число.")


bot.polling(none_stop=True)
