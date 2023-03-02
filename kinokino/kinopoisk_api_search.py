import requests

URL_MOVIE = 'https://api.kinopoisk.dev/movie'
TOKEN = '3ZMWJDP-WZVM0V9-PQG4VX1-QTK87G4'
SECOND_TOKEN = 'AGPD8ND-8BH47X9-N1TJEAH-1PG18YP'


def search_film(params: list):
    params.append(('token', TOKEN))
    result = {'films': []}
    response = requests.get(URL_MOVIE, params=params)
    response_json = response.json()
    for film_info in response_json['docs']:
        name = film_info['name']
        poster = film_info['poster']['previewUrl']
        result['films'].append({name: poster})
    return result


search_function = {'search_film': search_film}


def main():
    pass
    # params = {
    #     'field': 'name',
    #     'search': 'одни из нас',
    #     'token': TOKEN,
    # }
    # search_film(params)


if __name__ == '__main__':
    main()
