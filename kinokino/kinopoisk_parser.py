import requests

URL_MOVIE = 'https://api.kinopoisk.dev/v1/movie'
URL_SEASON = 'https://api.kinopoisk.dev/v1/season'
TOKEN = '3ZMWJDP-WZVM0V9-PQG4VX1-QTK87G4'
SECOND_TOKEN = 'AGPD8ND-8BH47X9-N1TJEAH-1PG18YP'


def search_series(params: list):
    params.append(('selectFields', 'movieId number episodesCount episodes'))
    params.append(('token', TOKEN))
    response = requests.get(URL_SEASON, params=params, timeout=20)
    if response.status_code == 403:
        params = params[:-1]
        params.append(('token', SECOND_TOKEN))
        response = requests.get(URL_SEASON, params=params, timeout=20)
        if not response.ok:
            return 'всё плохо(((('
        response_json = response.json()
        result = response_json['docs']
        if len(result) > 1:
            episodes = result[-1]['episodes'][0]
            if not episodes['enName'] and not episodes['name'] and not episodes['date']:
                result = result[:-1]
        return result
    elif not response.ok:
        return 'всё плохо(((('
    response_json = response.json()
    result = response_json['docs']
    if len(result) > 1:
        episodes = result[-1]['episodes'][0]
        if not episodes['enName'] and not episodes['name'] and not episodes['date']:
            result = result[:-1]
    return result


def search_series_by_id(kin_id: int):
    return search_series([
        ('movieId', kin_id)
    ])


def search_film(params: list):
    params.append(('selectFields', 'id type name year releaseYears poster.previewUrl'))
    params.append(('limit', 9))
    params.append(('token', TOKEN))
    response = requests.get(URL_MOVIE, params=params, timeout=20)
    if response.status_code == 403:
        params = params[:-1]
        params.append(('token', SECOND_TOKEN))
        response = requests.get(URL_MOVIE, params=params, timeout=20)
        if not response.ok:
            return 'всё плохо(((('
        response_json = response.json()
        result = response_json['docs']
        return result
    elif not response.ok:
        return 'всё плохо(((('
    response_json = response.json()
    result = response_json['docs']
    return result


def search_film_by_name(film: str):
    return search_film([
            ('name', film)
        ])


search_function = {
    'search_film': search_film,
    'search_series': search_series,
    'search_film_by_name': search_film_by_name,
   }


def main():
    pass


if __name__ == '__main__':
    main()
