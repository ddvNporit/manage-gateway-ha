import json
import logging
from dataclasses import dataclass
from pathlib import Path

from environs import Env

logger = logging.getLogger(__name__)


class MissingEnvVarsError(Exception):
    def __init__(self, missing_vars):
        message = f"Отсутствуют или пусты обязательные переменные окружения: {', '.join(missing_vars)}"
        super().__init__(message)


@dataclass
class TgBot:
    token: str
    bot_allow_users: list


@dataclass
class HA:
    token: str
    url: str


@dataclass
class Alias:
    aliases: list


@dataclass
class Config:
    tg_bot: TgBot
    ha: HA
    aliases: Alias


def check_required_env_vars(env: Env, keys: list[str]) -> dict[str, str]:
    missing_vars = []
    values = {}

    for key in keys:
        value = env.str(key, None)
        if not value:
            missing_vars.append(key)
        else:
            values[key] = value

    if missing_vars:
        raise MissingEnvVarsError(missing_vars)
    return values


def load_config(path: str | None = None) -> Config:
    env = Env()
    try:
        if path:
            env.read_env(path)
            logger.info(f".env загружен из файла: {path}")
        else:
            env.read_env()
            logger.info(".env файл загружен из текущего каталога")
    except FileNotFoundError:
        logger.warning(f".env файл не найден, продолжаем с переменными окружения")

    required_keys = ["BOT_TOKEN", "HA_TOKEN", "HA_URL", "CONFIG_FILE"]
    env_vars = check_required_env_vars(env, required_keys)

    json_path_obj = Path(env_vars["CONFIG_FILE"])

    if not json_path_obj.exists():
        logger.info(f"Конфигурационный JSON файл {json_path_obj} не найден, создается с дефолтным содержимым.")
        default_content = {
            "bot_allow_users": [],
            "aliases": []
        }
        json_path_obj.write_text(json.dumps(default_content, indent=2), encoding="utf-8")

    with open(json_path_obj, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    bot_allow_users = json_data.get("bot_allow_users") or []
    aliases = json_data.get("aliases") or []

    logger.info("Конфигурация успешно загружена")
    return Config(
        tg_bot=TgBot(
            token=env_vars["BOT_TOKEN"],
            bot_allow_users=bot_allow_users
        ),
        ha=HA(
            token=env_vars["HA_TOKEN"],
            url=env_vars["HA_URL"]
        ),
        aliases=Alias(
            aliases=aliases
        )
    )
