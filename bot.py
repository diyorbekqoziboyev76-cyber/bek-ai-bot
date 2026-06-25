import asyncio
import aiohttp
import urllib.parse
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile

BOT_TOKEN = "8744804638:AAFfB_3UsZE6-9PbNc0Sf7CZrbhzPc4yDbA"
GEMINI_API_KEY = "AQ.Ab8RN6ICRaJYLgHmfj7RDyJ1jFFCf1f6KH3olzt_Mg66Jwo9MA"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def gemini_chat(text):
    payload = {"contents": [{"parts": [{"text": "Sen Bek_AI - aqlli yordamchi. Foydalanuvchi tilida javob ber.\n\n" + text}]}]}
    async with aiohttp.ClientSession() as s:
        async with s.post(GEMINI_URL, json=payload) as r:
            d = await r.json()
            return d["candidates"][0]["content"]["parts"][0]["text"]

@dp.message(Command("start"))
async def start(m: Message):
    await m.answer("👑 Salom! Men Bek_AI!\n\n🗣 Suhbat - istalgan savol\n🖼 /rasm [tavsif]\n🎵 /musiqa [tavsif]")

@dp.message(Command("rasm"))
async def rasm(m: Message):
    p = m.text.replace("/rasm","").strip()
    if not p:
        await m.answer("Masalan: /rasm tog manzarasi")
        return
    await m.answer("🎨 Yaratilmoqda...")
    url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(p)
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            img = BufferedInputFile(await r.read(), "img.jpg")
            await m.answer_photo(img, caption=p)

@dp.message(Command("musiqa"))
async def musiqa(m: Message):
    p = m.text.replace("/musiqa","").strip()
    if not p:
        await m.answer("Masalan: /musiqa lo-fi relaxing")
        return
    await m.answer("🎵 Yaratilmoqda...")
    url = "https://audio.pollinations.ai/" + urllib.parse.quote(p)
    async with aiohttp.ClientSession() as s:
        async with s.get(url, timeout=aiohttp.ClientTimeout(total=120)) as r:
            audio = BufferedInputFile(await r.read(), "music.mp3")
            await m.answer_audio(audio, caption=p)

@dp.message()
async def chat(m: Message):
    if m.text:
        await bot.send_chat_action(m.chat.id, "typing")
        await m.answer(await gemini_chat(m.text))

async def main():
    await dp.start_polling(bot)

asyncio.run(main())
