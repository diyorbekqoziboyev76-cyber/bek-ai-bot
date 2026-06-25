import telebot
import requests
import urllib.parse
from telebot.types import BotCommand, ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = "8744804638:AAFfB_3UsZE6-9PbNc0Sf7CZrbhzPc4yDbA"
GEMINI_KEY = "AQ.Ab8RN6ICRaJYLgHmfj7RDyJ1jFFCf1f6KH3olzt_Mg66Jwo9MA"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"

bot = telebot.TeleBot(BOT_TOKEN)

bot.set_my_commands([
    BotCommand("start", "Botni boshlash"),
    BotCommand("rasm", "Rasm yaratish"),
    BotCommand("musiqa", "Musiqa yaratish"),
])

user_mode = {}

def gemini(text):
    r = requests.post(GEMINI_URL, json={"contents":[{"parts":[{"text":text}]}]})
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]

def translate_to_english(text):
    return gemini(f"Translate to English for image generation, only translation: {text}")

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🖼 Rasm yaratish"))
    markup.add(KeyboardButton("🎵 Musiqa yaratish"))
    markup.add(KeyboardButton("🗣 Suhbat"))
    return markup

@bot.message_handler(commands=["start"])
def start(m):
    user_mode[m.chat.id] = None
    bot.send_message(m.chat.id,
        "Assalomu alaykum! Men Bek_AI man 👑\nMen DIYORBEK tomonidan yaratilganman!\n\nQuyidagilardan birini tanlang:",
        reply_markup=main_menu())

@bot.message_handler(commands=["rasm"])
def rasm_cmd(m):
    user_mode[m.chat.id] = "rasm"
    bot.reply_to(m, "🖼 Rasm tavsifini yozing (O'zbekcha yoki inglizcha):")

@bot.message_handler(commands=["musiqa"])
def musiqa_cmd(m):
    user_mode[m.chat.id] = "musiqa"
    bot.reply_to(m, "🎵 Musiqa tavsifini yozing:")

@bot.message_handler(func=lambda m: True)
def handle(m):
    chat_id = m.chat.id
    text = m.text

    if text == "🖼 Rasm yaratish":
        user_mode[chat_id] = "rasm"
        bot.send_message(chat_id, "🖼 Rasm tavsifini yozing (O'zbekcha yozaversang bo'ladi):")
        return

    if text == "🎵 Musiqa yaratish":
        user_mode[chat_id] = "musiqa"
        bot.send_message(chat_id, "🎵 Musiqa tavsifini yozing:")
        return

    if text == "🗣 Suhbat":
        user_mode[chat_id] = "suhbat"
        bot.send_message(chat_id, "🗣 Savolingizni yozing:")
        return

    mode = user_mode.get(chat_id)

    if mode == "rasm":
        bot.send_message(chat_id, "🎨 Yaratilmoqda...")
        eng = translate_to_english(text)
        url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(eng)
        bot.send_photo(chat_id, url, caption=text)
        return

    if mode == "musiqa":
        bot.send_message(chat_id, "🎵 Yaratilmoqda...")
        eng = translate_to_english(text)
        url = "https://audio.pollinations.ai/" + urllib.parse.quote(eng)
        bot.send_audio(chat_id, url, caption=text)
        return

    prompt = "Sen Bek_AI - aqlli yordamchi. DIYORBEK tomonidan yaratilgansan. Foydalanuvchi tilida javob ber.\n\n" + text
    bot.reply_to(m, gemini(prompt))

bot.infinity_polling()
