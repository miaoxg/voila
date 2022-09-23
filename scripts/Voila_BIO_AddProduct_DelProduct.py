#!/usr/local/bin/python3.9
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
response_data = {}
seconds = random.randint(5, 9)

# 可控制窗口大小
# driver.maximize_window()

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
            chrome_options.add_argument('--remote-debugging-port=9223')
            driver = webdriver.Chrome(options=chrome_options, executable_path='/usr/bin/chromedriver')
        else:
            driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))
        wait = WebDriverWait(driver, 10)
        logging.info("begin get cookies")
        # load page
        try:
            driver.get('https://creator.voila.love')
        except Exception as e:
            pushalert("voila_addproduct_status", "1", "voila_addproduct")
            # exit()
        # 等待页面加载
        time.sleep(seconds)

        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "//*[@id=\"app\"]/div/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/input"))).send_keys(
                USERNAME)
        except Exception as e:
            pushalert("voila_addproduct_status", "2", "voila_addproduct")
            # exit()
        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "/html/body/div/div/div[2]/div[1]/div[2]/form/div[2]/div/div[1]/input"))).send_keys(PASSWORD)
        except Exception as e:
            pushalert("voila_addproduct_status", "3", "voila_addproduct")
            # exit()
        # click "SIGN IN" button
        try:
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                   '#app > div > div.container__main > div.login > div.login-form > form > div:nth-child(3) > div > button'))).click()
        except Exception as e:
            pushalert("voila_addproduct_status", "4", "voila_addproduct")
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
            pushalert("voila_addproduct_status", "5", "voila_addproduct")
            logging.info("Generate cookies failed!")

    time.sleep(518400)


def search_add_product():
    while True:

        if not requests_cookies:
            time.sleep(60)

        headers = {
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": "macOS",
            "content-type": "application/json",
            "referer": "https://creator.voila.love/bio/"
        }

        data = {
            "query": "shoes",
            "sort": "SortTypeDefault",
            "page": 1,
            "pageSize": 1,
            "cursor": "",
            "filtration": "Filtration",
            "postId": 0,
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
        except Exception as e:
            pushalert("voila_addproduct_status", "6", "voila_addproduct")

        try:
            response_data = json.loads(response.text)
            skuProductId = response_data.get('data')[0].get('sku').get('skuProductId')
            spuProductId = response_data.get('data')[0].get('sku').get('spuProductId')
            canonicalUrl = response_data.get('data')[0].get('sku').get('canonicalUrl')
            price = response_data.get('data')[0].get('sku').get('price')
            description = response_data.get('data')[0].get('sku').get('description')
            retailer = response_data.get('data')[0].get('sku').get('retailer')
            siteName = response_data.get('data')[0].get('sku').get('siteName')
            title = response_data.get('data')[0].get('sku').get('title')
            brandName = response_data.get('data')[0].get('sku').get('brandName')
            images = response_data.get('data')[0].get('sku').get('resource')

            # logging.info(
            #     'skuProductId is %s, spuProductId is %s, canonicalUrl is %s, price is %s, description is %s, retailer is %s, siteName is %s, title is %s, brandName is %s, images is %s',
            #     skuProductId, spuProductId, canonicalUrl, price, description, retailer, siteName, title, brandName,
            #     images)
            logging.info("search product generate parameters successfully.")

        except TypeError as e:
            logging.error("TypeError is :", e)
            # some var is None
            pushalert("voila_addproduct_status", "7", "voila_addproduct")
            logging.info("search product generate parameters failed.")

        if response.status_code == 200:
            logging.info("search product successfully,status code is %s", response.status_code)
        else:
            pushalert("voila_addproduct_status", "8", "voila_addproduct")
            logging.info("search product failed,status code is %s", response.status_code)

        # def bio_add_product():

        add_product_data = {
            "data": {
                "type": "Product",
                "data": {
                    "@type": "type.googleapis.com/chameleon.voila.v1.post.AddProductRequest",
                    "postId": "0",
                    "data": [
                        {
                            "skuId": skuProductId,
                            "spuId": spuProductId,
                            "canonicalUrl": canonicalUrl,
                            "productInfo": {
                                "title": title,
                                "brandName": brandName,
                                "desc": description,
                                "images": images,
                                "price": price,
                                "retailer": retailer,
                                # "retailer": "",
                                "siteName": siteName
                            },
                            "from": "ProductFromWarehouse"

                        }
                    ],
                    "verb": ""
                }
            }
        }

        try:
            response = requests.post('https://creator.voila.love/_/voila/v2/feeds', cookies=requests_cookies,
                                     json=add_product_data, headers=headers)
            addproduct_response_data = json.loads(response.text)
            title = re.findall('title\': [\'|\"](.+?)[\'|\"],', str(response_data))
            id = addproduct_response_data['data'][0].get('id')
            logging.info("id is: %s, title is %s, response.status_code is %s", id, title, response.status_code)
        except Exception as e:
            pushalert("voila_addproduct_status", "9", "voila_addproduct")
            logging.info("e")

        if response.status_code == 200 and title != None and id != None:
            pushalert("voila_addproduct_status", "0", "voila_addproduct")
            logging.info("add product success")
        else:
            pushalert("voila_addproduct_status", "10", "voila_addproduct")
            logging.info("add product failed")

        time.sleep(30)

        delete_url = "https://creator.voila.love/_/voila/v2/feeds/batch?ids=" + id
        try:
            delete_response = requests.delete(delete_url, cookies=requests_cookies, headers=headers)
            deleteproduct_response_data = json.loads(delete_response.text)
            logging.info("deleteproduct_response_data is %s", deleteproduct_response_data)
        except Exception as e:
            pushalert("voila_delproduct_status", "1", "voila_delproduct")
            logging.info("delete")

        if delete_response.status_code == 200:
            logging.info("delete_response.status_code is %s", delete_response.status_code)
            pushalert("voila_delproduct_status", "0", "voila_delproduct")
        else:
            logging.info("delete_response.status_code is %s", delete_response.status_code)
            pushalert("voila_delproduct_status", "2", "voila_delproduct")
    time.sleep(20)


if __name__ == "__main__":
    p1 = threading.Thread(target=login_get_cookies)
    p2 = threading.Thread(target=search_add_product)
    p1.start()
    p2.start()
