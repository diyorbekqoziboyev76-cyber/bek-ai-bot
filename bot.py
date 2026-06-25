import telebot
import requests
import urllib.parse

BOT_TOKEN = "8744804638:AAFfB_3UsZE6-9PbNc0Sf7CZrbhzPc4yDbA"
GEMINI_KEY = "AQ.Ab8RN6ICRaJYLgHmfj7RDyJ1jFFCf1f6KH3olzt_Mg66Jwo9MA"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"

bot = telebot.TeleBot(BOT_TOKEN)

def gemini(text):
    r = requests.post(GEMINI_URL, json={"contents":[{"parts":[{"text":"Sen Bek_AI yordamchisan. Foydalanuvchi tilida javob ber.\n\n"+text}]}]})
    return r.json()["candidates"][0]["content"]["parts"][0]["text"]

@bot.message_handler(commands=["start"])
def start(m):
    bot.reply_to(m, "👑 Salom! Men Bek_AI!\n\n🗣 Suhbat - istalgan savol\n🖼 /rasm [tavsif]\n🎵 /musiqa [tavsif]")

@bot.message_handler(commands=["rasm"])
def rasm(m):
    p = m.text.replace("/rasm","").strip()
    if not p:
        bot.reply_to(m, "Masalan: /rasm tog manzarasi")
        return
    bot.reply_to(m, "🎨 Yaratilmoqda...")
    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(p)
    bot.send_photo(m.chat.id, url, caption=p)

@bot.message_handler(commands=["musiqa"])
def musiqa(m):
    p = m.text.replace("/musiqa","").strip()
    if not p:
        bot.reply_to(m, "Masalan: /musiqa lo-fi relaxing")
        return
    bot.reply_to(m, "🎵 Yaratilmoqda...")
    url = "https://audio.pollinations.ai/" + urllib.parse.quote(p)
    bot.send_audio(m.chat.id, url, caption=p)

@bot.message_handler(func=lambda m: True)
def chat(m):
    bot.reply_to(m, gemini(m.text))

bot.infinity_polling()
