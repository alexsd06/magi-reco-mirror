# https://android.magi-reco.com/magica/resource/download/asset/master/resource/image_native/mini/anime_v2/mini_100100_d_r0.png
# https://jp.rika.ren/magica/resource/image_native/mini/anime_v2/mini_100100_d_r0.png
# https://ex.magi.co/magica/resource/image_native/mini/anime_v2/mini_100100_d_r0.png (CLOSED)

import json
import os
import shutil
import threading
import time
from tqdm import tqdm
import concurrent.futures

import my_wget
from my_wget import download_file


root_url = 'https://android.magi-reco.com' #or "https://jp.rika.ren/"
json_url = f"{root_url}/magica/resource/download/asset/master/"
resource_url = f"{root_url}/magica/resource/download/asset/master/resource/"

# List of JSON assets to download
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

# Paths within the JSON structure to be checked for character data
resource_character_list_json = [
    "image_native/live2d/list.json",
    "image_native/live2d_v4/list.json",
]

# File to store joined JSON
full_json_for_browse = 'asset_joined.json'

# List to store URLs to be downloaded
download_urls = []

# Function to create a joined JSON file from individual JSON assets
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

# Function to download the JSON assets if they are not already downloaded
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

# Function to traverse JSON and add URLs to download list
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

# Function to load download URLs from the JSON assets
def load_download_urls_from_json():
    for json_asset in json_assets:
        json_data = ""
        with open(json_asset, 'r') as file:
            json_data = file.read()
        json_data = json.loads(json_data)
        traverse_json_and_add_urls(json_data)
    print('Loaded download urls!')

# Function to create the filesystem structure
def create_filesystem_structure():
    create_resources()
    os.chdir('resource')
    for download_url in download_urls:
        folders = os.path.split(download_url)[0]
        if not os.path.exists(folders):
            os.makedirs(folders)
    print("Created filesystem structure!")

# Function to update the progress bar during downloads
def update_progress_bar(progress):
    while True:
        progress.update(my_wget.result - my_wget.lastResult)
        my_wget.lastResult = my_wget.result
        time.sleep(0.5)

# Function to download files from URLs
def download_from_urls():
    progress = tqdm(total=len(download_urls), unit='B', unit_scale=False, desc='Downloading', leave=False)
    max_workers = 10

    my_wget.result = 0
    x = threading.Thread(target=lambda: update_progress_bar(progress))
    x.start()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download_file, resource_url + valid_url, valid_url, False) for valid_url in download_urls]

# Helper function to remove files directory
def remove_files():
    if os.path.exists('files'):
        shutil.rmtree('files')

# Helper function to create files directory
def create_files():
    if not os.path.exists('files'):
        os.mkdir('files')

# Helper function to remove resources directory
def remove_resources():
    if os.path.exists('resource'):
        shutil.rmtree('resource')

# Helper function to create resources directory
def create_resources():
    if not os.path.exists('resource'):
        os.mkdir('resource')

# Main execution
if __name__ == "__main__":
    create_files()
    download_json_assets()
    create_joined_json()
    load_download_urls_from_json()

    print(len(download_urls))

    create_filesystem_structure()
    download_from_urls()
