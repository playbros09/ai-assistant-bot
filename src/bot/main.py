import asyncio
import logging

from aiogram import Bot, Dispatcher
from src.middlewares.rate_limit import RateLimitMiddleware

from src.bot.config import settings
from src.bot.handlers import router

# Налаштування читаємого формату логів
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

dp = Dispatcher()
dp.include_router(router)
# Подключаем к диспетчеру сообщений
dp.message.middleware(RateLimitMiddleware())


async def main() -> None:
    bot = Bot(token=settings.bot_token)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
