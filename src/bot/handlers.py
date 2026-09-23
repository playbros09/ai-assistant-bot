from aiogram import F, Router
from aiogram.types import Message

from src.services.llm import ask_ai

router = Router()


# Ваш попередній обробник /start залишається тут...
@router.message(F.text == "/start")
async def cmd_start(message: Message) -> None:
    await message.answer("Привет! Я твой персональный AI-ассистент.")


# Новий обробник звичайних текстових повідомлень із пам'яттю сесії
@router.message(F.text)
async def handle_text(message: Message) -> None:
    # Показуємо статус "друкує...", щоб користувач бачив, що бот думає
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # Отримуємо відповідь від Gemini з урахуванням історії цього користувача
    reply = await ask_ai(message.from_user.id, message.text)

    await message.answer(reply)
