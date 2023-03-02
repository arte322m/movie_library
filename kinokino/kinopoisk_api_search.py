import requests

URL_MOVIE = 'https://api.kinopoisk.dev/movie'
TOKEN = '3ZMWJDP-WZVM0V9-PQG4VX1-QTK87G4'
SECOND_TOKEN = 'AGPD8ND-8BH47X9-N1TJEAH-1PG18YP'


def search_film(params: list):
    params.append(('token', TOKEN))
    response = requests.get(URL_MOVIE, params=params, timeout=20)
    response_json = response.json()
    result = response_json['docs']
    return result


search_function = {'search_film': search_film}


def main():
    pass


if __name__ == '__main__':
    main()
