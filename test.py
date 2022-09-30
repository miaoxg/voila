import time

import requests

while True:
    try:
        response = requests.get('https://www.baidu.co')
        if response.status_code == 200:
            print("status code is ", response.status_code)
        else:
            print("status code is", response.status_code)
    except Exception as e:
        print(e)
    time.sleep(1)
