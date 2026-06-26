import telebot
import requests
import urllib.parse
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = "8744804638:AAEN9xm9WPCXH7daFScPrIzkZ1gfC59PNvs"
GEMINI_KEY = "AQ.Ab8RN6LOrCZc3jcsLZwLDVS8U_bvEYCjue4yPHpzZSZXUBOcsg"
GROQ_KEY = "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"
REMOVEBG_KEY = "DX6v26gdPDxczmVffiJmqxQC"

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

bot = telebot.TeleBot(BOT_TOKEN)
user_state = {}
SYSTEM = "Sen Bek_AI — aqlli O'zbek yordamchisan. DIYORBEK yaratgan. FAQAT O'ZBEK TILIDA javob ber."

def gemini(text):
    try:
        r = requests.post(GEMINI_URL, json={"contents":[{"parts":[{"text":text}]}]}, timeout=30)
        return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except:
        return None

def groq(system, text):
    try:
        r = requests.post(GROQ_URL, headers={"Authorization":f"Bearer {GROQ_KEY}","Content-Type":"application/json"}, json={"model":"llama3-70b-8192","messages":[{"role":"system","content":system},{"role":"user","content":text}],"max_tokens":1000}, timeout=30)
        return r.json()["choices"][0]["message"]["content"].strip()
    except:
        return None

def suhbat(text):
    return groq(SYSTEM, text) or gemini(f"{SYSTEM}\n\n{text}") or "Xatolik, qayta urining."

def tarjima(text):
    return groq("Translate the Uzbek text to English image prompt only. Do not explain.", text) or text

def menu():
    m = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add(KeyboardButton("🖼 Rasm"), KeyboardButton("🎵 Musiqa"))
    m.add(KeyboardButton("🖼 Fon"), KeyboardButton("🗣 Suhbat"))
    return m

@bot.message_handler(commands=["start"])
def start(m):
    user_state[m.chat.id] = "chat"
    bot.send_message(m.chat.id, "Assalomu alaykum! 👑 Men Bek_AI man!\nDIYORBEK tomonidan yaratilganman!\n\nTugmani tanlang 👇", reply_markup=menu())

@bot.message_handler(content_types=["photo"])
def photo(m):
    if user_state.get(m.chat.id) == "fon":
        user_state[m.chat.id] = "fon_tavsif"
        user_state[f"{m.chat.id}_photo"] = m.photo[-1].file_id
        bot.send_message(m.chat.id, "Yangi fon tavsifini yozing:")

@bot.message_handler(func=lambda m: True)
def handle(m):
    text = m.text
    chat_id = m.chat.id
    state = user_state.get(chat_id, "chat")

    if text == "🖼 Rasm":
        user_state[chat_id] = "rasm"
        bot.send_message(chat_id, "🖼 Rasm tavsifini yozing:")
        return
    if text == "🎵 Musiqa":
        user_state[chat_id] = "musiqa"
        bot.send_message(chat_id, "🎵 Musiqa tavsifini yozing:")
        return
    if text == "🖼 Fon":
        user_state[chat_id] = "fon"
        bot.send_message(chat_id, "📸 Rasmingizni yuboring:")
        return
    if text == "🗣 Suhbat":
        user_state[chat_id] = "chat"
        bot.send_message(chat_id, "🗣 Savolingizni yozing:", reply_markup=menu())
        return

    if state == "rasm":
        user_state[chat_id] = "chat"
        msg = bot.send_message(chat_id, "🎨 Yaratilmoqda...")
        try:
            eng = tarjima(text)
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(eng)},4k?width=1024&height=1024&nologo=true"
            r = requests.get(url, timeout=60)
            bot.delete_message(chat_id, msg.message_id)
            bot.send_photo(chat_id, r.content, caption=f"🖼 {text}", reply_markup=menu())
        except:
            bot.edit_message_text("❌ Xatolik, qayta urining.", chat_id, msg.message_id)
        return

    if state == "musiqa":
        user_state[chat_id] = "chat"
        msg = bot.send_message(chat_id, "🎵 Yaratilmoqda...")
        try:
            eng = tarjima(text)
            url = f"https://audio.pollinations.ai/{urllib.parse.quote(eng)}"
            r = requests.get(url, timeout=120)
            bot.delete_message(chat_id, msg.message_id)
            bot.send_audio(chat_id, r.content, caption=f"🎵 {text}", reply_markup=menu())
        except:
            bot.edit_message_text("❌ Xatolik, qayta urining.", chat_id, msg.message_id)
        return

    if state == "fon_tavsif":
        user_state[chat_id] = "chat"
        file_id = user_state.get(f"{chat_id}_photo")
        msg = bot.send_message(chat_id, "🖼 Fon o'zgartirilmoqda...")
        try:
            fi = bot.get_file(file_id)
            img = requests.get(f"https://api.telegram.org/file/bot{BOT_TOKEN}/{fi.file_path}").content
            r = requests.post("https://api.remove.bg/v1.0/removebg", files={"image_file":img}, data={"size":"auto"}, headers={"X-Api-Key":REMOVEBG_KEY})
            bot.delete_message(chat_id, msg.message_id)
            bot.send_photo(chat_id, r.content, caption="✅ Fon o'chirildi!", reply_markup=menu())
        except:
            bot.edit_message_text("❌ Xatolik, qayta urining.", chat_id, msg.message_id)
        return

    bot.reply_to(m, suhbat(text), reply_markup=menu())

bot.infinity_polling()
