import telebot
import requests
import urllib.parse
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = "8744804638:AAG1MMNCoonI7-pM-XTktQhXzBx0jo_TSZ0"
GEMINI_KEY = "Ab8RN6IO6cG1uDE5JRowFA2pWfedZLfpUmkp3WSBl7UgmW"
GROQ_KEY  = "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"
REMOVEBG_KEY = "SX3ShdFpjCrppDhqAd2LS769"

bot = telebot.TeleBot(BOT_TOKEN)

user_state = {}

def menu():
    m = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add(
        KeyboardButton("🖼 Rasm"),
        KeyboardButton("🎵 Musiqa")
    )
    m.add(
        KeyboardButton("🖼 Fon o'zgartir"),
        KeyboardButton("🗣 Suhbat")
    )
    return m


@bot.message_handler(commands=["start"])
def start(message):
    user_state[message.chat.id] = "chat"

    bot.send_message(
        message.chat.id,
        "Assalomu alaykum! 👑 Men Bek_AI man!",
        reply_markup=menu()
    )


@bot.message_handler(func=lambda m: True)
def handle(m):

    chat_id = m.chat.id

    if not m.text:
        return

    text = m.text

    if text == "🖼 Rasm":
        bot.send_message(
            chat_id,
            "🖼 Rasm tavsifini yuboring."
        )
        return

    if text == "🎵 Musiqa":
        bot.send_message(
            chat_id,
            "🎵 Musiqa tavsifini yuboring."
        )
        return

    if text == "🖼 Fon o'zgartir":
        bot.send_message(
            chat_id,
            "📸 Rasm yuboring."
        )
        return

    if text == "🗣 Suhbat":
        bot.send_message(
            chat_id,
            "🗣 Savolingizni yozing."
        )
        bot.send_message(
    chat_id,
    "AI javobi hozircha ulanmagan."


bot.infinity_polling(skip_pending=True)
