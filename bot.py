import telebot
import yt_dlp
import os
import requests
import json
import base64
import hashlib
import hmac
import time
from urllib.parse import quote

# ============================================================
# 🔑 API KALITLAR - bularni o'zingizniki bilan almashtiring!
# ============================================================
BOT_TOKEN = "8744804638:AAFutJj7V02I1mKmVFpUZhiXz7h3A_tYGv0"          
ACR_ACCESS_KEY = "2Z8VBWhdDxxA1NeMONEsPlUzmciLamQrUcSKC41f"
ACRCLOUD_HOST = "identify-ap-southeast-1.acrcloud.com"
YOUTUBE_API_KEY = "AIzaSyBTnWcgpl7eyYeT54Bx5hrs4NkJjds5bCs"

bot = telebot.TeleBot(BOT_TOKEN)

# ============================================================
# 🎵 AUDD.IO orqali musiqa aniqlash
# ============================================================
def audd_recognize(audio_path):
    try:
        with open(audio_path, 'rb') as f:
            data = {'api_token': AUDD_API_KEY, 'return': 'spotify,apple_music'}
            files = {'file': f}
            response = requests.post('https://api.audd.io/', data=data, files=files)
            result = response.json()
            if result.get('status') == 'success' and result.get('result'):
                r = result['result']
                return {
                    'title': r.get('title', 'Noma\'lum'),
                    'artist': r.get('artist', 'Noma\'lum'),
                    'album': r.get('album', ''),
                    'source': 'AudD'
                }
    except Exception as e:
        print(f"AudD xato: {e}")
    return None

# ============================================================
# 🎵 ACRCLOUD orqali musiqa aniqlash
# ============================================================
def acrcloud_recognize(audio_path):
    try:
        http_method = "POST"
        http_uri = "/v1/identify"
        data_type = "audio"
        signature_version = "1"
        timestamp = str(time.time())

        string_to_sign = "\n".join([http_method, http_uri, ACRCLOUD_ACCESS_KEY,
                                     data_type, signature_version, timestamp])
        sign = base64.b64encode(
            hmac.new(ACRCLOUD_SECRET_KEY.encode('ascii'),
                     string_to_sign.encode('ascii'),
                     digestmod=hashlib.sha1).digest()
        ).decode('ascii')

        with open(audio_path, 'rb') as f:
            audio_data = f.read()

        files = {'sample': ('audio.mp3', audio_data, 'audio/mpeg')}
        data = {
            'access_key': ACRCLOUD_ACCESS_KEY,
            'sample_bytes': len(audio_data),
            'timestamp': timestamp,
            'signature': sign,
            'data_type': data_type,
            'signature_version': signature_version
        }

        url = f"https://{ACRCLOUD_HOST}/v1/identify"
        response = requests.post(url, files=files, data=data)
        result = response.json()

        if result.get('status', {}).get('code') == 0:
            music = result['metadata']['music'][0]
            return {
                'title': music.get('title', 'Noma\'lum'),
                'artist': music['artists'][0]['name'] if music.get('artists') else 'Noma\'lum',
                'album': music.get('album', {}).get('name', ''),
                'source': 'ACRCloud'
            }
    except Exception as e:
        print(f"ACRCloud xato: {e}")
    return None

# ============================================================
# 🔍 YOUTUBE dan qo'shiq qidirish
# ============================================================
def youtube_search(query):
    try:
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': query,
            'type': 'video',
            'maxResults': 3,
            'key': YOUTUBE_API_KEY
        }
        response = requests.get(url, params=params)
        result = response.json()

        videos = []
        for item in result.get('items', []):
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            channel = item['snippet']['channelTitle']
            videos.append({
                'title': title,
                'channel': channel,
                'url': f"https://youtube.com/watch?v={video_id}"
            })
        return videos
    except Exception as e:
        print(f"YouTube xato: {e}")
    return []

# ============================================================
# 📥 Video/audio yuklab olish va audio ajratib olish
# ============================================================
def download_audio(url):
    filename = f"audio_{int(time.time())}"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filename,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return filename + ".mp3"
    except Exception as e:
        print(f"Yuklab olish xato: {e}")
    return None

# ============================================================
# 🤖 BOT KOMANDALAR
# ============================================================

@bot.message_handler(commands=['start'])
def start(message):
    text = (
        "🎵 *Musiqa Tanish Bot ga Xush Kelibsiz!*\n\n"
        "Men quyidagilarni qila olaman:\n\n"
        "🔗 *Video link* yuboring → musiqasini aniqlayman\n"
        "🎧 *Audio/video fayl* yuboring → musiqasini aniqlayman\n"
        "🔍 `/qidir qo'shiq nomi` → YouTube dan topaman\n\n"
        "Silk, TikTok, Instagram, YouTube linklar qabul qilinadi!\n\n"
        "Boshlash uchun link yoki fayl yuboring 👇"
    )
    bot.reply_to(message, text, parse_mode='Markdown')

@bot.message_handler(commands=['qidir'])
def qidir(message):
    query = message.text.replace('/qidir', '').strip()
    if not query:
        bot.reply_to(message, "❗ Qo'shiq nomini kiriting!\nMasalan: `/qidir Dildora Niyozova`", parse_mode='Markdown')
        return

    bot.reply_to(message, f"🔍 *{query}* qidirilmoqda...", parse_mode='Markdown')
    videos = youtube_search(query)

    if videos:
        text = f"🎵 *'{query}'* bo'yicha natijalar:\n\n"
        for i, v in enumerate(videos, 1):
            text += f"{i}. *{v['title']}*\n"
            text += f"   📺 {v['channel']}\n"
            text += f"   🔗 {v['url']}\n\n"
        bot.reply_to(message, text, parse_mode='Markdown')
    else:
        bot.reply_to(message, "😔 Hech narsa topilmadi. Boshqa nom bilan urinib ko'ring.")

# ============================================================
# 🔗 LINK yuborilganda
# ============================================================
@bot.message_handler(func=lambda m: m.text and any(
    site in m.text for site in ['silk.by', 'tiktok.com', 'instagram.com', 'youtube.com', 'youtu.be', 'vm.tiktok.com']
))
def handle_link(message):
    url = message.text.strip()
    msg = bot.reply_to(message, "⏳ Video yuklanmoqda va musiqa aniqlanmoqda...")

    audio_path = download_audio(url)
    if not audio_path or not os.path.exists(audio_path):
        bot.edit_message_text("❌ Video yuklab bo'lmadi. Link to'g'riligini tekshiring.", 
                               message.chat.id, msg.message_id)
        return

    bot.edit_message_text("🎵 Musiqa aniqlanmoqda...", message.chat.id, msg.message_id)

    # AudD bilan sinab ko'rish
    result = audd_recognize(audio_path)

    # Agar AudD topa olmasa, ACRCloud bilan sinash
    if not result:
        result = acrcloud_recognize(audio_path)

    os.remove(audio_path)

    if result:
        text = (
            f"✅ *Musiqa topildi!*\n\n"
            f"🎵 *Nomi:* {result['title']}\n"
            f"👤 *Ijrochi:* {result['artist']}\n"
            f"💿 *Album:* {result.get('album', 'Noma\'lum')}\n"
            f"🔍 *Manba:* {result['source']}\n\n"
            f"YouTube da qidirish uchun:\n"
            f"`/qidir {result['artist']} {result['title']}`"
        )
        bot.edit_message_text(text, message.chat.id, msg.message_id, parse_mode='Markdown')

        # YouTube dan avtomatik qidirish
        videos = youtube_search(f"{result['artist']} {result['title']}")
        if videos:
            yt_text = "🎬 *YouTube natijalar:*\n\n"
            for i, v in enumerate(videos[:2], 1):
                yt_text += f"{i}. [{v['title']}]({v['url']})\n"
            bot.send_message(message.chat.id, yt_text, parse_mode='Markdown')
    else:
        bot.edit_message_text(
            "😔 Musiqa aniqlanmadi.\n\nQo'shiq nomini bilsangiz:\n`/qidir qo'shiq nomi`",
            message.chat.id, msg.message_id, parse_mode='Markdown'
        )

# ============================================================
# 🎧 AUDIO/VIDEO FAYL yuborilganda
# ============================================================
@bot.message_handler(content_types=['audio', 'video', 'voice', 'document'])
def handle_file(message):
    msg = bot.reply_to(message, "⏳ Fayl qabul qilindi, musiqa aniqlanmoqda...")

    # Fayl turini aniqlash
    if message.audio:
        file_info = bot.get_file(message.audio.file_id)
    elif message.video:
        file_info = bot.get_file(message.video.file_id)
    elif message.voice:
        file_info = bot.get_file(message.voice.file_id)
    elif message.document:
        file_info = bot.get_file(message.document.file_id)
    else:
        bot.edit_message_text("❌ Fayl turi qo'llab-quvvatlanmaydi.", message.chat.id, msg.message_id)
        return

    # Faylni yuklab olish
    downloaded = bot.download_file(file_info.file_path)
    audio_path = f"temp_audio_{int(time.time())}.mp3"
    with open(audio_path, 'wb') as f:
        f.write(downloaded)

    # AudD bilan sinash
    result = audd_recognize(audio_path)

    # Agar AudD topa olmasa, ACRCloud bilan sinash
    if not result:
        result = acrcloud_recognize(audio_path)

    os.remove(audio_path)

    if result:
        text = (
            f"✅ *Musiqa topildi!*\n\n"
            f"🎵 *Nomi:* {result['title']}\n"
            f"👤 *Ijrochi:* {result['artist']}\n"
            f"💿 *Album:* {result.get('album', 'Noma\'lum')}\n"
            f"🔍 *Manba:* {result['source']}\n\n"
        )
        bot.edit_message_text(text, message.chat.id, msg.message_id, parse_mode='Markdown')

        # YouTube dan avtomatik qidirish
        videos = youtube_search(f"{result['artist']} {result['title']}")
        if videos:
            yt_text = "🎬 *YouTube natijalar:*\n\n"
            for i, v in enumerate(videos[:2], 1):
                yt_text += f"{i}. [{v['title']}]({v['url']})\n"
            bot.send_message(message.chat.id, yt_text, parse_mode='Markdown')
    else:
        bot.edit_message_text(
            "😔 Musiqa aniqlanmadi.\n\nQo'shiq nomini bilsangiz:\n`/qidir qo'shiq nomi`",
            message.chat.id, msg.message_id, parse_mode='Markdown'
        )

# ============================================================
# ▶️ BOTNI ISHGA TUSHIRISH
# ============================================================
print("🤖 Bot ishga tushdi!")
bot.infinity_polling()
