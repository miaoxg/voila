#!/usr/local/bin/python3.9
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

USERNAME = 'xiao20090813xiao@163.com'
PASSWORD = 'sunsh1ne0sunny'

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
            chrome_options.add_argument('--remote-debugging-port=9228')
            driver = webdriver.Chrome(options=chrome_options, executable_path='/usr/bin/chromedriver')
        else:
            driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))
        wait = WebDriverWait(driver, 10)
        logging.info("begin get cookies")
        # load page
        try:
            driver.get('https://creator.voila.love')
        except Exception as e:
            pushalert("voila_searchretailer_status", "1", "voila_searchretailer")

        # 等待页面加载
        time.sleep(seconds)

        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id=\"app\"]/div/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/input"))).send_keys(
                USERNAME)
        except Exception as e:
            pushalert("voila_searchretailer_status", "2", "voila_searchretailer")
            # exit()
        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/div/div/div[2]/div[1]/div[2]/form/div[2]/div/div[1]/input"))).send_keys(PASSWORD)
        except Exception as e:
            pushalert("voila_searchretailer_status", "3", "voila_searchretailer")
            # exit()
        # click "SIGN IN" button
        try:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                   '#app > div > div.container__main > div.login > div.login-form > form > div:nth-child(3) > div > button'))).click()
        except Exception as e:
            pushalert("voila_searchretailer_status", "4", "voila_searchretailer")
            # exit()

        # sleep必须要有，否则cookies获取不全
        time.sleep(20)

        cookies = driver.get_cookies()
        for c in cookies:
            requests_cookies[c['name']] = c['value']

        if requests_cookies:
            logging.info('Generate cookies successfully: %s', requests_cookies)
        else:
            # status=5 get cookies failed
            pushalert("voila_searchretailer_status", "5", "voila_searchretailer")
            logging.info("Generate cookies failed: %s", requests_cookies)

        time.sleep(6 * 60 * 60)
        driver.close()

def search_retailers():
    while True:
        total_retailers = ""
        if not requests_cookies:
            time.sleep(60)

        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": "macOS",
            "content-type": "application/json",
            "referer": "https://creator.voila.love/bio/"
        }

        url = "https://creator.voila.love/_/voila/v2/retailers?page=1&count=30&sort=DEFAULT&weight=false&query=&isReturnAllData=true"
        try:
            response = requests.get(url, cookies=requests_cookies, headers=headers)
            repsonse_data = json.loads(response.text)
            total_retailers = repsonse_data['pagination'].get('total')
        except Exception as e:
            logging.info(e)

        if response.status_code == 200 and total_retailers > 20000:
            pushalert("voila_searchretailer_status", "0", "voila_searchretailer")
            logging.info("search retailers successfully. response.status_code is: %s, total_retailers: %s",
                         response.status_code, total_retailers)
        else:
            pushalert("voila_searchretailer_status", "6", "voila_searchretailer")
            logging.info("search retailers failed. response.status_code is: %s, total_retailers: %s",
                         response.status_code, total_retailers)

        time.sleep(50)


if __name__ == "__main__":
    p1 = threading.Thread(target=login_get_cookies)
    p2 = threading.Thread(target=search_retailers)
    p1.start()
    p2.start()
