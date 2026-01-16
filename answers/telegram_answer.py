import asyncio
import json
import os
import tempfile

from aiogram.types import FSInputFile


class TgAnswers:
    @staticmethod
    async def answer_command_turn(bot, code, field, message, value):
        if int(code) == 200:
            await bot.send_message(message.from_user.id, f"Объект {field} переведен в режим {value}")
        else:
            await bot.send_message(message.from_user.id,
                                   f"код ответа: {code}, проверьте работоспособность HA, и корректность запроса")

    @staticmethod
    async def answer_base(bot, code: int, message, response, formate_html=None):
        delta = 13 if formate_html else 0  # 13 символов для тегов <code> и </code>
        if int(code) == 200:
            text = await TgAnswers.format_input_text(response)
            max_length = 4096 - delta if formate_html else 4096
            if len(text) <= max_length:
                if formate_html:
                    await bot.send_message(
                        message.from_user.id,
                        f"<code>{text}</code>",
                        parse_mode='HTML'
                    )
                else:
                    await bot.send_message(message.from_user.id, text)
            else:
                if formate_html:
                    parts = [text[i:i + max_length] for i in range(0, len(text), max_length)]
                    for part in parts:
                        await bot.send_message(
                            message.from_user.id,
                            f"<code>{part}</code>",
                            parse_mode='HTML'
                        )
                        await asyncio.sleep(0.3)
                else:
                    parts = [text[i:i + max_length] for i in range(0, len(text), max_length)]
                    for part in parts:
                        await bot.send_message(message.from_user.id, part)
                        await asyncio.sleep(0.3)
        else:
            error_msg = f"Код ответа: {code}, проверьте работоспособность HA и корректность запроса"
            await bot.send_message(message.from_user.id, error_msg)

    @staticmethod
    async def answer_send_image(bot, code, message, response):
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

    @staticmethod
    async def format_input_text(response):
        if isinstance(response, list):
            text = json.dumps(response, indent=2, ensure_ascii=False)
        else:
            if hasattr(response, 'text'):
                reply = response.json()
                text = json.dumps(reply, indent=2, ensure_ascii=False)
            else:
                text = "Недопустимый формат ответа HA"
        return text
