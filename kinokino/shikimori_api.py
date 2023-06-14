import requests

URL_SHIKIMORI_SEARCH = 'https://shikimori.me/api/animes'

USER_AGENT = 'test_api_shik'
# AUTHORIZATION =


def search_anime(name: str):
    header = {
        'User-Agent': USER_AGENT
    }
    params = {
        'limit': 10,
        'search': name,
    }
    response = requests.get(
        url=URL_SHIKIMORI_SEARCH,
        header=header,
        params=params,
    )
    pass
