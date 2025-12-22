from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart, Text

router: Router = Router()


@router.message(CommandStart())
async def process_start_comand(message: Message):
    await message.answer("Hi")


@router.message(Text(text='Hi, Bot'))
async def hi(message: Message, bot: Bot):
    await bot.send_message(message.from_user.id, "hi, user")
