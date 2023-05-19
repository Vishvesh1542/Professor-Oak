import interactions
import aiohttp
import cv2
import os
import numpy as np


class AsyncList:
    def __init__(self, lst=list()):
        self.lst = lst
        self.i = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.i >= len(self.lst):
            raise StopAsyncIteration
        item = self.lst[self.i]
        self.i += 1
        return item


class AsyncDict:
    def __init__(self, dct):
        self.dct = dct
        self.keys = list(dct.keys())
        self.i = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.i >= len(self.keys):
            raise StopAsyncIteration
        key = self.keys[self.i]
        value = self.dct[key]
        self.i += 1
        return key, value


# Getting all the images
def init_files():
    global images
    images = {}

    for image in os.listdir('data/image_dataset'):
        images[image[:-4]] = cv2.imread('data/image_dataset/' + image)
    print('(re)loaded pokemon images')


async def download_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            image_ = await response.read()
            return image_


async def get_image(url):
    image_raw = await download_image(url)
    np_image = np.frombuffer(image_raw, np.uint8)
    image_ = cv2.imdecode(np_image, cv2.IMREAD_UNCHANGED)
    return cv2.resize(image_, (10, 10)), image_


def is_similar(imageA, imageB):
    imageA = cv2.cvtColor(imageA, cv2.COLOR_RGBA2RGB)
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])

    if err < 1500:
        return True
    else:
        return False


async def get_best_match(image):
    async for i, v in AsyncDict(images):
        if is_similar(image, v):
            return i

    return 'Unknown'


async def add_unrecognised(image):
    image_list = os.listdir(os.getcwd() + '/data/unrecognised')
    new_list = [int(i[:-4]) for i in image_list]
    if image_list != []:
        last_number = max(new_list)
    else:
        last_number = 0

    cv2.imwrite('/data/unrecognised/' +
                str(last_number + 1) + '.png', image)

async def name_pokemon(image_url):
    embed = interactions.Embed(
        title='Unknown', color=0xC86464)

    # Getting image
    image, full_size = await get_image(image_url)
    pokemon_name = await get_best_match(image)
    if pokemon_name == 'Unknown':
        await add_unrecognised(full_size)

    embed.color = 0x64C864
    embed.title = pokemon_name

    return embed
