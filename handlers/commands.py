from request_comand import RequestApi


class CommandsOnHa:
    @staticmethod
    async def send_command_on_ha(path, payload):
        req_ha = RequestApi()
        code, response = req_ha.method_post(path, payload)
        return code, response
