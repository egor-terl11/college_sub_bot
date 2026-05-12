from aiogram import Dispatcher, Bot, Router
import asyncio
from os import getenv
from dotenv import load_dotenv

from flask import Flask
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return "Я жив!"

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()
router = Router()
dp.include_router(router)

async def main():
    await init_db()
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5000, debug=False)).start()
    asyncio.run(main())
