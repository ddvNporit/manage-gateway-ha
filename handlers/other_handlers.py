from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart, Text
from request_comand import RequestApi

router: Router = Router()


@router.message(CommandStart())
async def process_start_comand(message: Message):
    await message.answer("Hi")


@router.message(Text(text='Hi, Bot'))
async def hi(message: Message, bot: Bot):
    await (bot.send_message
           (message.from_user.id, f"hi, {message.from_user.full_name} ({message.from_user.id})"))


@router.message(Text(text='config HA'))
async def get_config_ha(message: Message, bot: Bot):
    req_ha = RequestApi()
    code, response = req_ha.method_get("config", None)
    await bot.send_message(message.from_user.id, f"ответ: {response.text}")
