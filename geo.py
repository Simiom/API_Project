import time
import requests
import json


def get_city(req):
    # перебираем сущности

    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.GEO':
            # Если есть сущность с ключом 'first_name',
            # то возвращаем её значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('city', None)


def get_weather(city_name):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

    geocoder_params = {"geocode": city_name, "format": "json"}

    response = requests.get(geocoder_api_server, params=geocoder_params)

    json_response = response.json()
    coordinates_str = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']

    long, lat = coordinates_str.split()

    url = 'https://api.weather.yandex.ru/v1/forecast?lat={}&lon={}&extra=false'.format(lat, long)
    headers = {'X-Yandex-API-Key': '7bbc89cc-fc42-46a2-b7c4-bb26f04b1e5b'}

    request = requests.get(url, headers=headers)

    all_info = json.loads(request.text)

    t = time.ctime(time.time() + (time.altzone + 3600) + int(all_info["info"]["tzinfo"]["offset"]))
    return all_info['forecasts'][1]["hours"][int(t.split()[3].split(":")[0])]["temp"], \
           all_info['forecasts'][1]["hours"][int(t.split()[3].split(":")[0])]["condition"]
