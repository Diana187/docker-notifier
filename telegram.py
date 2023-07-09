import telebot


def send_telegram_message(api_token, chat_id, text):
    bot = telebot.TeleBot(api_token)
    bot.send_message(chat_id, text)
