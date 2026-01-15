import os
import tempfile
import asyncio
from typing import List
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
    async def answer_base(bot, code: int, message, response):
        if int(code) == 200:
            text = response.text
            max_length = 4096

            if len(text) <= max_length:
                await bot.send_message(message.from_user.id, text)
            else:
                words = text.split(' ')
                parts = []
                current_part = []

                for word in words:
                    if len(' '.join(current_part + [word])) <= max_length:
                        current_part.append(word)
                    else:
                        parts.append(' '.join(current_part))
                        current_part = [word]

                if current_part:
                    parts.append(' '.join(current_part))

                for part in parts:
                    await bot.send_message(message.from_user.id, part)
                    await asyncio.sleep(0.3)
        else:
            await bot.send_message(message.from_user.id,
                                   f"Код ответа: {code}, проверьте работоспособность HA и корректность запроса")

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
