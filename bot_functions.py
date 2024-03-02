from telebot import types
from api import client_window
from datetime import datetime
from typing import Any
from telebot.types import Message

history = {}


def bot_handlers(bot: Any) -> None:
    """
    Функция, в которой содержатся все функции по работе с ботом
    """

    @bot.message_handler(commands=['start', 'hello'])
    def handle_start(message: Message) -> None:
        """
        Функция отвечает пользователю на команды /start и /hello приветствием, а так же выводит в консоль бота кнопки
        команд вызовом функции show_sort_buttons
        """
        bot.send_message(message.chat.id, "Привет {}! Я виртуальный ассистент по  KinoPoisk. Я помогу вам выбрать "
                                          "популярные фильмы различных годов. ".format(
            message.from_user.first_name))
        show_sort_buttons(message)

    @bot.message_handler(func=lambda message: message.text.lower() == 'привет')
    def hello(message: Message) -> None:
        """
        Функция отвечает пользователю на текст 'привет' приветствием и так же выводит в консоль бота кнопки команд
        вызовом функции show_sort_buttons
        """
        bot.send_message(message.chat.id, "Привет {}! Я виртуальный ассистент по  KinoPoisk. Я помогу вам выбрать "
                                          "популярные фильмы различных годов. ".format(
            message.from_user.first_name))
        show_sort_buttons(message)

    def show_sort_buttons(message: Message):
        """
        Функция в которой создаются кнопки команд по работе с ботом, а так же выводится описание различных команд
        """
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

    @bot.message_handler(func=lambda message: message.text.lower() in ['/low', '/high'])
    def get_count_and_send_films(message: Message) -> None:
        """
        Функция принимает команду /low или /high от пользователя и сохраняет в переменную sort_type, после чего идет
        вызов основной функции process_count_and_send_films с аргументом sort_type. Так же дает пользователю ввести
        количество фильмов
        """
        sort_type = 'low' if message.text.lower() == '/low' else 'high'
        bot.send_message(message.chat.id, 'Напишите количество фильмов: ')
        bot.register_next_step_handler(message, lambda msg: process_count_and_send_films(msg, sort_type))

    @bot.message_handler(func=lambda message: message.text.lower() == '/history')
    def show_history(message: Message) -> None:
        """
        Функция принимает команду /history от пользователя и сохраняет в переменную history_text текст истории команд
        пользователя, для дальнейшего вывода истории в основной функции process_count_and_send_films
        """
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
    def get_custom_year_films(message: Message) -> None:
        """
        Функция принимает от пользователя команду /custom, предлагает ввести год поиска и вызывает функцию
        save_custom_year, передавая в неё введенный год
        """
        bot.send_message(message.chat.id, "Напишите год или диапазон годов для поиска фильмов: ")
        bot.register_next_step_handler(message, lambda msg: save_custom_year(msg))

    def save_custom_year(message: Message) -> None:
        """
        Функция сохраняет с прошлой функции год в переменную, предлагает выбрать количество фильмов и вызывает
        функцию process_count_and_send_films, передавая в неё переменную custom_year в качестве аргумента
        """
        custom_year = message.text.strip()
        bot.send_message(message.chat.id, "Год сохранен. Теперь напишите количество фильмов:")
        bot.register_next_step_handler(message, lambda msg: process_count_and_send_films(msg, 'custom', custom_year))

    def process_count_and_send_films(message: Message, sort_type: str, custom_year: str = "0000") -> None:
        """
        Функция принимает с функций тип сортировки и год пользователя, если тип сортировки custom, в ином случае
        аргумент не требуется. Затем обращается к client_window в функционале API через импорт и работет со списком
        фильмов по заданным критериям пользователя с API сервиса
        """
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


def bot_run(bot: Any) -> None:
    """
    Функция служит, чтоб бот работал постоянно, пока работает отладка
    """
    bot.polling(none_stop=True)
