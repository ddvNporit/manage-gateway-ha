from datetime import datetime, timedelta

import tzlocal
from aiogram.types import Message


class FiltersData:
    @staticmethod
    async def processing_filter(message, count_separators=2):
        text = message.text.strip()
        parts = text.split(maxsplit=4)
        atr = parts[1] if len(parts) >= 2 and count_separators == 3 else None
        field = parts[2] if len(parts) > 2 and count_separators >= 2 else None
        value = parts[3] if len(parts) > 3 and count_separators == 3 else None

        return field, value, atr

    @staticmethod
    async def processing_short_filter(message, count_separators=2):
        text = message.strip()
        parts = text.split(maxsplit=4)
        atr = parts[1] if len(parts) > 2 and count_separators == 3 else None
        field = parts[2] if len(parts) > 2 and count_separators >= 2 else None
        value = parts[3] if len(parts) > 3 and count_separators == 3 else None
        return field, value, atr

    @staticmethod
    async def get_entity_id_and_attribute(data):
        entity_id = data.get('entity_id')
        attributes = data.get('attributes')
        return entity_id, attributes

    @staticmethod
    async def get_filter(message: Message, cmd: str = None, count_separators=2):
        if cmd is None:
            return await FiltersData.processing_filter(message, count_separators)
        else:
            return await FiltersData.processing_short_filter(cmd, count_separators)

    @staticmethod
    def validate_delta(value: str) -> bool:
        try:
            val = int(value)
            return 0 < val <= 7
        except (TypeError, ValueError):
            return False


class DateTimeProcessor:
    @staticmethod
    def get_date_minus_delta(delta: int) -> str:
        if not (1 <= delta <= 7):
            raise ValueError("delta должен быть в диапазоне от 1 до 7")
        local_tz = tzlocal.get_localzone()
        now = datetime.now(local_tz)
        target_date = now - timedelta(days=delta)
        return target_date.strftime("%Y-%m-%dT%H:%M:%S%z")[:-2] + ":" + target_date.strftime("%Y-%m-%dT%H:%M:%S%z")[-2:]
