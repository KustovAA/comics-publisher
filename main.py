import os
from random import randint

from environs import Env
import requests


def fetch_image(url, filename, params):
    headers = {
        "User-Agent": "CoolBot/0.0 (https://example.org/coolbot/; coolbot@example.org)"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    with open(filename, "wb") as file:
        file.write(response.content)


def post_comics_to_community(comics_id, community_id, access_token):
    comics_url = f'https://xkcd.com/{comics_id}/info.0.json'
    response = requests.get(comics_url)
    response.raise_for_status()

    comics = response.json()

    img_filename = f'{comics_id}.png'
    fetch_image(comics['img'], img_filename, {})
    alt = comics['alt']
    params = {'v': '5.131', 'access_token': access_token}
    response = requests.get('https://api.vk.com/method/photos.getWallUploadServer', params=params)
    response.raise_for_status()

    response = response.json()['response']

    with open(img_filename, 'rb') as file:
        url = response['upload_url']
        files = {'photo': file}
        response = requests.post(url, files=files)

    response.raise_for_status()
    response = requests.post('https://api.vk.com/method/photos.saveWallPhoto', params=params, data=response.json())
    response.raise_for_status()
    photos = response.json()['response']

    for photo in photos:
        try:
            params = {
                'v': '5.131',
                'access_token': access_token,
                'owner_id': -community_id,
                'from_group': 1,
                'attachments': f"photo{photo['owner_id']}_{photo['id']}",
                'message': alt
            }
            response = requests.post('https://api.vk.com/method/wall.post', params=params)
            response.raise_for_status()
        finally:
            os.remove(img_filename)


if __name__ == '__main__':
    env = Env()
    env.read_env()

    comics_id = randint(1, 600)
    community_id = env.int('VK_GROUP_ID')
    access_token = env.str('VK_ACCESS_TOKEN')
    post_comics_to_community(comics_id, community_id, access_token)
