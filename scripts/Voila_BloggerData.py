#!/usr/local/bin/python3.9
# coding=utf-8
import datetime
import json
import logging
import platform
import random
import threading
import time

import requests
from pushgateway_client import client
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

USERNAME = 'miaoxg'
PASSWORD = 'aSYsEoPZAmc3y7l5'

requests_cookies = {}

blogger = "tiamcintosh"
creatorId = ""

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(filename)s %(funcName)s：line %(lineno)d threadid %(thread)d %(levelname)s %(message)s",
                    datefmt='%Y-%m-%d %H:%M:%S'
                    )


def pushalert(metric_name="test", metric_value="-1", job_name="job_name"):
    result = client.push_data(
        url="pushgateway.voiladev.xyz:32684",
        metric_name=metric_name,
        metric_value=metric_value,
        job_name=job_name,
        timeout=5,
        labels={
            "env": "prod"
        }
    )


def login_get_cookies():
    while True:
        driver = ""
        if driver:
            driver.quit()

        seconds = random.randint(5, 9)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')  ## to avoid getting detected

        if platform.system() == "Linux":
            chrome_options.add_argument('--remote-debugging-port=9225')
            driver = webdriver.Chrome(options=chrome_options, executable_path='/usr/bin/chromedriver')
        else:
            driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))
        wait = WebDriverWait(driver, 10)
        logging.info("begin get cookies")
        # load page
        try:
            driver.get('https://creator.voila.love')
        except Exception as e:
            pushalert("voila_searchproduct_status", "1", "voila_searchproduct")
            # exit()
        # 等待页面加载
        time.sleep(seconds)

        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id=\"app\"]/div/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/input"))).send_keys(
                USERNAME)
        except Exception as e:
            pushalert("voila_searchproduct_status", "2", "voila_searchproduct")
            # exit()
        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/div/div/div[2]/div[1]/div[2]/form/div[2]/div/div[1]/input"))).send_keys(PASSWORD)
        except Exception as e:
            pushalert("voila_searchproduct_status", "3", "voila_searchproduct")
            # exit()
        # click "SIGN IN" button
        try:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                   '#app > div > div.container__main > div.login > div.login-form > form > div:nth-child(3) > div > button'))).click()
        except Exception as e:
            pushalert("voila_searchproduct_status", "4", "voila_searchproduct")
            # exit()

        # sleep必须要有，否则cookies获取不全
        time.sleep(seconds)

        cookies = driver.get_cookies()
        for c in cookies:
            requests_cookies[c['name']] = c['value']

        if requests_cookies:
            logging.info('Generate cookies successfully!')
        else:
            # status=5 get cookies failed
            pushalert("voila_searchproduct_status", "5", "voila_searchproduct")
            logging.info("Generate cookies failed!")

        time.sleep(86400 * 6)


def get_bloggerdata():
    global creatorId
    while True:
        pv_list = []
        uv_list = []
        if not requests_cookies:
            time.sleep(60)
        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": "macOS",
            "content-type": "application/json; charset=UTF-8",
            "referer": "https://dashboard.voila.love/data/",
            "origin": "https://dashboard.voila.love",
            "authority": "dashboard.voila.love",
            "accept": "application/json, text/plain, */*"
        }

        data = {
            "query": {
                "and": {
                    "values": [
                        {
                            "condition": {
                                "key": "info",
                                "operator": "ne",
                                "values": [
                                    "platform",
                                    "ldap"
                                ]
                            }
                        },
                        {
                            "condition": {
                                "key": "name",
                                "operator": "startswith",
                                "values": [
                                    blogger
                                ]
                            }
                        }
                    ]
                }
            },
            "sort": {
                "rules": [
                    {
                        "key": "createTime",
                        "descending": bool(1)
                    }
                ]
            },
            "start": 0,
            "size": 50
        }

        url = "https://dashboard.voila.love/_/security/identity/user/list"

        try:
            response = requests.post(url, json=data, headers=headers, cookies=requests_cookies)
            creatorId = json.loads(response.text).get("users")[0].get('id')
        except Exception as e:
            logging.info(e)

        if response.status_code == 200 and creatorId:
            logging.info("Get creatorid successfully. response.status_code is :%s, creatorId is :s%",
                         response.status_code,
                         creatorId)
        else:
            logging.info("Get creatorid failed.response.status_code is :%s, creatorId is :%s", response.status_code,
                         creatorId)

        today = str(datetime.date.today()) + " 08:00:00"
        format_today = time.mktime(time.strptime(today, "%Y-%m-%d %H:%M:%S"))
        unix_today = str(format_today).split('.')[0]
        unix_7_day_before = str(format_today - 86400 * 7).split('.')[0]

        headers = {
            "authority": "dashboard.voila.love",
            "accept": "*/*",
            "accept-language": "en,zh;q=0.9,zh-CN;q=0.8",
            "content-type": "application/json",
            "referer": "https://dashboard.voila.love/creator/",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
        }

        try:
            url = "https://dashboard.voila.love/_/voila/v2/metrics/user/core?beginDate=" + unix_7_day_before + "&endDate=" + unix_today + "&creatorId=" + creatorId
            response = requests.get(url, cookies=requests_cookies, headers=headers)
            response_data = json.loads(response.text).get("daily")
        except Exception as e:
            logging.info(e)

        for i in response_data:
            pv_list.append(i.get("pv"))
            uv_list.append(i.get("uv"))

        logging.info("pv_list is %s, uv_list is %s", pv_list, uv_list)

        if response.status_code == 200 and pv_list.count(0) < 3 and uv_list.count(0) < 3 and len(uv_list) == 8 and len(
                pv_list) == 8:
            # pushalert()
            logging.info("get blogger %s's data success", blogger)
        else:
            # pushalert()
            logging.info("get blogger %s's data success", blogger)
        time.sleep(50)


if __name__ == "__main__":
    p1 = threading.Thread(target=login_get_cookies)
    p2 = threading.Thread(target=get_bloggerdata)
    p1.start()
    p2.start()
