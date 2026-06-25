import telebot
import requests
import urllib.parse

BOT_TOKEN = "8744804638:AAFfB_3UsZE6-9PbNc0Sf7CZrbhzPc4yDbA"
GEMINI_KEY = "AQ.Ab8RN6ICRaJYLgHmfj7RDyJ1jFFCf1f6KH3olzt_Mg66Jwo9MA"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"

bot = telebot.TeleBot(BOT_TOKEN)

def gemini(text):
    r = requests.post(GEMINI_URL, json={"contents":[{"parts":[{"text":text}]}]})
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]

@bot.message_handler(commands=["start"])
def start(m):
    bot.reply_to(m, "Assalomu alaykum! Men Bek_AI man 👑\nMen DIYORBEK tomonidan yaratilganman!\n\n🖼 /rasm bolajon kulyapti\n🎵 /musiqa lo-fi\n🗣 Istalgan savol yozing")

@bot.message_handler(commands=["rasm"])
def rasm(m):
    p = m.text.replace("/rasm","").strip()
    if not p:
        bot.reply_to(m, "Masalan:\n/rasm bolajon kulyapti")
        return
    bot.reply_to(m, "🎨 Yaratilmoqda...")
    eng = gemini(f"Translate to English only, no extra text: {p}")
    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(eng.strip())
    bot.send_photo(m.chat.id, url, caption=p)

@bot.message_handler(commands=["musiqa"])
def musiqa(m):
    p = m.text.replace("/musiqa","").strip()
    if not p:
        bot.reply_to(m, "Masalan:\n/musiqa lo-fi relaxing")
        return
    bot.reply_to(m, "🎵 Yaratilmoqda...")
    eng = gemini(f"Translate to English only, no extra text: {p}")
    url = "https://audio.pollinations.ai/" + urllib.parse.quote(eng.strip())
    bot.send_audio(m.chat.id, url, caption=p)

@bot.message_handler(func=lambda m: True)
def chat(m):
    prompt = f"Sen Bek_AI - aqlli yordamchi. DIYORBEK yaratgan. Foydalanuvchi tilida javob ber:\n\n{m.text}"
    bot.reply_to(m, gemini(prompt))

bot.infinity_polling()
