from typing import Any
import requests
from pprint import pprint
from config import API_TOKEN
import json


def get_params(sort_type: str, count: int) -> str | Any:
    """
    Функция принимает параметр отсеивания Страна и так же количество данных, возвращает словарь с API сервера
    """
    headers = {
        "X-API-KEY": API_TOKEN
    }
    url = "https://api.kinopoisk.dev/v1.4/movie"
    params = {
        "page": 1,
        "limit": count,
        "selectFields": ['name', 'rating', 'year', 'poster', 'genres', 'shortDescription', 'countries'],
        "rating.kp": "8-10",
        "notNullFields": ['name', 'type'],
    }

    if sort_type.lower() == 'low':
        params["year"] = "1970-1990"
    elif sort_type.lower() == 'high':
        params["year"] = "2019-2023"

    response = requests.get(url, params=params, headers=headers)

    if response.status_code != 200:
        return "Не удалось выполнить поиск"
    else:
        return json.loads(response.text)


def client_window(sort_type: str, count: int) -> str | list[Any]:
    """
    Основная функция, которая принимает от пользователя параметры и возвращает отсортированный список фильмов
    """
    try:
        params = get_params(sort_type, count)
        sorted_films = sorted(params['docs'], key=lambda x: x['year'])
        result_films = []

        for film in sorted_films:
            name = film['name']
            year = film['year']
            rating = film['rating']['kp']
            country = film['countries'][0]['name'] if 'countries' in film else ''
            genres = [i['name'] for i in film['genres']] if 'genres' in film else []
            image = film['poster']['previewUrl'] if 'poster' in film else ''
            formatted_string = "{} ({}) - Рейтинг: {}\nЖанры:\n{}\nСтрана: {}\n==={}===".format(
                name, year, rating, '\\ '.join(genres), country,
                film['shortDescription'])
            result_films.append((formatted_string, image))

        return result_films

    except ValueError:
        return []


pprint(client_window('low', 3))
