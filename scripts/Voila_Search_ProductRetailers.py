#!/usr/local/bin/python3.9
# coding=utf-8
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

requests_cookies = {}
USERNAME = 'xiao20090813xiao@163.com'
PASSWORD = 'sunsh1ne0sunny'

logging.basicConfig(level=logging.INFO,
                    filename="Voila_Search_ProductRetailers.log",
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


def delete_monitor_instance():
    try:
        # 先起新pod，再删除旧pod，因此有可能出现此函数在新pod中执行后，旧pod仍未删除还在推送旧pod上的metric的情况,所以延迟300s后删除
        time.sleep(300)
        # 监控脚本运行前，先清理pushgateway中上由上一个监控实例推送的监控数据，以避免误报
        response = requests.get('http://pushgateway.voiladev.xyz:32684/metrics')
        content = str(response.content)
        instance = re.findall(r'instance=[\'|\"](monitorscripts.+?)[\'|\"]', content)
        uniq_instance = []
        job_name = ["voila_searchproductretailers"]

        # instance去重
        for i in instance:
            if i not in uniq_instance:
                uniq_instance.append(i)
        for job in job_name:
            for j in uniq_instance:
                url = "http://pushgateway.voiladev.xyz:32684/metrics/job/" + job + "/instance/" + j + "/env/prod"
                response = requests.delete(url)
                logging.info(
                    "pushgateway job is %s, delete instance %s successfully, url is %s, response.status_code is %s",
                    job, j, url, response.status_code)
    except Exception as e:
        logging.info(e)


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
            pushalert("voila_searchproductretailers_status", "1", "voila_searchproductretailers")

        # 等待页面加载
        time.sleep(seconds)

        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id=\"app\"]/div/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/input"))).send_keys(
                USERNAME)
        except Exception as e:
            pushalert("voila_searchproductretailers_status", "2", "voila_searchproductretailers")
            # exit()
        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/div/div/div[2]/div[1]/div[2]/form/div[2]/div/div[1]/input"))).send_keys(PASSWORD)
        except Exception as e:
            pushalert("voila_searchproductretailers_status", "3", "voila_searchproductretailers")
            # exit()
        # click "SIGN IN" button
        try:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                   '#app > div > div.container__main > div.login > div.login-form > form > div:nth-child(3) > div > button'))).click()
        except Exception as e:
            pushalert("voila_searchproductretailers_status", "4", "voila_searchproductretailers")
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
            pushalert("voila_searchproductretailers_status", "5", "voila_searchproductretailers")
            logging.info("Generate cookies failed: %s", requests_cookies)

        time.sleep(60 * 60 * 24 * 6)
        driver.quit()


def get_productretailers():
    while True:
        if not requests_cookies:
            time.sleep(20)
        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": "macOS",
            "content-type": "application/json",
            "referer": "https://creator.voila.love/bio/"
        }

        url = "https://creator.voila.love/_/voila/v2/retailers"
        try:
            response = requests.get(url, headers=headers, cookies=requests_cookies)

            response_data = json.loads(response.text).get("data")

            # logging.info("response_data.get(data) is %s, type is %s", response_data, type(response_data))

            retailers_num = len(response_data)
            logging.info("retailers_num is %s", retailers_num)

            i = 0
            retailers_name = []
            while i < retailers_num:
                retailers_name.append(response_data[i].get("brandName"))
                i += 1
            logging.info("retailers_name is %s", retailers_name)

            if retailers_num > 70 and retailers_name.count("") < 1 and response.status_code == 200:
                pushalert("voila_searchproductretailers_status", "0", "voila_searchproductretailers")
                logging.info("search product retailers successfully")
            else:
                pushalert("voila_searchproductretailers_status", "6", "voila_searchproductretailers")
                logging.info("search product retailers failed")
        except Exception as e:
            logging.info(e)
            pushalert("voila_searchproductretailers_status", "7", "voila_searchproductretailers")
        time.sleep(50)


if __name__ == "__main__":
    p1 = threading.Thread(target=login_get_cookies)
    p2 = threading.Thread(target=get_productretailers)

    p1.start()
    p2.start()
    delete_monitor_instance()
