import asyncio
import os
import threading

from aiogram import Bot, Dispatcher
from flask import Flask
from dotenv import load_dotenv

from handlers.routes import router as main_router
from students.database import init_db

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

app = Flask(__name__)

@app.route('/')
def home():
    return "Я жив!"

def run_flask():
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

dp = Dispatcher()
dp.include_router(main_router)

async def main():
    await init_db()
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    asyncio.run(main())
