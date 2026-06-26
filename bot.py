import telebot, requests, urllib.parse
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = "8744804638:AAEN9xm9WPCXH7daFScPrIzkZ1gfC59PNvs"
GEMINI_KEY = "AQ.Ab8RN6LOrCZc3jcsLZwLDVS8U_bvEYCjue4yPHpzZSZXUBOcsg"
GROQ_KEY = "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"
OWNER_ID = "7709192535"

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

bot = telebot.TeleBot(BOT_TOKEN)
user_state = {}
users = set()

def tarjima(text):
    try:
        r = requests.post(GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"},
            json={"model": "llama3-70b-8192", "messages": [{"role": "user", "content": f"Translate to English only, no explanation: {text}"}], "max_tokens": 200},
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

def is_url(text):
    return text.startswith("http://") or text.startswith("https://")

def tahrirla(m, chat_id, img_source, tavsif, is_link=False):
    msg = bot.send_message(chat_id, "✏️ O'zgartirilmoqda...")
    try:
        if is_link:
            img_url = img_source
        else:
            fi = bot.get_file(img_source)
            img_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{fi.file_path}"
        eng = tarjima(tavsif)
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

@bot.message_handler(commands=["start"])
def start(m):
    chat_id = m.chat.id
    user_state[chat_id] = "chat"
    
    # Yangi foydalanuvchi
    if chat_id not in users:
        users.add(chat_id)
        name = m.from_user.first_name or "Noma'lum"
        username = f"@{m.from_user.username}" if m.from_user.username else "yo'q"
        try:
            bot.send_message(OWNER_ID,
                f"👤 Yangi foydalanuvchi!\n"
                f"Ism: {name}\n"
                f"Username: {username}\n"
                f"ID: {chat_id}\n"
                f"Jami: {len(users)} ta")
        except:
            pass
    
    bot.send_message(chat_id,
        "Assalomu alaykum! 👑 Men Bek_AI man!\n"
        "DIYORBEK tomonidan yaratilganman!\n\n"
        "📌 Ishlatish:\n"
        "🖼 Matn yozing — yangi rasm yaratadi\n"
        "📸 Rasm yuboring — tavsif so'raydi\n"
        "🔗 URL yuboring — tavsif so'raydi\n\n"
        "Sinab ko'ring! 👇", reply_markup=menu())

@bot.message_handler(commands=["stats"])
def stats(m):
    if m.chat.id == OWNER_ID:
        bot.reply_to(m, f"📊 Statistika:\n👥 Jami foydalanuvchilar: {len(users)} ta")
    else:
        bot.reply_to(m, "❌ Siz admin emassiz!")

@bot.message_handler(content_types=["photo"])
def photo_handler(m):
    chat_id = m.chat.id
    file_id = m.photo[-1].file_id
    user_state[f"{chat_id}_photo"] = file_id
    if m.caption:
        user_state[chat_id] = "chat"
        tahrirla(m, chat_id, file_id, m.caption, is_link=False)
    else:
        user_state[chat_id] = "tahrirla"
        bot.send_message(chat_id, "✏️ Rasmga qanday o'zgartirish kiritay?")

@bot.message_handler(func=lambda m: True)
def handle(m):
    text = m.text
    chat_id = m.chat.id
    state = user_state.get(chat_id, "chat")

    if text == "🖼 Yangi rasm yaratish":
        user_state[chat_id] = "rasm"
        bot.send_message(chat_id, "🖼 Qanday rasm chizay?")
        return

    lines = text.strip().split("\n")
    if len(lines) >= 2 and is_url(lines[0]):
        tahrirla(m, chat_id, lines[0], "\n".join(lines[1:]), is_link=True)
        return

    if is_url(text):
        user_state[chat_id] = "url_tahrirla"
        user_state[f"{chat_id}_url"] = text
        bot.send_message(chat_id, "✏️ Qanday o'zgartirish kiritay?")
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
            tahrirla(m, chat_id, file_id, text, is_link=False)
        return

    if state == "url_tahrirla":
        user_state[chat_id] = "chat"
        url_link = user_state.get(f"{chat_id}_url")
        if url_link:
            tahrirla(m, chat_id, url_link, text, is_link=True)
        return

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

bot.infinity_polling()
