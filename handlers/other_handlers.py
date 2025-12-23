from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart, Text
from request_comand import RequestApi
from config_data.config import Config, load_config

router: Router = Router()
config: Config = load_config()
bot_allow_users = config.tg_bot.bot_allow_users


async def check_access(message: Message) -> bool:
    if message.from_user.id not in bot_allow_users:
        await message.answer("Access denied")
        return False
    return True


@router.message(CommandStart())
async def process_start_comand(message: Message):
    if not await check_access(message):
        return
    await message.answer("Hi")


@router.message(Text(text='Hi, Bot'))
async def hi(message: Message, bot: Bot):
    if not await check_access(message):
        return
    await (bot.send_message
           (message.from_user.id, f"Hi, {message.from_user.full_name} ({message.from_user.id})"))


@router.message(Text(text='config HA'))
async def get_config_ha(message: Message, bot: Bot):
    if not await check_access(message):
        return
    req_ha = RequestApi()
    code, response = req_ha.method_get("config", None)
    await bot.send_message(message.from_user.id, f"ответ: {response.text}")
