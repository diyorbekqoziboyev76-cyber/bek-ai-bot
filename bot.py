import telebot, requests, urllib.parse
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = "8744804638:AAEN9xm9WPCXH7daFScPrIzkZ1gfC59PNvs"
GEMINI_KEY = "AQ.Ab8RN6LOrCZc3jcsLZwLDVS8U_bvEYCjue4yPHpzZSZXUBOcsg"
GROQ_KEY = "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"

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

bot = telebot.TeleBot(BOT_TOKEN)
user_state = {}

def tarjima(text):
    try:
        r = requests.post(GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={"model": "llama3-70b-8192", "messages": [{"role": "user", "content": f"Translate to English only: {text}"}], "max_tokens": 200},
            timeout=15)
        return r.json()["choices"][0]["message"]["content"].strip()
    except:
        try:
            r = requests.post(GEMINI_URL,
                json={"contents": [{"parts": [{"text": f"Translate to English only: {text}"}]}]},
                timeout=15)
            return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        except:
            return text

def menu():
    m = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    m.add(KeyboardButton("🖼 Yangi rasm yaratish"))
    return m

@bot.message_handler(commands=["start"])
def start(m):
    user_state[m.chat.id] = "chat"
    bot.send_message(m.chat.id,
        "Assalomu alaykum! 👑 Men Bek_AI man!\n"
        "DIYORBEK tomonidan yaratilganman!\n\n"
        "📌 Ishlatish:\n"
        "🖼 Yangi rasm — tavsif yozing\n"
        "✏️ Rasmni o'zgartirish — rasm yuboring va tavsif yozing\n\n"
        "Sinab ko'ring! 👇", reply_markup=menu())

@bot.message_handler(content_types=["photo"])
def photo_handler(m):
    chat_id = m.chat.id
    file_id = m.photo[-1].file_id
    user_state[f"{chat_id}_photo"] = file_id
    
    # Agar caption bilan kelsa
    if m.caption:
        user_state[chat_id] = "chat"
        tahrirla(m, chat_id, file_id, m.caption)
    else:
        user_state[chat_id] = "tahrirla"
        bot.send_message(chat_id, "✏️ Rasmga qanday o'zgartirish kiritay?\nMisol: fonni dengizga o'zgartir")

def tahrirla(m, chat_id, file_id, tavsif):
    msg = bot.send_message(chat_id, "✏️ O'zgartirilmoqda...")
    try:
        fi = bot.get_file(file_id)
        img_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{fi.file_path}"
        eng = tarjima(tavsif)
        
        # Pollinations image-to-image
        prompt = urllib.parse.quote(f"{eng}, high quality, 4k, detailed")
        img_encoded = urllib.parse.quote(img_url)
        url = f"https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&nologo=true&image={img_encoded}"
        
        r = requests.get(url, timeout=90)
        if r.status_code == 200 and len(r.content) > 5000:
            bot.delete_message(chat_id, msg.message_id)
            bot.send_photo(chat_id, r.content, caption=f"✅ {tavsif}", reply_markup=menu())
        else:
            bot.edit_message_text("❌ Xatolik, qayta urining.", chat_id, msg.message_id)
    except:
        bot.edit_message_text("❌ Xatolik, qayta urining.", chat_id, msg.message_id)

@bot.message_handler(func=lambda m: True)
def handle(m):
    text = m.text
    chat_id = m.chat.id
    state = user_state.get(chat_id, "chat")

    if text == "🖼 Yangi rasm yaratish":
        user_state[chat_id] = "rasm"
        bot.send_message(chat_id, "🖼 Qanday rasm chizay?\nMisol: kichik bola o'ynayapti")
        return

    if state == "rasm":
        user_state[chat_id] = "chat"
        msg = bot.send_message(chat_id, "🎨 Yaratilmoqda...")
        try:
            eng = tarjima(text)
            url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(eng)},high quality,4k?width=1024&height=1024&nologo=true"
            r = requests.get(url, timeout=60)
            if r.status_code == 200:
                bot.delete_message(chat_id, msg.message_id)
                bot.send_photo(chat_id, r.content, caption=f"🖼 {text}", reply_markup=menu())
            else:
                bot.edit_message_text("❌ Xatolik, qayta urining.", chat_id, msg.message_id)
        except:
            bot.edit_message_text("❌ Xatolik, qayta urining.", chat_id, msg.message_id)
        return

    if state == "tahrirla":
        user_state[chat_id] = "chat"
        file_id = user_state.get(f"{chat_id}_photo")
        if file_id:
            tahrirla(m, chat_id, file_id, text)
        return

    bot.reply_to(m, "🖼 Rasm yaratish uchun tavsif yozing yoki rasm yuboring!", reply_markup=menu())

bot.infinity_polling()
