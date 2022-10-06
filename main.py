import os
import pathlib
from random import randint

from environs import Env
import requests


def fetch_comics(comics_id):
    comics_url = f'https://xkcd.com/{comics_id}/info.0.json'
    response = requests.get(comics_url)
    response.raise_for_status()

    comics = response.json()
    img_url, message = comics['img'], comics['alt']

    response = requests.get(img_url)
    response.raise_for_status()

    img = response.content

    return img, message, f'{comics_id}{pathlib.Path(img_url).suffix}'


def fetch_upload_url(access_token):
    params = {'v': '5.131', 'access_token': access_token}
    response = requests.get('https://api.vk.com/method/photos.getWallUploadServer', params=params)
    response.raise_for_status()

    return response.json()['response']['upload_url']


def save_photo(img_filename, upload_url, access_token):
    params = {'v': '5.131', 'access_token': access_token}
    with open(img_filename, 'rb') as file:
        response = requests.post(upload_url, files={'photo': file})

    response.raise_for_status()
    response = requests.post('https://api.vk.com/method/photos.saveWallPhoto', params=params, data=response.json())
    response.raise_for_status()
    return response.json()['response'][0]


def post_comics_to_community(photo, community_id, message):
    params = {
        'v': '5.131',
        'access_token': access_token,
        'owner_id': -community_id,
        'from_group': 1,
        'attachments': f"photo{photo['owner_id']}_{photo['id']}",
        'message': message
    }
    response = requests.post('https://api.vk.com/method/wall.post', params=params)
    response.raise_for_status()


if __name__ == '__main__':
    env = Env()
    env.read_env()

    first_comics_id = 1
    last_comics_id = 2681
    comics_id = randint(first_comics_id, last_comics_id)
    community_id = env.int('VK_GROUP_ID')
    access_token = env.str('VK_ACCESS_TOKEN')
    comics_img, comics_message, img_filename = fetch_comics(comics_id)
    try:
        with open(img_filename, "wb") as file:
            file.write(comics_img)

        upload_url = fetch_upload_url(access_token)
        photo = save_photo(img_filename, upload_url, access_token)

        post_comics_to_community(photo, community_id, comics_message)
    finally:
        os.remove(img_filename)
