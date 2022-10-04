import os
from random import randint

from environs import Env
import requests


def fetch_image(url):
    response = requests.get(url)
    response.raise_for_status()

    return response.content


def fetch_comics(comics_id):
    comics_url = f'https://xkcd.com/{comics_id}/info.0.json'
    response = requests.get(comics_url)
    response.raise_for_status()

    return response.json()


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
    return response.json()['response']

def upload_photos(photos, community_id, message):
    for photo in photos:
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

    comics_id = randint(1, 600)
    community_id = env.int('VK_GROUP_ID')
    access_token = env.str('VK_ACCESS_TOKEN')
    comics = fetch_comics(comics_id)
    comics_img_url, comics_message = comics['img'], comics['alt']
    img_filename = f'{comics_id}.png'
    try:
        img_file = fetch_image(comics_img_url)

        with open(img_filename, "wb") as file:
            file.write(img_file)

        upload_url = fetch_upload_url(access_token)
        photos = save_photo(img_filename, upload_url, access_token)

        upload_photos(photos, community_id, comics_message)
    finally:
        os.remove(img_filename)

