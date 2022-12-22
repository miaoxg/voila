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
                    filename='Voila_BIO_AD_Collection.log',
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
        job_name = ["voila_delcollection", "voila_addcollection"]

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
    try:
        seconds = random.randint(5, 9)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')  ## to avoid getting detected

        if platform.system() == "Linux":
            driver = webdriver.Chrome(options=chrome_options, executable_path='/usr/bin/chromedriver')
        else:
            driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))
        wait = WebDriverWait(driver, 10)
        logging.info("begin get cookies")
        # load page
        try:
            driver.get('https://creator.voila.love')
        except Exception as e:
            pushalert("voila_addcollection_status", "1", "voila_addcollection")
            logging.info(e)
            # exit()
        # 等待页面加载
        time.sleep(seconds)

        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id=\"app\"]/div/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/input"))).send_keys(
                USERNAME)
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
        try:
            cookies = driver.get_cookies()
            for c in cookies:
                requests_cookies[c['name']] = c['value']

            if requests_cookies:
                logging.info('Generate cookies successfully!')
            else:
                # status=5 get cookies failed
                pushalert("voila_addcollection_status", "5", "voila_addcollection")
                logging.info("Generate cookies failed!")
        except Exception as e:
            logging.info(e)
    except Exception as e:
        logging.info(e)


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

        all_collection_id = json.loads(search_response.text).get('data')

        for i in all_collection_id:
            all_collection_id_list.append(i.get('id'))

        logging.info(' all_collection_id_list is : %s', all_collection_id_list)

        if len(all_collection_id_list) != 0:
            logging.info(' all_collection_id_list is : %s', all_collection_id_list)
            for i in all_collection_id_list:
                delete_url = "https://creator.voila.love/_/voila/v2/feeds/collection/" + i
                delete_response = requests.delete(delete_url, cookies=requests_cookies, headers=headers)
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
    except Exception as e:
        logging.info(e)


def generate_collection_id():
    global collection_id

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": "macOS",
        "content-type": "application/json",
        "referer": "https://creator.voila.love/bio/"
    }

    data = {
        "name": ""
    }

    url = "https://creator.voila.love/_/voila/v2/feeds/collection"
    try:
        response = requests.post(url, cookies=requests_cookies, headers=headers, json=data)

        collection_id = json.loads(response.text).get("id")

        if response.status_code == 200 and collection_id is not None:
            logging.info("Generate collection id successfully: %s", collection_id)
        else:
            pushalert("voila_addcollection_status", "7", "voila_addcollection")
            logging.info("Generate collection id failed: %s", collection_id)
    except Exception as e:
        logging.info(e)


def bind_collection_id_name():
    global collection_id
    global collection_name
    try:
        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": "macOS",
            "content-type": "application/json",
            "referer": "https://creator.voila.love/bio/"
        }

        data = {
            "id": collection_id,
            "name": collection_name
        }

        url = "https://creator.voila.love/_/voila/v2/feeds/collection"

        response = requests.post(url, cookies=requests_cookies, headers=headers, json=data)
        logging.info("bind_collection_id_name response.status_code is %s", response.status_code)
        response_collection_id = json.loads(response.text).get("id")
        response_collection_name = json.loads(response.text).get("name")
        logging.info("response_collection_id is %s , response_collection_name is %s", response_collection_id,
                     response_collection_name)

        if response.status_code == 200 and response_collection_id == collection_id and response_collection_name == collection_name:
            logging.info(
                "bind collection id and name successfully. response_collection_id is %s, response_collection_name is %s",
                response_collection_id, response_collection_name)
        else:
            pushalert("voila_addcollection_status", "8", "voila_addcollection")
            logging.info(
                "bind collection id and name failed. response_collection_id is %s, response_collection_name is %s",
                response_collection_id, response_collection_name)
    except Exception as e:
        logging.info(e)


def get_userid():
    global userid
    try:

        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": "macOS",
            "content-type": "application/json"
        }

        response = requests.get('https://creator.voila.love/_/voila/v1/who', cookies=requests_cookies, headers=headers)
        response_data = json.loads(response.text)

        userid = response_data.get('id')

        logging.info("get_userid userid is: %s", userid)

        if userid is None or response.status_code != 200:
            pushalert("voila_addcollection_status", "9", "voila_addcollection")
        logging.info("get_userid response.status_code is: %s", response.status_code)
    except Exception as e:
        logging.info(e)


def list_products():
    global sourceId
    global uniqueCode
    global type
    global isDeleted
    global feedCreateTime

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": "macOS",
        "content-type": "application/json",
        "referer": "https://creator.voila.love/bio/",
        "origin": "https://creator.voila.love",
        "authority": "creator.voila.love",
        "accept": "*/*"
    }

    try:
        url = "https://creator.voila.love/_/voila/v2/feeds?count=20&cursor=&userId=" + userid + "&isRetProduct=true&isSharePage=false&collectionId=" + collection_id
        list_products_response = requests.get(url, cookies=requests_cookies, headers=headers)
        list_products_response_data = json.loads(list_products_response.text).get("data")

        # add product to collection
        #         i = 0
        #         while i < len(list_products_response_data):
        #             if list_products_response_data[i].get('type') == 'Product':
        #                 type = list_products_response_data[i].get('type')
        #                 uniqueCode = list_products_response_data[i].get('id')
        #                 sourceId = list_products_response_data[i].get('data').get('sku').get('sourceId')
        #                 feedCreateTime = time.strftime("%Y-%m-%d %H:%M", time.localtime(
        #                     int(list_products_response_data[i].get('data').get('sku').get('createdUtc'))))
        #                 if list_products_response_data[i].get('data').get('sku').get('isDeleted') == 0:
        #                     isDeleted = bool(0)
        #                 else:
        #                     isDeleted = bool(1)
        #                 break
        #             i += 1
        #     except Exception as e:
        #         pushalert("voila_addcollection_status", '14', "voila_addcollection")
        #         print("list_products e is: ", e)

        i = 0
        while i < len(list_products_response_data):
            if list_products_response_data[i].get('type') == 'Post':
                type = list_products_response_data[i].get('type')
                uniqueCode = list_products_response_data[i].get('id')
                sourceId = list_products_response_data[i].get('data').get('id')
                feedCreateTime = time.strftime("%Y-%m-%d %H:%M", time.localtime(
                    int(list_products_response_data[i].get('data').get('products')[0].get('sku').get('createdUtc'))))
                if list_products_response_data[i].get('data').get('products')[0].get('sku').get('isDeleted') == 0:
                    isDeleted = bool(0)
                else:
                    isDeleted = bool(1)
                break
            i += 1
        logging.info("uniqueCode is %s, sourceId is %s, type is %s, isDeleted is %s, feedCreateTime is %s", uniqueCode,
                     sourceId, type, isDeleted, feedCreateTime)

        if list_products_response.status_code == 200 and uniqueCode is not None and sourceId is not None and type is not None and feedCreateTime is not None:
            logging.info("list products successfully")
        else:
            pushalert("voila_addcollection_status", "10", "voila_addcollection")
            logging.info("list products failed")
    except Exception as e:
        logging.info(e)


def add_product_to_collection():
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": "macOS",
        "content-type": "application/json",
        "referer": "https://creator.voila.love/bio/",
        "origin": "https://creator.voila.love",
        "authority": "creator.voila.love",
        "accept": "*/*"
    }

    data = {
        "id": collection_id,
        "data": [
            {
                "type": type,
                "sourceId": sourceId,
                "isDeleted": isDeleted,
                "uniqueCode": uniqueCode,
                "feedCreateTime": feedCreateTime
            }
        ]
    }

    url = "https://creator.voila.love/_/voila/v2/feeds/collection/content"

    try:
        response = requests.post(url, cookies=requests_cookies, headers=headers, json=data)

        if response.status_code == 200:
            logging.info("add_product_to_collection successfully: %s, response.status_code is: %s", collection_id,
                         response.status_code)
        else:
            pushalert("voila_addcollection_status", "11", "voila_addcollection")
            logging.info("add_product_to_collection failed: %s, response.status_code is: %s", collection_id,
                         response.status_code)
    except Exception as e:
        logging.info(e)


def list_collection():
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": "macOS",
        "content-type": "application/json",
        "referer": "https://creator.voila.love/bio/",
        "origin": "https://creator.voila.love",
        "authority": "creator.voila.love",
        "accept": "*/*"
    }

    try:
        url = "https://creator.voila.love/_/voila/v2/feeds/collection?count=1&cursor=&isRetProduct=true&isSharePage=false&id=" + collection_id
        response = requests.get(url, cookies=requests_cookies, headers=headers)
        id = json.loads(response.text).get('data').get('id')

        if response.status_code == 200 and id == collection_id:
            pushalert("voila_addcollection_status", "0", "voila_addcollection")
            logging.info("list collection successfully: %s, %s", collection_id, id)
        else:
            pushalert("voila_addcollection_status", "12", "voila_addcollection")
            logging.info("list collection failed: %s, %s", collection_id, id)
    except Exception as e:
        logging.info(e)


def delete_collection():
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": "macOS",
        "content-type": "application/json",
        "referer": "https://creator.voila.love/bio/",
        "origin": "https://creator.voila.love",
        "authority": "creator.voila.love",
        "accept": "*/*"
    }

    try:
        url = "https://creator.voila.love/_/voila/v2/feeds/collection/" + collection_id
        delete_response = requests.delete(url, cookies=requests_cookies, headers=headers)

        if delete_response.status_code == 200:
            logging.info("delete collection successfully: %s, %s", collection_id, collection_name)
            pushalert("voila_delcollection_status", "0", "voila_delcollection")
        else:
            pushalert("voila_delcollection_status", "2", "voila_delollection")
            logging.info("delete collection failed: %s, %s", collection_id, collection_name)
    except Exception as e:
        logging.info(e)


def login():
    while True:
        try:
            login_get_cookies()
            # 每6小时重新生成一次cookies
            time.sleep(60 * 60 * 24 * 6)
            driver.quit()
        except Exception as e:
            print(e)

def total():
    while True:
        # 解决第一次启动时login函数生成cookies在后，下列函数执行失败的问题
        try:
            if not requests_cookies:
                time.sleep(60)
            delete_all_collection()
            time.sleep(10)
            generate_collection_id()
            time.sleep(10)
            bind_collection_id_name()
            time.sleep(10)
            get_userid()
            time.sleep(10)
            list_products()
            time.sleep(10)
            add_product_to_collection()
            time.sleep(10)
            list_collection()
            time.sleep(10)
            delete_collection()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    p1 = threading.Thread(target=login)
    p2 = threading.Thread(target=total)
    p1.start()
    p2.start()
    delete_monitor_instance()
