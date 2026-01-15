from requests import *
from config_data.config import Config, load_config


class RequestApi:
    @staticmethod
    def method_get(name_method_ha: str, params_request: dict = None):
        headers, url = RequestApi.constructor_header_url(name_method_ha)
        response = get(url, params=params_request, headers=headers)
        code = response.status_code
        return code, response

    @staticmethod
    def constructor_header_url(name_method_ha):
        config_app: Config = load_config()
        url = f"{config_app.ha.url}/api/{name_method_ha}"
        headers = {"Authorization": f"Bearer {config_app.ha.token}", "content-type": "application/json"}
        return headers, url

    @staticmethod
    def method_post(name_method_ha: str, json=None):
        headers, url = RequestApi.constructor_header_url(name_method_ha)
        response = post(url, headers=headers, json=json)
        code = response.status_code
        return code, response
