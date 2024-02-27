from typing import Any
import requests
from pprint import pprint
from config import API_TOKEN
import json


def get_params(sort_type: str, count: int) -> str | Any:
    """
    Функция принимает параметр отсеивания Страна и так же количество данных, возвращает словарь с API сервера
    """
    global start_year, end_year
    headers = {
        "X-API-KEY": API_TOKEN
    }
    if sort_type.lower() == 'low':
        start_year = 1970
        end_year = 1990
    elif sort_type.lower() == 'high':
        start_year = 2019
        end_year = 2023
    response = requests.get(
        f"https://api.kinopoisk.dev/v1.4/movie?page=1&limit={count}&selectFields=name&selectFields"
        f"=rating&selectFields=year&selectFields=poster&rating.kp=8-10&selectFields=genres&selectFields"
        f"=&notNullFields=name&notNullFields=type&year={start_year}-{end_year}&selectFields=shortDescription&selectFields=countries",
        headers=headers)
    if response.status_code != 200:
        return "Не удалось выполнить поиск"
    else:
        return json.loads(response.text)


def client_window(sort_type: str, count: int) -> str | list[Any]:
    """
    Основная функция, которая принимает от пользователя параметры и возвращает отсортированный список фильмов
    """
    global genres, image, country
    try:
        params = get_params(sort_type, count)
        sorted_films = sorted(params['docs'], key=lambda x: x['year'])
        result_films = []
        for film in sorted_films:
            if 'countries' in film:
                country = film['countries'][0]['name']
            if 'genres' in film:
                genres = [i['name'] for i in film['genres']]
            if 'poster' in film:
                image = film['poster']['previewUrl']
            result_films.append(("{} ({}) - Рейтинг: {}\nЖанры:\n{}\nСтрана: {}\n==={}===".format(film['name'], film['year'],
                                                                                      film['rating']['kp'],
                                                                                      '\\ '.join(genres),country,
                                                                                      film['shortDescription']), image))
        return result_films

    except ValueError:
        return []


pprint(client_window('low', 3))
