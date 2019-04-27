from flask import Flask, request
import logging
import json

from geo import get_weather, get_city, get_day_weather, get_time, get_weather_at_time

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

sessionStorage = {}
temp, vid = get_weather("Тюмень")
ask = {"weather": False, "translation": False}
vidipogod = {"clear": ["Ясно", "965417/d0e9e1d946e45a104d98"],
             "partly-cloudy": ["Малооблачно", "1521359/7f637007f0035c05bdd1"],
             "cloudy": ["Облачно с прояснениями", "1652229/2f3f2d4b994ffc06f5d6"],
             "overcast": ["Пасмурно", "1652229/a5b17a737d5bf01ce43f"],
             "partly-cloudy-and-light-rain": ["Небольшой дождь", "1521359/1572cc627ace32714613"],
             "partly-cloudy-and-rain": ["Дождь", "1652229/7c57d9b9cd81cd1adba5"],
             "overcast-and-rain": ["Сильный дождь", "965417/a657334d909ab9aa9a6a"],
             "overcast-thunderstorms-with-rain": ["Сильный дождь, гроза", "965417/83cdd18ca3d220268567"],
             "cloudy-and-light-rain": ["Небольшой дождь", "1521359/9ecc907528c4cd554d73"],
             "overcast-and-light-rain": ["Небольшой дождь", "1540737/d22b9bf38e9708d1279d"],
             "cloudy-and-rain": ["Дождь", "1030494/b38702a423ba3d9230bb"],
             "overcast-and-wet-snow": ["Дождь со снегом", "1521359/b18772365d37ff5cf90e"],
             "partly-cloudy-and-light-snow": ["Небольшой снег", "1540737/8febf9fa801778f15ab6"],
             "partly-cloudy-and-snow": ["Снег", "1030494/f8406f0ff9606ed6b3c8"],
             "overcast-and-snow": ["Снегопад", "1521359/e74a70d241b1eef50035"],
             "cloudy-and-light-snow": ["Небольшой снег", "1521359/5e4801926e7d06207de5"],
             "overcast-and-light-snow": ["Небольшой снег", "965417/6dc5e3365856b590c61c"],
             "cloudy-and-snow": ["Снег", "1030494/170de856713a3d189e60"]}
wind_dir = {"nw": "северо-западное", "n": "северное", "ne": "северо-восточное", "e": "восточное", "se": "юго-восточное",
            "s": "южное", "sw": "юго-западное", "w": "западное", "c": "штиль", }


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)

    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', request.json)

    return json.dumps(response)


def handle_dialog(req, res):
    user_id = req['session']['user_id']

    if req['session']['new']:
        # Это новый пользователь.
        # Инициализируем сессию и поприветствуем его.
        # Запишем подсказки, которые мы ему покажем в первый раз

        sessionStorage[user_id] = {
            'suggests': [
                "Да",
                "Нет"
            ]
        }
        # Заполняем текст ответа
        res['response']['text'] = 'Привет! Хочешь узнать погоду?'
        # Получим подсказки
        res['response']['buttons'] = get_suggests(user_id)
        return

    # Сюда дойдем только, если пользователь не новый,
    # и разговор с Алисой уже был начат
    # Обрабатываем ответ пользователя.
    # В req['request']['original_utterance'] лежит весь текст,
    # что нам прислал пользователь
    # Если он написал 'ладно', 'куплю', 'покупаю', 'хорошо',
    # то мы считаем, что пользователь согласился.
    # Подумайте, всё ли в этом фрагменте написано "красиво"?
    if req['request']['original_utterance'].lower() in ["да", "конечно", "ладно", "давай", "погода"] and ask[
        "weather"] is False:
        res['response']['text'] = 'Я вас слушаю.'
        ask["weather"] = True
        return
    elif req['request']['original_utterance'].lower() in ["нет"]:
        res['response']['text'] = 'Раз так, то я подожду, пока вы не напишите слово "Погода".'
        res['response']['buttons'] = [{'title': "Погода", 'hide': True}]
        ask["weather"] = False
        return

    if ask["weather"] is True:
        cit = get_city(req)

        if cit is None:
            res['response']['text'] = "Не расслышала(. Повтори пожалуйста."
            return
        else:
            if len(req['request']['original_utterance'].lower().split()) == 3:  # Запрос: Погода в <Город>
                temp, vid, mon, day, ivn = get_day_weather(cit)
                res['response']['text'] = "Погода сейчас"
                res['response']['card'] = {}
                res['response']['card']['type'] = 'BigImage'
                res['response']['card']['image_id'] = vidipogod[vid][1]
                res['response']['card']['title'] = '''Сейчас в {}: {}°'''.format(cit.title(), temp)
                res['response']['card']['description'] = "Утром: {}° | Днём: {}° | Вечером: {}°".format(mon, day, ivn)

                res['response']['end_session'] = True
                return
            elif len(req['request']['original_utterance'].lower().split()) == 5:
                time = get_time(req)
                if time is not None:
                    if req['request']['original_utterance'].lower().split()[-2] == "в" and time <= 23 and time >= 1:
                        temp, vid, feel, wind_s, wind_d = get_weather_at_time(cit, time)
                        res['response']['text'] = "Погода на время"
                        res['response']['card'] = {}
                        res['response']['card']['type'] = 'BigImage'
                        res['response']['card']['image_id'] = vidipogod[vid][1]
                        res['response']['card']['title'] = '''В {} в {}: {}°'''.format(cit.title(), time, temp)
                        res['response']['card'][
                            'description'] = ''' Ощущается: {}°| Ветер: {}° | Направление: {}°'''.format(feel, wind_s,
                                                                                                         wind_dir[
                                                                                                             wind_d])
                        res['response']['end_session'] = True
                        return

                    else:
                        res['response']['text'] = "Возможно запрос не верен. Пересмотрите его."
                        return

                elif req['request']['original_utterance'].lower().split()[-1] == "завтра":
                    temp, vid, feel, wind_s, wind_d = get_weather_at_time(cit, time, True)
                    res['response']['text'] = "Погода на время"
                    res['response']['card'] = {}
                    res['response']['card']['type'] = 'BigImage'
                    res['response']['card']['image_id'] = vidipogod[vid][1]
                    res['response']['card']['title'] = '''Завтра в {} {}°'''.format(cit.title(), temp)
                    res['response']['card'][
                        'description'] = ''' Ощущается: {}°| Ветер: {}° | Направление: {}°'''.format(feel, wind_s,
                                                                                                     wind_dir[wind_d])
                    res['response']['end_session'] = True
                    return
                else:
                    res['response']['text'] = "Возможно запрос не верен. Пересмотрите его."
                    return
            elif len(req['request']['original_utterance'].lower().split()) == 6:
                if req['request']['original_utterance'].lower().split()[-1] == "число":
                    time = get_time(req)

                    if time is not None and time <= 31 and time >= 1:

                        vid, chis, mon, day, ivn = get_day_weather(cit, time)
                        if vid is not None:
                            res['response']['text'] = "Погода на число"
                            res['response']['card'] = {}
                            res['response']['card']['type'] = 'BigImage'
                            res['response']['card']['image_id'] = vidipogod[vid][1]
                            res['response']['card']['title'] = '''Погода в {} на {} число'''.format(cit.title(),
                                                                                                    str(int(chis)))
                            res['response']['card']['description'] = "Утром: {}° | Днём: {}° | Ночь: {}°".format(mon,
                                                                                                                 day,
                                                                                                                 ivn)
                            res['response']['end_session'] = True
                            return
                        else:
                            res['response']['text'] = "Прогноз бпредоставляется на 7 дней с сегодняшнего дня."
                            return
                    else:
                        res['response']['text'] = "Возможно запрос не верен. Пересмотрите его."
                        return
                elif req['request']['original_utterance'].lower().split()[-1] in ["дней", "день", "дня"]:
                    try:
                        kol = int(req['request']['original_utterance'].lower().split()[-2])
                    except Exception:
                        res['response']['text'] = "Возможно запрос не верен. Пересмотрите его."
                        return
                    if kol <= 5 and kol >= 1:
                        pogoda = get_weather(cit, True)
                        res['response']['text'] = "период"
                        res['response']['card'] = {}
                        res['response']['card']['type'] = 'ItemsList'
                        res['response']['card']['header'] = {}
                        res['response']['card']['header']["text"] = "Погода на {} {}".format(str(kol), req['request'][
                            'original_utterance'].lower().split()[-1])
                        m = []
                        for i in range(kol):
                            m.append({})
                        res['response']['card']['items'] = m

                        for i in range(kol):
                            vid, chis, mon, day, ivn = pogoda[i]['parts']['day']["condition"], \
                                                       pogoda[i]['date'][8:], \
                                                       pogoda[i]['parts']['morning']["temp_max"], \
                                                       pogoda[i]['parts']['day']["temp_max"], \
                                                       pogoda[i]['parts']['night_short']["temp"]

                            res['response']['card']['items'][i]['image_id'] = vidipogod[vid][1]
                            res['response']['card']["items"][i]["title"] = "Погода на {} число".format(chis)
                            res['response']['card']["items"][i][
                                "description"] = "Утром: {}° | Днём: {}° | Ночь: {}°".format(mon, day,
                                                                                             ivn)
                        res['response']['end_session'] = True
                        return
                else:
                    res['response']['text'] = "Возможно запрос не верен. Пересмотрите его."
                    return
            else:
                res['response']['text'] = "Возможно запрос не верен. Пересмотрите его."
                return
    else:
        res['response']['text'] = "Не расслышала(. Повтори пожалуйста."
        res['response']['buttons'] = [{'title': "Погода", 'hide': True}]

        return


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    return suggests


if __name__ == '__main__':
    app.run()
