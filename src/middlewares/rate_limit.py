import time

from aiogram import BaseMiddleware


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit_seconds: float = 2.0):
        self.limit_seconds = limit_seconds
        self.last_call: dict[int, float] = {}

    async def __call__(self, handler, event, data):
        user_id = event.from_user.id
        now = time.monotonic()
        if now - self.last_call.get(user_id, 0) < self.limit_seconds:
            await event.answer("Слишком быстро, подожди секунду.")
            return
        self.last_call[user_id] = now
        return await handler(event, data)
