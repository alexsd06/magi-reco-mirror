import json
import os.path
import shutil
import threading
import time

import my_wget
from my_wget import download_file

import concurrent.futures
from tqdm import tqdm

import requests

# https://android.magi-reco.com/magica/resource/download/asset/master/resource/image_native/mini/anime_v2/mini_100100_d_r0.png
# https://jp.rika.ren/magica/resource/image_native/mini/anime_v2/mini_100100_d_r0.png
# https://ex.magi.co/magica/resource/image_native/mini/anime_v2/mini_100100_d_r0.png

json_assets = [
    "asset_char_list.json",
    "asset_config.json",
    "asset_fullvoice.json",
    "asset_main.json",
    "asset_movie_high.json",
    "asset_movie_low.json",
    "asset_movieall_high.json",
    "asset_movieall_low.json",
    "asset_prologue_main.json",
    "asset_prologue_voice.json",
    "asset_voice.json"
]

resource_character_list_json = [
    "image_native/live2d/list.json",
    "image_native/live2d_v4/list.json",
]

root_url='https://android.magi-reco.com'

json_url = f"{root_url}/magica/resource/download/asset/master/"
resource_url = f"{root_url}/magica/resource/download/asset/master/resource/"

full_json_for_browse = 'asset_joined.json'

download_urls = []


def create_joined_json():
    if not os.path.exists(full_json_for_browse):
        print('Creating joined json!')
        asset_joined = ""
        for json_asset in json_assets:
            with open(json_asset, 'r') as file:
                text = file.read()
                asset_joined += text
        with open(full_json_for_browse, 'w') as file:
            file.write(asset_joined)
    else:
        print('joined.json already existing!')


def download_json_assets():
    if not os.path.exists('files'):
        os.mkdir('files')
    os.chdir('files')
    for json_asset in json_assets:
        if os.path.exists(json_asset):
            print(json_asset + " already on filesystem!")
            continue
        url = json_url + json_asset
        download_file(url, json_asset)


def remove_files():
    if os.path.exists('files'):
        shutil.rmtree('files')

def create_files():
    if not os.path.exists('files'):
        os.mkdir('files')


def traverse_json_and_add_urls(json_data):
    item_list = []
    if type(json_data) == dict:
        for key in json_data.keys():
            item = json_data[key]
            item_list.append(item)
            if key == 'url':
                download_urls.append(item)
    elif type(json_data) == list:
        for item in json_data:
            item_list.append(item)
    for item in item_list:
        if type(item) == dict or type(item) == list:
            traverse_json_and_add_urls(item)


def load_download_urls_from_json():
    for json_asset in json_assets:
        json_data = ""
        with open(json_asset, 'r') as file:
            json_data = file.read()
        json_data = json.loads(json_data)
        traverse_json_and_add_urls(json_data)
    print('Loaded download urls!')

def remove_resources():
    if os.path.exists('resource'):
        shutil.rmtree('resource')

def create_resources():
    if not os.path.exists('resource'):
        os.mkdir('resource')

def create_filesystem_structure(that_contains):
    # remove_resources()
    create_resources()
    os.chdir('resource')
    for download_url in download_urls:
        valid=False
        for li in that_contains:
            valid_list=True
            for item in li:
                if item not in download_url:
                    valid_list=False
            if valid_list==True:
                valid=True
                break
        if valid==False:
            continue
        #print(download_urls)
        folders = os.path.split(download_url)[0]
        if not os.path.exists(folders):
            os.makedirs(folders)
    print("Created filesystem structure!")

def update_progress_bar(progress):
    while True:
        progress.update(my_wget.result-my_wget.lastResult)
        my_wget.lastResult=my_wget.result
        time.sleep(0.5)

def download_from_urls(that_contains):
    valid_urls=[]
    for download_url in download_urls:
        valid = False
        for li in that_contains:
            valid_list = True
            for item in li:
                if item not in download_url:
                    valid_list = False
            if valid_list == True:
                valid = True
                break
        if valid == False:
            continue

        if download_url not in valid_urls:
            valid_urls.append(download_url)

    progress = tqdm(total=len(valid_urls), unit='B', unit_scale=False, desc='Downloading', leave=False)
    max_workers=10

    my_wget.result=0
    x=threading.Thread(target=lambda: update_progress_bar(progress))
    x.start()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download_file, resource_url+valid_url, valid_url, False) for valid_url in valid_urls]

only_that_contains={
    'image_native': {
        'mini': {
            'image': ['2001', '2002', '2003', '2004', '2005', '2006', '2007']
        }
    }
}

restriction_list=[]

def restriction_dict_to_list(data, father):
    if type(data)==dict:
        for key in data.keys():
            restriction_dict_to_list(data[key], father+'~'+key)
    elif type(data)==list:
        for item in data:
            string=father+'~'+item
            split=string.split('~')
            split=split[1:]
            restriction_list.append(split)
    else:
        string=father+'~'+data
        split=string.split('~')
        split=split[1:]
        restriction_list.append(split)

if __name__ == "__main__":
    # remove_files()
    create_files()
    download_json_assets()
    create_joined_json()
    load_download_urls_from_json()

    restriction_dict_to_list(only_that_contains, "")
    print(restriction_list)
    print(len(download_urls))

    create_filesystem_structure(restriction_list)
    download_from_urls(restriction_list)
