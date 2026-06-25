import telebot
import requests
import urllib.parse
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

BOT_TOKEN = "8744804638:AAG1MMNCoonI7-pM-XTktQhXzBx0jo_TSZ0"
GEMINI_KEY = "Ab8RN6IO6cG1uDE5JRowFA2pWfedZLfpUmkp3WSBl7UgmW"
GROQ_KEY = "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"
REMOVEBG_KEY = "SX3ShdFpjCrppDhqAd2LS769"

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

bot = telebot.TeleBot(BOT_TOKEN)
user_state = {}

SYSTEM = (
    "Sen Bek_AI — aqlli, do'stona O'zbek yordamchisan. "
    "DIYORBEK tomonidan yaratilgansan. "
    "FAQAT O'ZBEK TILIDA javob ber. "
    "Qisqa, aniq va foydali bo'l."
)

def gemini(text):
    try:
        r = requests.post(GEMINI_URL,
            json={"contents":[{"parts":[{"text":text}]}]},
            timeout=30)
        return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except:
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
    javob = groq(SYSTEM, text)
    if javob:
        return javob
    javob = gemini(f"{SYSTEM}\n\nFoydalanuvchi: {text}")
    return javob or "Xatolik yuz berdi, qayta urining."

def tarjima(text):
    eng = groq("You are a translator. Translate Uzbek/Russian to English. Return ONLY translation.", text)
    if eng:
        return eng
    eng = gemini(f"Translate to English only: {text}")
    return eng or text

def menu():
    m = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    m.add(KeyboardButton("🖼 Rasm"), KeyboardButton("🎵 Musiqa"))
    m.add(KeyboardButton("🖼 Fon o'zgartir"), KeyboardButton("🗣 Suhbat"))
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
    if not m.text and not m.photo:
        return
    chat_id = m.chat.id
    state = user_state.get(chat_id, "chat")

    if m.photo:
        if state == "fon":
            user_state[chat_id] = "fon_tavsif"
            user_state[f"{chat_id}_photo"] = m.photo[-1].file_id
            bot.send_message(chat_id, "🖼 Yangi fon tavsifini yozing:\nMisol: dengiz bo'yi, tog' manzarasi")
        return

    text = m.text

    if text == "🖼 Rasm":
        if text == "🖼 Rasm":
    user_state[chat_id] = "rasm"
    bot.send_message(chat_id, "🖼 Rasm tavsifini yozing:\nMisol: kichik bola o'ynayapti")
    return

if text == "🎵 Musiqa":
    user_state[chat_id] = "musiqa"
    bot.send_message(chat_id, "🎵 Musiqa tavsifini yozing:\nMisol: tinch lo-fi")
    return

if text == "🖼 Fon o'zgartir":
    user_state[chat_id] = "fon"
    bot.send_message(chat_id, "📸 Avval rasm yuboring.")
    return

if text == "🗣 Suhbat":
    user_state[chat_id] = "chat"
    bot.send_message(chat_id, "🗣 Savolingizni yozing:", reply_markup=menu())
    return


# RASM
if state == "rasm":
    user_state[chat_id] = "chat"
    msg = bot.send_message(chat_id, "🎨 Rasm yaratilmoqda...")

    try:
        eng = tarjima(text)

        prompt = f"ultra realistic, photorealistic, high detail, cinematic lighting, 4k, {eng}"

        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1024&height=1024&nologo=true"

        r = requests.get(url, timeout=60)

        if r.status_code == 200:
            bot.delete_message(chat_id, msg.message_id)
            bot.send_photo(
                chat_id,
                r.content,
                caption=f"🖼 {text}",
                reply_markup=menu()
            )
        else:
            bot.edit_message_text(
                f"❌ Xatolik: {r.status_code}",
                chat_id,
                msg.message_id
            )

    except Exception as e:
        bot.edit_message_text(
            f"❌ Xatolik:\n{e}",
            chat_id,
            msg.message_id
        )

    return


# MUSIQA
if state == "musiqa":
    user_state[chat_id] = "chat"
    msg = bot.send_message(chat_id, "🎵 Musiqa yaratilmoqda...")

    try:
        eng = tarjima(text)

        url = f"https://audio.pollinations.ai/{urllib.parse.quote(eng)}"

        r = requests.get(url, timeout=120)

        if r.status_code == 200:
            bot.delete_message(chat_id, msg.message_id)

            bot.send_audio(
                chat_id,
                r.content,
                caption=f"🎵 {text}",
                reply_markup=menu()
            )
        else:
            bot.edit_message_text(
                f"❌ Xatolik: {r.status_code}",
                chat_id,
                msg.message_id
            )

    except Exception as e:
        bot.edit_message_text(
            f"❌ Xatolik:\n{e}",
            chat_id,
            msg.message_id
        )

    return


# FON O'ZGARTIR
if state == "fon":
    user_state[chat_id] = "chat"

    file_id = user_state.get(f"{chat_id}_photo")

    if not file_id:
        bot.send_message(
            chat_id,
            "❌ Avval rasm yuboring.",
            reply_markup=menu()
        )
        return

    msg = bot.send_message(chat_id, "🖼 Fon olib tashlanmoqda...")

    try:
        file_info = bot.get_file(file_id)

        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"

        img_data = requests.get(file_url).content

        r = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files={"image_file": img_data},
            data={"size": "auto"},
            headers={"X-Api-Key": REMOVEBG_KEY}
        )

        if r.status_code == 200:
            bot.delete_message(chat_id, msg.message_id)

            bot.send_document(
                chat_id,
                r.content,
                visible_file_name="background_removed.png"
            )

            bot.send_message(
                chat_id,
                "✅ Fon olib tashlandi.",
                reply_markup=menu()
            )
        else:
            bot.edit_message_text(
                f"❌ RemoveBG xatosi: {r.status_code}",
                chat_id,
                msg.message_id
            )

    except Exception as e:
        bot.edit_message_text(
            f"❌ Xatolik:\n{e}",
            chat_id,
            msg.message_id
        )

    return


javob = suhbat(text)
bot.reply_to(m, javob, reply_markup=menu())
