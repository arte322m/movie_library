import requests

URL_SHIKIMORI_SEARCH = 'https://shikimori.me/api/animes/'

USER_AGENT = 'test_api_shik'
HEADER = {
    'User-Agent': USER_AGENT
}


def search_anime_series(anime_id):
    anime_url = f"{URL_SHIKIMORI_SEARCH}{anime_id}"
    response = requests.get(
        url=anime_url,
        headers=HEADER
    )
    if not response.ok:
        return 'всё плохо(((('
    response_json = response.json()

    return response_json


def search_anime(search_text: str):
    params = {
        'limit': 10,
        'search': f"{search_text}",
    }
    response = requests.get(
        url=URL_SHIKIMORI_SEARCH,
        params=params,
        headers=HEADER
    )
    if not response.ok:
        return 'всё плохо(((('
    response_json = response.json()

    return response_json


if __name__ == '__main__':
    text = input()
    print(search_anime(text))
