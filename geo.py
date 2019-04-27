import time
import requests
import json
import datetime


def get_city(req):
    # перебираем сущности

    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.GEO':
            # Если есть сущность с ключом 'first_name',
            # то возвращаем её значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('city', None)


def get_time(req):
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'
        if entity['type'] == 'YANDEX.NUMBER':
            return entity.get('value', None)


def get_weather_at_time(city_name, time, will=False):
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
    if will is False:
        return all_info['forecasts'][0]["hours"][time]["temp"], \
               all_info['forecasts'][0]["hours"][time]["condition"],\
               all_info['forecasts'][0]['hours'][time]['feels_like'],\
               all_info['forecasts'][0]['hours'][time]["wind_speed"], \
               all_info['forecasts'][0]['hours'][time]["wind_dir"]
    else:
        return all_info['forecasts'][1]["hours"][13]["temp"], \
               all_info['forecasts'][1]["hours"][13]["condition"],\
               all_info['forecasts'][1]['hours'][13]['feels_like'],\
               all_info['forecasts'][1]['hours'][13]["wind_speed"], \
               all_info['forecasts'][1]['hours'][13]["wind_dir"]


def get_weather(city_name, mass=False):
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
    if mass is False:
        return all_info['forecasts'][0]["hours"][int(t.split()[3].split(":")[0])]["temp"], \
               all_info['forecasts'][0]["hours"][int(t.split()[3].split(":")[0])]["condition"]
    else:
        return all_info['forecasts']


def get_day_weather(city_name, day=0):
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
    if day == 0:
        return all_info['forecasts'][0]["hours"][int(t.split()[3].split(":")[0])]["temp"], \
               all_info['forecasts'][0]["hours"][int(t.split()[3].split(":")[0])]["condition"], \
               all_info['forecasts'][0]["hours"][8]["temp"], \
               all_info['forecasts'][0]["hours"][13]["temp"], \
               all_info['forecasts'][0]["hours"][20]["temp"]
    else:
        now = all_info['forecasts'][0]["date"]
        now = [now[:4], now[5:7], now[8:]]
        posl = now.copy()

        if int(now[2]) > day:
            posl[2], posl[1] = str(day), posl[1][0] + str(int(posl[1][1]) + 1)
        elif int(now[2]) < day:
            posl[2] = str(day)
        else:
            return all_info['forecasts'][0]['parts']['day']["condition"], all_info['forecasts'][0]['date'][8:], \
                   all_info['forecasts'][0]['parts']['morning']["temp_max"], \
                   all_info['forecasts'][0]['parts']['day']["temp_max"], \
                   all_info['forecasts'][0]['parts']['night_short']["temp"]

        aa = datetime.date(int(now[0]), int(now[1]), int(now[2]))
        bb = datetime.date(int(posl[0]), int(posl[1]), int(posl[2]))
        cc = aa - bb
        den = abs(int(str(cc).split()[0]))
        if den > 7:
            return None, None, None, None, None
        else:

            return all_info['forecasts'][den]['parts']['day']["condition"], all_info['forecasts'][den]['date'][8:], \
                   all_info['forecasts'][den]['parts']['morning']["temp_max"], \
                   all_info['forecasts'][den]['parts']['day']["temp_max"], \
                   all_info['forecasts'][den]['parts']['night_short']["temp"]
