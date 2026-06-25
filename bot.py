import telebot
import requests
import urllib.parse
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = "8744804638:AAFfB_3UsZE6-9PbNc0Sf7CZrbhzPc4yDbA"
GEMINI_KEY = "Ab8RN6IO6cG1uDE5JRowFA2pWfedZLfpUmkp3WSBl7UgmW"
GROQ_KEY = "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"

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

bot = telebot.TeleBot(BOT_TOKEN)
user_state = {}

def gemini(prompt):
    try:
        r = requests.post(GEMINI_URL,
            json={"contents":[{"parts":[{"text":prompt}]}]},
            timeout=30)
        return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        return None

def groq(system, text):
    try:
        r = requests.post(GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={
                "model": "llama3-70b-8192",
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": text}
                ],
                "max_tokens": 1000
            }, timeout=30)
        return r.json()["choices"][0]["message"]["content"].strip()
    except:
        return None

def suhbat(text):
    system = (
        "Sen Bek_AI — aqlli, do'stona O'zbek yordamchisan. "
        "DIYORBEK tomonidan yaratilgansan. "
        "FAQAT O'ZBEK TILIDA javob ber. "
        "Qisqa, aniq va foydali bo'l."
    )
    javob = groq(system, text)
    if javob:
        return javob
    javob = gemini(f"{system}\n\nFoydalanuvchi: {text}")
    if javob:
        return javob
    return "Xatolik yuz berdi, qayta urining."

def tarjima(text):
    prompt = f"Translate this text to English for AI image generation. Return ONLY the English translation: {text}"
    eng = groq("You are a translator.", prompt)
    if eng:
        return eng
    eng = gemini(f"Translate to English only, no explanation: {text}")
    if eng:
        return eng
    return text

def menu():
    m = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add(KeyboardButton("🖼 Rasm"), KeyboardButton("🎵 Musiqa"))
    m.add(KeyboardButton("🗣 Suhbat"))
    return m

@bot.message_handler(commands=["start"])
def start(m):
    user_state[m.chat.id] = "chat"
    bot.send_message(m.chat.id,
        "Assalomu alaykum! 👑 Men Bek_AI man!\n"
        "Men DIYORBEK tomonidan yaratilganman!\n\n"
        "Tugmani tanlang 👇",
        reply_markup=menu())

@bot.message_handler(func=lambda m: True)
def handle(m):
    if not m.text:
        return
    text = m.text
    chat_id = m.chat.id
    state = user_state.get(chat_id, "chat")

    if text == "🖼 Rasm":
        user_state[chat_id] = "rasm"
        bot.send_message(chat_id, "🖼 Rasm tavsifini yozing:\nMisol: kichik bola o'ynayapti")
        return

    if text == "🎵 Musiqa":
        user_state[chat_id] = "musiqa"
        bot.send_message(chat_id, "🎵 Musiqa tavsifini yozing:\nMisol: tinch lo-fi")
        return

    if text == "🗣 Suhbat":
        user_state[chat_id] = "chat"
        bot.send_message(chat_id, "🗣 Savolingizni yozing:", reply_markup=menu())
        return

    if state == "rasm":
        user_state[chat_id] = "chat"
        msg = bot.send_message(chat_id, "🎨 Rasm yaratilmoqda...")
        try:
            eng = tarjima(text)
            full = f"{eng}, photorealistic, high quality, 4k, detailed"
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(full)}?width=1024&height=1024&nologo=true&enhance=true"
            r = requests.get(url, timeout=60)
            if r.status_code == 200 and len(r.content) > 1000:
                bot.delete_message(chat_id, msg.message_id)
                bot.send_photo(chat_id, r.content, caption=f"🖼 {text}", reply_markup=menu())
            else:
                bot.edit_message_text("❌ Rasm yuklanmadi, qayta urining.", chat_id, msg.message_id)
        except Exception as e:
            bot.edit_message_text("❌ Xatolik, qayta urining.", chat_id, msg.message_id)
        return

    if state == "musiqa":
        user_state[chat_id] = "chat"
        msg = bot.send_message(chat_id, "🎵 Musiqa yaratilmoqda... (1-2 daqiqa kuting)")
        try:
            eng = tarjima(text)
            url = f"https://audio.pollinations.ai/{urllib.parse.quote(eng)}"
            r = requests.get(url, timeout=120)
            if r.status_code == 200 and len(r.content) > 1000:
                bot.delete_message(chat_id, msg.message_id)
                bot.send_audio(chat_id, r.content, caption=f"🎵 {text}", reply_markup=menu())
            else:
                bot.edit_message_text("❌ Musiqa yuklanmadi, qayta urining.", chat_id, msg.message_id)
        except:
            bot.edit_message_text("❌ Xatolik, qayta urining.", chat_id, msg.message_id)
        return

    javob = suhbat(text)
    bot.reply_to(m, javob, reply_markup=menu())

bot.infinity_polling()
