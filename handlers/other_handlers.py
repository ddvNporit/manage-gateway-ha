from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import CommandStart, Text
from request_comand import RequestApi
from config_data.config import Config, load_config
import asyncio

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


@router.message(lambda message: message.text.lower().startswith("states ha"))
async def get_states_ha(message: Message, bot: Bot):
    if not await check_access(message):
        return

    filter_value, value = await processing_filter(message)

    req_ha = RequestApi()
    code, response = req_ha.method_get("states", None)
    if int(code) != 200:
        await bot.send_message(message.from_user.id,
                               f"код ответа: {code}, проверьте работоспособность HA, и корректность запроса")
        return

    reply = response.json()
    # filtered_elements = []
    if filter_value is None:
        filtered_elements = reply
    else:
        try:
            count = int(filter_value)
            if count <= 0:
                await bot.send_message(message.from_user.id, "Количество элементов должно быть положительным числом.")
                return
            filtered_elements = reply[:count]
        except ValueError:
            filtered_elements = [el for el in reply if filter_value in el.get('entity_id', '')]
    if not filtered_elements:
        await bot.send_message(message.from_user.id, "По заданному критерию ничего не найдено.")
        return

    messages = []
    current_msg = ""
    for i, el in enumerate(filtered_elements):
        line = f"element #{i}: {el}\n"
        if len(current_msg) + len(line) > 4096:
            messages.append(current_msg)
            current_msg = line
        else:
            current_msg += line
    if current_msg:
        messages.append(current_msg)

    for msg in messages:
        await bot.send_message(message.from_user.id, msg)
        await asyncio.sleep(0.3)


async def processing_filter(message, count_separators=2):
    text = message.text.strip()
    parts = text.split(maxsplit=4)
    # field = None
    value = None
    field = parts[2] if (len(parts) > 2 and count_separators == 2) else None
    if count_separators == 3:
        try:
            field = parts[2]
        except:
            field = None
        try:
            value = parts[3]
        except:
            value = None
    return field, value


async def get_entity_id_and_attribute(data):
    entity_id = data.get('entity_id')
    attributes = data.get('attributes')
    return entity_id, attributes


@router.message(lambda message: message.text.lower().startswith("update:bool states"))
async def updated_states_ha(message: Message, bot: Bot):
    if not await check_access(message):
        return
    field, value = await processing_filter(message, 3)
    if value in ('1', 'on', 'вкл'):
        value = 'on'
    elif value in ('0', 'off', 'выкл'):
        value = 'off'
    else:
        await bot.send_message(message.from_user.id,
                               f"неизвестный аргумент: {value}, допустимо: [0, 1, вкл, выкл, on, off]")
        return
    req_ha = RequestApi()
    code, response = req_ha.method_get(f"states/{field}", None)
    if int(code) == 200:
        entity_id, attributes = await get_entity_id_and_attribute(response.json())
    else:
        await bot.send_message(message.from_user.id,
                               f"код ответа: {code}, проверьте работоспособность HA, и корректность запроса")
        return
    payload = {
        "state": value,
        "attributes": attributes
    }
    code, response = req_ha.method_post(f"states/{field}", payload)
    if int(code) == 200:
        await bot.send_message(message.from_user.id, response.text)
    else:
        await bot.send_message(message.from_user.id,
                               f"код ответа: {code}, проверьте работоспособность HA, и корректность запроса")
        return


@router.message(lambda message: message.text.lower().startswith("turn ha"))
async def turn_ha_object(message: Message, bot: Bot):
    if not await check_access(message):
        return
    field, value = await processing_filter(message, 3)
    if value in ('1', 'on', 'вкл'):
        value = 'on'
    elif value in ('0', 'off', 'выкл'):
        value = 'off'
    else:
        await bot.send_message(message.from_user.id,
                               f"неизвестный аргумент: {value}, допустимо: [0, 1, вкл, выкл, on, off]")
        return
    req_ha = RequestApi()
    payload = {
        "entity_id": field
    }
    parts = field.split('.')
    code, response = req_ha.method_post(f"services/{parts[0]}/turn_{value}", payload)
    if int(code) == 200:
        await bot.send_message(message.from_user.id, f"Объект {field} переведен в режим {value}")
    else:
        await bot.send_message(message.from_user.id,
                               f"код ответа: {code}, проверьте работоспособность HA, и корректность запроса")
        return
