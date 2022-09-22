#!/usr/local/bin/python3.9
# coding=utf-8
import inspect
import json
import logging
import platform
import random
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

get_line = lambda: inspect.getframeinfo(inspect.stack()[1][0]).lineno
get_file = inspect.__file__
get_func = lambda: inspect.getframeinfo(inspect.stack()[1][0]).function

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

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(filename)s %(funcName)s：line %(lineno)d %(levelname)s %(message)s",
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
    driver = ""
    if driver:
        driver.quit()

    seconds = random.randint(5, 9)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')  ## to avoid getting detected

    if platform.system() == "Linux":
        driver = webdriver.Chrome(options=chrome_options, executable_path='/usr/bin/chromedriver')
    else:
        driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))

    wait = WebDriverWait(driver, 10)
    # load page
    try:
        driver.get('https://creator.voila.love')
    except Exception as e:
        pushalert("voila_addcollection_status", "1", "voila_addcollection")
        logging.error("driver.get https://creator.voila.love failed")

    # 等待页面加载
    time.sleep(seconds)

    try:
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[@id=\"app\"]/div/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/input"))).send_keys(USERNAME)
    except Exception as e:
        pushalert("voila_addcollection_status", "2", "voila_addcollection")
        # exit()
    try:
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div/div/div[2]/div[1]/div[2]/form/div[2]/div/div[1]/input"))).send_keys(PASSWORD)
    except Exception as e:
        pushalert("voila_addcollection_status", "3", "voila_addcollection")
        # exit()
    # click "SIGN IN" button
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                               '#app > div > div.container__main > div.login > div.login-form > form > div:nth-child(3) > div > button'))).click()
    except Exception as e:
        pushalert("voila_addcollection_status", "4", "voila_addcollection")
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
        pushalert("voila_addcollection_status", "5", "voila_addcollection")
        logging.error("Generate cookies failed")

        time.sleep(30)


def delete_all_collection():
    all_collection_id_list = []
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": "macOS",
        "content-type": "application/json",
        "referer": "https://creator.voila.love/bio/",
        "origin": "https://creator.voila.love",
        "authority": "creator.voila.love",
        "accept": "*/*"
    }

    search_url = 'https://creator.voila.love/_/voila/v2/feeds/collections?isSharePage=false'

    try:
        search_response = requests.get(search_url, cookies=requests_cookies, headers=headers)
    except requests.exceptions.RequestException as e:
        logging.error(e)

    all_collection_id = json.loads(search_response.text).get('data')

    for i in all_collection_id:
        all_collection_id_list.append(i.get('id'))

    logging.info(' all_collection_id_list is : %s', all_collection_id_list)

    if len(all_collection_id_list) != 0:
        logging.info(' all_collection_id_list is : %s', all_collection_id_list)
        for i in all_collection_id_list:
            delete_url = "https://creator.voila.love/_/voila/v2/feeds/collection/" + i
            try:
                delete_response = requests.delete(delete_url, cookies=requests_cookies, headers=headers)
            except Exception as e:
                pushalert("voila_delcollection_status", '1', "voila_delcollection")
                logging.error("e is: ", e, "id is : ", i)
            delete_response_data = json.loads(delete_response.text)
            logging.info("collectionid is %s,delete_response.status_code is %s", i, delete_response.status_code)
            logging.info("delete_response_data is %s", delete_response_data)

            if delete_response.status_code == 200:
                logging.info("delete collectionid %s successfully", i)
            else:
                logging.info("delete collectionid %s failed", i)
    else:
        logging.info("all_collection_id_list is None")


login_get_cookies()
delete_all_collection()
