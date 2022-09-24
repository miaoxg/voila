#!/usr/bin/python3
import json
import logging
import platform
import random
import re
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

USERNAME = 'xiao20090813xiao@163.com'
PASSWORD = 'sunsh1ne0sunny'
# the keyword for searching product
PRODUCTWORD = ['red', 'red shirt', 'man', 'child']

requests_cookies = {}

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
        # 等待页面加载
        time.sleep(seconds)

        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id=\"app\"]/div/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/input"))).send_keys(
                USERNAME)
        except Exception as e:
            pushalert("voila_searchproduct_status", "2", "voila_searchproduct")
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

        time.sleep(6 * 60 * 60)
        driver.close()


def search_product():
    while True:
        total_statuscode_list = []
        total_title_list = []

        if not requests_cookies:
            time.sleep(30)

        for i in PRODUCTWORD:
            headers = {
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
                "sec-ch-ua-platform": "macOS",
                "content-type": "application/json"
            }

            data = {
                "query": i,
                "sort": "SortTypeDefault",
                "page": 1,
                "pageSize": 10,
                "cursor": "",
                "isCollect": "false",
                "attributes": [],
                "categoryIds": [],
                "brands": [],
                "retailers": [],
                "price": {"min": 0, "max": 0},
                "discount": []
            }

            try:
                response = requests.post('https://creator.voila.love/_/voila/v2/product-gateway/search',
                                         cookies=requests_cookies, json=data, headers=headers)
                logging.info('query word is %s', i)
                response_data = json.loads(response.text)
                title_list = re.findall('title\': [\'|\"](.+?)[\'|\"],', str(response_data))
                for j in title_list:
                    total_title_list.append(j)
                total_statuscode_list.append(response.status_code)
                logging.info('total_statuscode_list is %s', total_statuscode_list)
            except Exception as e:
                pushalert("voila_searchproduct_status", "6", "voila_searchproduct")
                logging.info("response.status_code is %s", response.status_code)
            time.sleep(12)

        logging.info("total_statuscode_list is: %s", total_statuscode_list)
        logging.info("total_title_list is: %s", total_title_list)
        logging.info("len(total_statuscode_list) is: %s", len(total_statuscode_list))
        logging.info("len(total_title_list) is: %s", len(total_title_list))

        if total_statuscode_list.count(200) == len(PRODUCTWORD) and len(total_title_list) >= (
                len(PRODUCTWORD) - 1) * 10:
            pushalert("voila_searchproduct_status", "0", "voila_searchproduct")
            logging.info("search products successfully")
        else:
            pushalert("voila_searchproduct_status", "7", "voila_searchproduct")
            logging.info("search products failed")


if __name__ == "__main__":
    p1 = threading.Thread(target=login_get_cookies)
    p2 = threading.Thread(target=search_product)
    p1.start()
    p2.start()
