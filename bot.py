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
    try:
        await dp.start_polling(bot)
    except asyncio.CancelledError:
        logger.info("Polling was cancelled")
    finally:
        # Корректное закрытие бота для освобождения ресурсов
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
