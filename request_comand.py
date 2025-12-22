from requests import *
from config_data.config import Config, load_config


class RequestApi:
    @staticmethod
    def method_get(name_method_ha: str, params_request: dict = None):
        config_app: Config = load_config()
        url = f"{config_app.ha.url}/api/{name_method_ha}"
        headers = {"Authorization": f"Bearer {config_app.ha.token}", "content-type": "application/json"}
        return get(url, params=params_request, headers=headers)


config: Config = load_config()
name_method = "config"
token = config.ha.token
params = {}
r_api = RequestApi()
response = r_api.method_get(name_method_ha=name_method, params_request=params)
print(response.text)
