#!/usr/local/bin/python3.9
# coding=utf-8
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import random
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import json
import requests
from pushgateway_client import client

USERNAME = 'xiao20090813xiao@163.com'
PASSWORD = 'sunsh1ne0sunny'

seconds = random.randint(5, 9)
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

requests_cookies = {}
collection_name = "test"
collection_id = ""
userid = ""

#for add product to collection
sourceId = ""
uniqueCode = ""
type = ""
isDeleted=""
feedCreateTime =""

def pushalert(metric_name="test", metric_value="-1", job_name="job_name"):
    result=client.push_data(
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
    # load page
    try:
        driver.get('https://creator.voila.love')
    except Exception as e:
        pushalert("voila_addcollection_status", "1", "voila_addcollection")
        # exit()
    #等待页面加载
    time.sleep(seconds)

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"app\"]/div/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/input"))).send_keys(USERNAME)
    except Exception as e:
        pushalert("voila_addcollection_status", "2", "voila_addcollection")
        # exit()
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div[2]/div[1]/div[2]/form/div[2]/div/div[1]/input"))).send_keys(PASSWORD)
    except Exception as e:
        pushalert("voila_addcollection_status", "3", "voila_addcollection")
        # exit()
    #click "SIGN IN" button
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#app > div > div.container__main > div.login > div.login-form > form > div:nth-child(3) > div > button'))).click()
    except Exception as e:
        pushalert("voila_addcollection_status", "4", "voila_addcollection")
        # exit()

    #sleep必须要有，否则cookies获取不全
    time.sleep(seconds)

    cookies = driver.get_cookies()
    for c in cookies:
        requests_cookies[c['name']] = c['value']

    if requests_cookies:
        return True
    else:
        # status=5 get cookies failed
        pushalert("voila_addcollection_status", "5", "voila_addcollection")

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
        response=requests.post(url, cookies=requests_cookies, headers=headers, json=data)
    except Exception as e:
        pushalert("voila_addcollection_status", '7', "voila_addcollection")

    response_data = json.loads(response.text)
    collection_id=json.loads(response.text).get("id")

    if response.status_code == 200 and collection_id is True:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Generate collection id successfully", collection_id)
    else:
        pushalert("voila_add_collection_status", "8", "voila_add_collection")


def bind_collection_id_name():
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
    try:
        response=requests.post(url, cookies=requests_cookies, headers=headers, json=data)
    except Exception as e:
        pushalert("voila_addcollection_status", '9', "voila_addcollection")

    response_collection_id = json.loads(response.text).get("id")
    response_collection_name = json.loads(response.text).get("name")

    if response.status_code == 200 and response_collection_id == response_collection_id and response_collection_name == collection_name:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "bind collection id and name successfully", response_collection_id, response_collection_name )
    else:
        pushalert("voila_add_collection_status", "10", "voila_add_collection")

def get_userid():

    global userid

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": "macOS",
        "content-type": "application/json"
    }

    try:
        response = requests.get('https://creator.voila.love/_/voila/v1/who',cookies=requests_cookies,headers=headers)
        response_data = json.loads(response.text)

        userid = response_data.get('id')
    except Exception as e:
        pushalert("voila_add_collection_status", "12", "voila_add_collection")

    if userid is None or response.status_code != 200:
        pushalert("voila_add_collection_status", "13", "voila_add_collection")

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

    url = "https://creator.voila.love/_/voila/v2/feeds?count=15&cursor=&userId=" + userid + "&isRetProduct=true&isSharePage=false&collectionId=" + collection_id

    try:
       list_products_response = requests.get(url, cookies=requests_cookies, headers=headers)
       list_products_response_data = json.loads(list_products_response.text).get("data")

       #取第5个post或product添加
       uniqueCode = list_products_response_data[4].get('id')
       sourceId = list_products_response_data[4].get('data').get('id')
       type = list_products_response_data[4].get('type')
       isDeleted = list_products_response_data[4].get('data').get('products')[1].get('sku').get('isDeleted')
       feedCreateTime = time.strftime("%Y-%m-%d %H:%M", time.localtime(int(list_products_response_data[4].get('data').get('products')[1].get('sku').get('createdUtc'))))
    except Exception as e:
        pushalert("voila_addcollection_status", '14', "voila_addcollection")
        print("e is: ", e)

    if list_products_response.status_code == 200 and  uniqueCode is True and sourceId is True and type is True and isDeleted == 0 and feedCreateTime is True:
        print("list products successfully")
    else:
        pushalert("voila_add_collection_status", "15", "voila_add_collection")


def add_product_to_collection():
    # print("uniqueCode is ", uniqueCode)
    # print("sourceId is ", sourceId)
    # print("type is ", type)
    # print("isDeleted is ", isDeleted)
    # print("feedCreateTime is ", feedCreateTime)
    # print("collection_id is ", collection_id)

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
        "data":[
            {
                "type": type,
                "sourceId": sourceId,
                "isDeleted": isDeleted,
                "uniqueCode": uniqueCode,
                "feedCreateTime": feedCreateTime
            }
        ]
    }

    print("data is :", data)

    url = "https://creator.voila.love/_/voila/v2/feeds/collection/content"

    try:
        response=requests.post(url, cookies=requests_cookies, headers=headers, json=data)
    except Exception as e:
        pushalert("voila_addcollection_status", '7', "voila_addcollection")

    add_product_to_collection_response_data=json.loads(response.text)
    print("add_product_to_collection_response_data is: ", add_product_to_collection_response_data)

    # if response.status_code == 200 and collection_id is True:
    #     print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Generate collection id successfully", collection_id)
    # else:
    #     pushalert("voila_add_collection_status", "8", "voila_add_collection")


def list_collection():
    pass

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

    url = "https://creator.voila.love/_/voila/v2/feeds/collection/" + collection_id
    try:
        delete_response=requests.delete(url, cookies=requests_cookies, headers=headers)
    except Exception as e:
        pushalert("voila_addcollection_status", '13', "voila_addcollection")
        print("e is: ", e)

    if delete_response.status_code == 200:
        print("delete collection successfully: ", collection_id, collection_name)
    else:
        pushalert("delete_collection_status", "1" ,"deleete_collection")

if __name__ == "__main__":
    login_get_cookies()
    generate_collection_id()
    bind_collection_id_name()
    # time.sleep(20)
    get_userid()
    list_products()
    add_product_to_collection()
    list_collection()
    delete_collection()
    #
    driver.quit()
