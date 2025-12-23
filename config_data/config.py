from __future__ import annotations

import ast
from dataclasses import dataclass
from environs import Env



@dataclass
class TgBot:
    token: str
    bot_allow_users: list


@dataclass
class HA:
    token: str
    url: str


@dataclass
class Config:
    tg_bot: TgBot
    ha: HA


def load_config(path: str | None = None) -> Config:
    env: Env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(
            token=env('BOT_TOKEN'),
            bot_allow_users=ast.literal_eval(env('BOT_ALLOW_USERS'))),
        ha=HA(
            token=env('HA_TOKEN'),
            url=env('HA_URL')
        )
    )
