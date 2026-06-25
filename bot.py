import telebot
import requests
import urllib.parse

BOT_TOKEN = "8744804638:AAFfB_3UsZE6-9PbNc0Sf7CZrbhzPc4yDbA"
GEMINI_KEY = "AQ.Ab8RN6ICRaJYLgHmfj7RDyJ1jFFCf1f6KH3olzt_Mg66Jwo9MA"
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
    return gemini(f"Translate to English for image generation. Return only the translation, nothing else: {text}")

@bot.message_handler(commands=["start"])
def start(m):
    user_state[m.chat.id] = "chat"
    bot.send_message(m.chat.id,
        "Assalomu alaykum! 👑 Men Bek_AI man\n"
        "Men DIYORBEK tomonidan yaratilganman!\n\n"
        "🖼 Rasm — shunchaki tavsif yozing yoki /rasm\n"
        "🎵 Musiqa — /musiqa [tavsif]\n"
        "🗣 Savol — istalgan narsani yozing\n\n"
        "Masalan: 'bolajon kulyapti' deb yozsangiz rasm chizaman!")

@bot.message_handler(commands=["rasm"])
def rasm_cmd(m):
    p = m.text.replace("/rasm", "").strip()
    if p:
        yaratish_rasm(m, p)
    else:
        user_state[m.chat.id] = "rasm"
        bot.reply_to(m, "🖼 Rasm tavsifini yozing:")

@bot.message_handler(commands=["musiqa"])
def musiqa_cmd(m):
    p = m.text.replace("/musiqa", "").strip()
    if p:
        yaratish_musiqa(m, p)
    else:
        user_state[m.chat.id] = "musiqa"
        bot.reply_to(m, "🎵 Musiqa tavsifini yozing:")

def yaratish_rasm(m, p):
    msg = bot.reply_to(m, "🎨 Yaratilmoqda...")
    try:
        eng = translate(p)
        url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(eng) + "?width=1024&height=1024&nologo=true&enhance=true"
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            bot.delete_message(m.chat.id, msg.message_id)
            bot.send_photo(m.chat.id, r.content, caption=f"🖼 {p}")
        else:
            bot.edit_message_text("❌ Rasm yuklanmadi, qayta urining.", m.chat.id, msg.message_id)
    except Exception as e:
        bot.edit_message_text("❌ Xatolik, qayta urining.", m.chat.id, msg.message_id)

def yaratish_musiqa(m, p):
    msg = bot.reply_to(m, "🎵 Yaratilmoqda... (1-2 daqiqa)")
    try:
        eng = translate(p)
        url = "https://audio.pollinations.ai/" + urllib.parse.quote(eng)
        r = requests.get(url, timeout=120)
        if r.status_code == 200:
            bot.delete_message(m.chat.id, msg.message_id)
            bot.send_audio(m.chat.id, r.content, caption=f"🎵 {p}", title=p)
        else:
            bot.edit_message_text("❌ Musiqa yuklanmadi.", m.chat.id, msg.message_id)
    except:
        bot.edit_message_text("❌ Xatolik, qayta urining.", m.chat.id, msg.message_id)

@bot.message_handler(func=lambda m: True)
def handle(m):
    text = m.text
    chat_id = m.chat.id
    state = user_state.get(chat_id, "chat")

    if state == "rasm":
        user_state[chat_id] = "chat"
        yaratish_rasm(m, text)
        return

    if state == "musiqa":
        user_state[chat_id] = "chat"
        yaratish_musiqa(m, text)
        return

    keywords = ["rasm", "chiz", "ko'rsat", "draw", "image", "picture", "paint"]
    if any(k in text.lower() for k in keywords):
        yaratish_rasm(m, text)
        return

    prompt = (
        "Sen Bek_AI - aqlli, do'stona yordamchi. "
        "DIYORBEK tomonidan yaratilgansan. "
        "Foydalanuvchi tilida (O'zbek/Rus/Ingliz) javob ber. "
        "Qisqa va foydali bo'l.\n\n"
        f"Foydalanuvchi: {text}"
    )
    bot.reply_to(m, gemini(prompt))

bot.infinity_polling()
