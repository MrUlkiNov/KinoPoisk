import telebot
from config import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'hello'])
def start_window(message):
    bot.send_message(message.chat.id, "Привет {}! Я виртуальный ассистент. Я отвечу на ваши вопросы о компании, "
                                      "нашей продукции, помогу сделать заказ. Какой у вас вопрос?".format(message.from_user.first_name))

@bot.message_handler()
def info(message):
    if message.text.lower() == "привет":
        bot.send_message(message.chat.id, "Привет {}! Я виртуальный ассистент. Я отвечу на ваши вопросы о компании, "
                                          "нашей продукции, помогу сделать заказ. Какой у вас вопрос?".format(
            message.from_user.first_name))

bot.infinity_polling()