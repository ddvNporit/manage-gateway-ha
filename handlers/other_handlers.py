import asyncio
import os
import tempfile

from aiogram import Bot
from aiogram.dispatcher.router import Router
from aiogram.filters import CommandStart, Text
from aiogram.types import Message, FSInputFile

from config_data.config import Config, load_config
from handlers.commands import CommandsOnHa as Com_Ha
from handlers.data_processor import FiltersData as Fp
from request_comand import RequestApi

router: Router = Router()
config: Config = load_config()
bot_allow_users = config.tg_bot.bot_allow_users
aliases = config.aliases.aliases


async def check_access(message: Message) -> bool:
    if message.from_user.id not in bot_allow_users:
        await message.answer("Access denied")
        return False
    return True


registered_commands = set()

registered_commands.update(["<code>HELP</code> - вывод всех доступных команд"])


@router.message(lambda message: message.text.lower().startswith("help"))
async def help_handler(message: Message):
    if not registered_commands:
        await message.answer("Команды не найдены.")
        return
    help_text = "Доступные команды:\n" + "\n".join(f"• {cmd}" for cmd in sorted(registered_commands))
    await message.answer(help_text)


registered_commands.update(["<code>restart HA</code> - перезапуск Home Assistant"])


@router.message(lambda message: message.text.lower().startswith("restart ha"))
async def restart_ha_handler(message: Message, bot: Bot):
    if not await check_access(message):
        return
    req_ha = RequestApi()
    code, response = req_ha.method_post("services/homeassistant/restart", None)
    await bot.send_message(message.from_user.id, f"ответ: {response.text}")


registered_commands.update(["<code>start</code> - старт работы с телеграм ботом"])


@router.message(CommandStart())
async def process_start_comand(message: Message):
    await message.answer("Hi")


registered_commands.update(["<code>Hi, Bot</code> - получить свои full_name и user_id"])


@router.message(Text(text='Hi, Bot'))
async def hi(message: Message, bot: Bot):
    await (bot.send_message
           (message.from_user.id, f"Hi, {message.from_user.full_name} ({message.from_user.id})"))


registered_commands.update(["<code>config HA</code> - получить конфиг HA"])


@router.message(Text(text='config HA'))
async def get_config_ha(message: Message, bot: Bot):
    if not await check_access(message):
        return
    req_ha = RequestApi()
    code, response = req_ha.method_get("config", None)
    await bot.send_message(message.from_user.id, f"ответ: {response.text}")


registered_commands.update(["<code>states HA</code> - получить спискок всех объектов"])


@router.message(lambda message: message.text.lower().startswith("states ha"))
async def get_states_ha(message: Message, bot: Bot):
    if not await check_access(message):
        return

    filter_value, value = await Fp.processing_filter(message)

    req_ha = RequestApi()
    code, response = req_ha.method_get("states", None)
    if int(code) != 200:
        await bot.send_message(message.from_user.id,
                               f"код ответа: {code}, проверьте работоспособность HA, и корректность запроса")
        return

    reply = response.json()
    if filter_value is None:
        filtered_elements = reply
    else:
        try:
            count = int(filter_value)
            if count <= 0:
                await bot.send_message(message.from_user.id,
                                       "Количество элементов должно быть положительным числом.")
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


registered_commands.update(["<code>update:bool states</code> - обновить статус объекта"])


@router.message(lambda message: message.text.lower().startswith("update:bool states"))
async def updated_states_ha(message: Message, bot: Bot):
    if not await check_access(message):
        return
    field, value = await Fp.processing_filter(message, 3)
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
        entity_id, attributes = await Fp.get_entity_id_and_attribute(response.json())
    else:
        await bot.send_message(message.from_user.id,
                               f"код ответа: {code}, проверьте работоспособность HA, и корректность запроса")
        return
    payload = {
        "state": value,
        "attributes": attributes
    }
    path = f"states/{field}"
    code, response = await Com_Ha.send_command_on_ha(path, payload)
    await answer_updated_states(bot, code, message, response)
    if code != 200:
        return


registered_commands.update(["<code>turn ha entity_id X</code> - вкл/выкл объекта entity_id, где X равно 1 или 0"])


@router.message(lambda message: message.text.lower().startswith("turn ha"))
async def turn_ha_object(message: Message, bot: Bot, cmd: str = None):
    if not await check_access(message):
        return
    if cmd is None:
        field, value = await Fp.processing_filter(message, 3)
    else:
        field, value = await Fp.processing_short_filter(cmd, 3)
    if value in ('1', 'on', 'вкл'):
        value = 'on'
    elif value in ('0', 'off', 'выкл'):
        value = 'off'
    else:
        await bot.send_message(message.from_user.id,
                               f"неизвестный аргумент: {value}, допустимо: [0, 1, вкл, выкл, on, off]")
        return
    payload = {
        "entity_id": field
    }
    parts = field.split('.')
    path = f"services/{parts[0]}/turn_{value}"
    code, response = await Com_Ha.send_command_on_ha(path, payload)

    await answer_command_turn(bot, code, field, message, value)
    if code != 200:
        return


registered_commands.update(["<code>ALIAS</code> - вывод всех ВАШИХ КОМАНД, зарегистрированных в конфиге"])


@router.message(lambda message: message.text.lower().startswith("alias"))
async def alias_list_handler(message: Message):
    # keys = [list(d.keys())[0] for d in aliases]
    response_lines = []
    for d in aliases:
        key = list(d.keys())[0]
        cmd = d[key]
        response_lines.append(f"<code>{key}</code> → {cmd}")
    response = "Список псевдонимов:\n" + "\n".join(response_lines)
    await message.answer(response)


registered_commands.update(
    [
        "<code>camera HA entity_id</code> - получить фото с камеры с идентификатором entity_id"
    ])


@router.message(lambda message: message.text.lower().startswith("camera ha"))
async def get_security_camera_image(message: Message, bot: Bot):
    if not await check_access(message):
        return
    filter_value, value = await Fp.processing_filter(message)
    if filter_value is not None:
        req_ha = RequestApi()
        code, response = req_ha.method_get(f"camera_proxy/camera.{filter_value}", None)

        if code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                tmp_file.write(response.content)
                tmp_file_path = tmp_file.name

            try:
                input_file = FSInputFile(tmp_file_path, filename="camera.jpg")
                await bot.send_photo(message.from_user.id, photo=input_file)
            finally:
                os.remove(tmp_file_path)
        else:
            await bot.send_message(message.from_user.id,
                                   f"код ответа: {code}, проверьте работоспособность HA, и корректность запроса")
            return
    else:
        await bot.send_message(message.from_user.id,
                               f"Запрос отклонен. Пустое значение идентификатора камеры")


registered_commands.update(
    [
        "<code>ВАША КОМАНДА</code> - вкл/выкл объекта c помощью псевдонимов. ВАША КОМАНДА регистрируется в конфиге"
    ])


@router.message()
async def process_alias(message: Message, bot: Bot):
    keys = [list(d.keys())[0] for d in aliases]

    if message.text.strip() in keys:
        cmd = next(d[message.text] for d in aliases if message.text in d)
        await bot.send_message(message.from_user.id, f"Выполняется команда: {cmd}")
        await turn_ha_object(message, bot, cmd)

    else:
        if not await check_access(message):
            return
        await bot.send_message(message.from_user.id,
                               "Команда не известна, используйте <code>HELP</code> для получения списка команд")


async def answer_command_turn(bot, code, field, message, value):
    if int(code) == 200:
        await bot.send_message(message.from_user.id, f"Объект {field} переведен в режим {value}")
    else:
        await bot.send_message(message.from_user.id,
                               f"код ответа: {code}, проверьте работоспособность HA, и корректность запроса")


async def answer_updated_states(bot, code, message, response):
    if int(code) == 200:
        await bot.send_message(message.from_user.id, response.text)
    else:
        await bot.send_message(message.from_user.id,
                               f"код ответа: {code}, проверьте работоспособность HA, и корректность запроса")
