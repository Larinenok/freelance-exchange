import telebot
from telebot import types
from decouple import config

TOKEN = config('telegram_bot_token')
bot = telebot.TeleBot(TOKEN)


def make_main_keyboard():
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Сайт", callback_data='go_to_site')
    btn2 = types.InlineKeyboardButton("Список заказов", callback_data='view_orders')
    btn3 = types.InlineKeyboardButton("Профиль", callback_data='profile')
    markup.add(btn1, btn2, btn3)
    return markup


@bot.message_handler(commands=['start'])
def start(message):
    markup = make_main_keyboard()
    bot.send_message(message.chat.id, "Привет, {0.last_name}! Я бот УмСтуд.".format(message.from_user), reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'go_to_site':
        bot.send_message(call.message.chat.id, "Перейдите на сайт: https://habr.com/ru/all/")
    elif call.data == 'view_orders':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Программирование", callback_data='programming')
        btn2 = types.InlineKeyboardButton("Математика", callback_data='mathematics')
        back = types.InlineKeyboardButton("Главное меню", callback_data='main_menu')
        markup.add(btn1, btn2, back)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выберите категорию:", reply_markup=markup)
    elif call.data == 'main_menu':
        markup = make_main_keyboard()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Вы вернулись в главное меню", reply_markup=markup)


def start_bot():
    bot.polling(none_stop=True)


if __name__ == "__main__":
    start_bot()
