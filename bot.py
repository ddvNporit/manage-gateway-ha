import asyncio
import logging
from handlers import other_handlers
from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format='%(filename)s:%(lineno)d #%(levelname) -8s '
                               '[%(asctime)s] -%(name)s -%(message)s'
                        )
    logger.info('start application')
    config: Config = load_config()
    bot: Bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp: Dispatcher = Dispatcher()

    # Регистрируем роутеры
    dp.include_router(other_handlers.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

# Включаем логирование, чтобы не пропустить важные сообщения
# logging.basicConfig(level=logging.INFO)
# # Создаём объекты бота и диспетчера
# bot = Bot(token=BOT_TOKEN)
# dp = Dispatcher()
#
#
# # Обработчик команды /start
# @dp.message(CommandStart())
# async def command_start_handler(message: types.Message) -> None:
#     await message.answer(f"Привет, {message.from_user.full_name}!")
#
#
# # Обработчик текстовых сообщений (эхо)
# @dp.message()
# async def echo_handler(message: types.Message):
#     await message.answer(message.text)
