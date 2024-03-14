import telebot
from decouple import config

TOKEN = config('telegram_bot_token')
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот. Как дела?")


def start_bot():
    bot.polling(none_stop=True)


if __name__ == "__main__":
    start_bot()
