from aiogram import Bot, Dispatcher
import asyncio
from os import getenv
from dotenv import load_dotenv
from handlers.routes import router as main_router
from students.database import init_db

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

dp = Dispatcher()
dp.include_router(main_router)

async def main():
    await init_db()

    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())