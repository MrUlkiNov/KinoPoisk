import telebot
from config import BOT_TOKEN
from bot_functions import bot_handlers, bot_run

bot = telebot.TeleBot(BOT_TOKEN)

if __name__ == "__main__":
    bot_handlers(bot)
    bot_run(bot)


