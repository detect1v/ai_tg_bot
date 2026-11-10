import os
import asyncio
import aiohttp
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

# Завантаження змінних оточення
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

PRIMARY_MODEL = "gemini-3.5-flash"
FALLBACK_MODELS = ["gemini-3.1-flash-lite", "gemini-3.6-flash"]

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Створення меню
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Студент"), KeyboardButton(text="IT-технології")],
        [KeyboardButton(text="Контакти"), KeyboardButton(text="Prompt AI")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Вітаю! Оберіть опцію з меню:", reply_markup=menu_keyboard)

@dp.message(F.text == "Студент")
async def handle_student(message: types.Message):
    text = "Студент: Боднарчук Андрій\nГрупа: ІА-31\nВаріант: 2"
    await message.answer(text)

@dp.message(F.text == "IT-технології")
async def handle_tech(message: types.Message):
    text = (
        "Мій стек технологій (AI/ML Engineer):\n"
        "- Python, SQL\n"
        "- PyTorch, TensorFlow, OpenCV\n"
        "- Ultralytics YOLO, MediaPipe, Diffusers\n"
        "- HuggingFace Transformers, CUDA\n"
        "- Docker, Docker Compose, AWS EC2, Vagrant\n"
        "- Базово ознайомлений: C#, .NET"
    )
    await message.answer(text)

@dp.message(F.text == "Контакти")
async def handle_contacts(message: types.Message):
    text = "Контакти:\nEmail: andrii.bodnarchuk.work@gmail.com\nTelegram: @bodnarchuk_andrii"
    await message.answer(text)

@dp.message(F.text == "Prompt AI")
async def handle_prompt_ai(message: types.Message):
    await message.answer("Напишіть ваше запитання до штучного інтелекту:")

@dp.message()
async def handle_ai_request(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    models = [PRIMARY_MODEL] + FALLBACK_MODELS
    payload = {"contents": [{"parts": [{"text": message.text}]}]}
    
    async with aiohttp.ClientSession() as session:
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
            try:
                async with session.post(url, json=payload, timeout=15) as response:
                    result = await response.json()
                    if response.status == 200:
                        ai_text = result['candidates'][0]['content']['parts'][0]['text']
                        await message.answer(ai_text)
                        return
                    elif response.status == 503:
                        continue
            except Exception:
                continue

    await message.answer("Вибачте, сервіс AI зараз перевантажений. Спробуйте ще раз через пару секунд.")

# Хендлер для перевірки стану Render (Health Check)
async def handle_health_check(request):
    return web.Response(text="OK")

async def main():
    print("Бот запущений...")

    # Старт фонового веб-сервера для Render
    app = web.Application()
    app.router.add_get("/", handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    # Старт поллінгу Telegram-бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
