import os
import requests
import time

result=0
lastResult=0

def download_file(url, destination_path, debug_print=True):
    global result
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Check for any request errors

        with open(destination_path, 'wb') as file:
            file.write(response.content)
        if debug_print==True:
            print(f"Downloaded file from {url} to {destination_path}")
        result+=1
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        print('Sleeping 5 seconds before trying again!')
        time.sleep(5)
        print('Trying again!')
        download_file(url, destination_path, debug_print)