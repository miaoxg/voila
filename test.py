#!/usr/local/bin/python3.9
# coding=utf-8
import json
import random
import threading
import time

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

USERNAME = 'xiao20090813xiao@163.com'
PASSWORD = 'sunsh1ne0sunny'

requests_cookies = {}
collection_name = "test"
collection_id = ""
userid = ""

# for add product to collection
sourceId = ""
uniqueCode = ""
type = ""
isDeleted = ""
feedCreateTime = ""


def login_get_cookies():
    while True:

        driver = ""
        if driver:
            driver.quit()

        seconds = random.randint(5, 9)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))
        wait = WebDriverWait(driver, 10)
        print("begin get cookies")
        # load page
        try:
            driver.get('https://creator.voila.love')
        except Exception as e:
            print("voila_addcollection_status", "1", "voila_adcollection")
            # exit()
        # 等待页面加载
        time.sleep(seconds)

        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id=\"app\"]/div/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/input"))).send_keys(
                USERNAME)
        except Exception as e:
            print("voila_addcollection_status", "2", "voila_addcollection")
            # exit()
        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/div/div/div[2]/div[1]/div[2]/form/div[2]/div/div[1]/input"))).send_keys(PASSWORD)
        except Exception as e:
            print("voila_addcollection_status", "3", "voila_addcollection")
            # exit()
        # click "SIGN IN" button
        try:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                   '#app > div > div.container__main > div.login > div.login-form > form > div:nth-child(3) > div > button'))).click()
        except Exception as e:
            print("voila_addcollection_status", "4", "voila_addcollection")
            # exit()

        # sleep必须要有，否则cookies获取不全
        time.sleep(seconds)

        cookies = driver.get_cookies()
        for c in cookies:
            requests_cookies[c['name']] = c['value']

        if requests_cookies:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "requests_cookies is: ", requests_cookies)
        else:
            # status=5 get cookies failed
            print("voila_addcollection_status", "5", "voila_addcollection")
        time.sleep(30)


def get_userid():
    while True:
        if not requests_cookies:
            time.sleep(60)
        else:
            time.sleep(30)
        global userid

        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": "macOS",
            "content-type": "application/json"
        }

        try:
            response = requests.get('https://creator.voila.love/_/voila/v1/who', cookies=requests_cookies,
                                    headers=headers)
            response_data = json.loads(response.text)

            userid = response_data.get('id')
        except Exception as e:
            print("voila_add_collection_status", "12", "voila_add_collection")
        print("get_userid requests_cookies is: ", requests_cookies)
        print("get_userid userid is: ", userid)
        print("get_userid response.status_code is: ", response.status_code)

        if userid is None or response.status_code != 200:
            print("voila_add_collection_status", "13", "voila_add_collection")


if __name__ == "__main__":
    p1 = threading.Thread(target=login_get_cookies)
    p2 = threading.Thread(target=get_userid)
    p1.start()
    p2.start()
