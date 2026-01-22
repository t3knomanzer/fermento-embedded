import gc
import config
import urequests
from app.models.jar import JarModel

from app.services.network import NetworkService


def connect_wifi():
    try:
        net_service = NetworkService()
        net_service.connect()
    except OSError as e:
        print(f"Connection error: {e}")


def get_url(table):
    url = f"{config.BASE_URL}{config.BASE_ID}/{table}"
    return url


def get_headers():
    return {
        "Authorization": f"Bearer {config.AIRTABLE_TOKEN}",
        "Content-Type": "application/json",
    }


def create_jar(model):
    headers = get_headers()
    url = get_url(config.TABLE_JARS)
    data = {"fields": model.to_dict()}
    print(f"{url}")
    print(f"{data}")

    try:
        response = urequests.post(url, headers=headers, json=data)
        print(response.json())
    except OSError as e:
        print(f"Error: {e}")


gc.collect()
print(f"Free RAM {gc.mem_free() / 1000}Kb")
connect_wifi()
print(f"Free RAM {gc.mem_free() / 1000}Kb")
model = JarModel("myname", 123)
create_jar(model)
print(f"Free RAM {gc.mem_free() / 1000}Kb")
