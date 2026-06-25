import telebot
import requests
import urllib.parse
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = "8744804638:AAFfB_3UsZE6-9PbNc0Sf7CZrbhzPc4yDbA"
GEMINI_KEY = "AQ.Ab8RN6JX_GSqp-BR2jFHYP38_VeJuNQNuqmKrcjKAJHnvtxvAw"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"

bot = telebot.TeleBot(BOT_TOKEN)
user_state = {}

def gemini(text):
    try:
        r = requests.post(GEMINI_URL, json={"contents":[{"parts":[{"text":text}]}]}, timeout=30)
        return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except:
        return "Xatolik yuz berdi, qayta urining."

def translate(text):
    return gemini(f"Translate to English for image generation. Return ONLY the translation: {text}")

def menu():
    m = ReplyKeyboardMarkup(resize_keyboard=True)
    m.add(KeyboardButton("🖼 Rasm yaratish"))
    m.add(KeyboardButton("🎵 Musiqa yaratish"))
    m.add(KeyboardButton("🗣 Suhbat"))
    return m

def yaratish_rasm(m, p):
    msg = bot.reply_to(m, "🎨 Rasm yaratilmoqda...")
    try:
        eng = translate(p)
        prompt = urllib.parse.quote(f"{eng}, high quality, realistic, 4k")
        url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true&enhance=true"
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            bot.delete_message(m.chat.id, msg.message_id)
            bot.send_photo(m.chat.id, r.content, caption=f"🖼 {p}", reply_markup=menu())
        else:
            bot.edit_message_text("❌ Rasm yuklanmadi, qayta urining.", m.chat.id, msg.message_id)
    except:
        bot.edit_message_text("❌ Xatolik, qayta urining.", m.chat.id, msg.message_id)

def yaratish_musiqa(m, p):
    msg = bot.reply_to(m, "🎵 Musiqa yaratilmoqda... (1-2 daqiqa)")
    try:
        eng = translate(p)
        url = "https://audio.pollinations.ai/" + urllib.parse.quote(eng)
        r = requests.get(url, timeout=120)
        if r.status_code == 200:
            bot.delete_message(m.chat.id, msg.message_id)
            bot.send_audio(m.chat.id, r.content, caption=f"🎵 {p}", title=p, reply_markup=menu())
        else:
            bot.edit_message_text("❌ Musiqa yuklanmadi.", m.chat.id, msg.message_id)
    except:
        bot.edit_message_text("❌ Xatolik, qayta urining.", m.chat.id, msg.message_id)

@bot.message_handler(commands=["start"])
def start(m):
    user_state[m.chat.id] = "chat"
    bot.send_message(m.chat.id,
        "Assalomu alaykum! 👑 Men Bek_AI man!\n"
        "Men DIYORBEK tomonidan yaratilganman!\n\n"
        "Quyidagi tugmalardan birini tanlang:",
        reply_markup=menu())

@bot.message_handler(func=lambda m: True)
def handle(m):
    if not m.text:
        return
    text = m.text
    chat_id = m.chat.id
    state = user_state.get(chat_id, "chat")

    if text == "🖼 Rasm yaratish":
        user_state[chat_id] = "rasm"
        bot.send_message(chat_id, "🖼 Rasm tavsifini yozing:\nMisol: tog' manzarasi, bolalar o'ynayapti")
        return

    if text == "🎵 Musiqa yaratish":
        user_state[chat_id] = "musiqa"
        bot.send_message(chat_id, "🎵 Musiqa tavsifini yozing:\nMisol: tinch lo-fi, o'zbek milliy")
        return

    if text == "🗣 Suhbat":
        user_state[chat_id] = "chat"
        bot.send_message(chat_id, "🗣 Savolingizni yozing:", reply_markup=menu())
        return

    if state == "rasm":
        user_state[chat_id] = "chat"
        yaratish_rasm(m, text)
        return

    if state == "musiqa":
        user_state[chat_id] = "chat"
        yaratish_musiqa(m, text)
        return

    prompt = (
        "Sen Bek_AI — aqlli O'zbek yordamchisan. "
        "DIYORBEK tomonidan yaratilgansan. "
        "HAR DOIM O'ZBEK TILIDA javob ber. "
        "Qisqa va foydali bo'l.\n\n"
        f"Foydalanuvchi: {text}"
    )
    bot.reply_to(m, gemini(prompt), reply_markup=menu())

bot.infinity_polling()
