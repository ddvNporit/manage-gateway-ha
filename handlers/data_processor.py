class FiltersData:
    @staticmethod
    async def processing_filter(message, count_separators=2):
        text = message.text.strip()
        parts = text.split(maxsplit=4)
        field = parts[2] if len(parts) > 2 and count_separators >= 2 else None
        value = parts[3] if len(parts) > 3 and count_separators == 3 else None
        return field, value

    @staticmethod
    async def processing_short_filter(message, count_separators=2):
        text = message.strip()
        parts = text.split(maxsplit=4)
        field = parts[2] if len(parts) > 2 and count_separators >= 2 else None
        value = parts[3] if len(parts) > 3 and count_separators == 3 else None
        return field, value

    @staticmethod
    async def get_entity_id_and_attribute(data):
        entity_id = data.get('entity_id')
        attributes = data.get('attributes')
        return entity_id, attributes
