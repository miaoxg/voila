#!/usr/bin/python3
import json
import random
import re
import time

import requests
# from pushgateway_client import CollectorRegistry,Gauge,push_to_gateway,client
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
# total_statuscode_list = []
# total_title_list = []
requests_cookies = {}

seconds = random.randint(1, 2)
chrome_options = Options()
# 不加载ui
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))
# 可控制窗口大小
# driver.maximize_window()
wait = WebDriverWait(driver, 10)


# define function for pushing alerts to prometheus
def pushalert(status="-1"):
    result = client.push_data(
        url="pushgateway.voiladev.xyz:32684",
        metric_name="creator_search_product_status",
        metric_value=status,
        job_name="creator_search_product",
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
        pushalert("4")
        # exit()
    # 等待页面加载
    time.sleep(seconds)

    try:
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[@id=\"app\"]/div/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/input"))).send_keys(USERNAME)
    except Exception as e:
        pushalert("6")
        # exit()
    try:
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div/div/div[2]/div[1]/div[2]/form/div[2]/div/div[1]/input"))).send_keys(PASSWORD)
    except Exception as e:
        pushalert("7")
        # exit()
    # click "SIGN IN" button
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                               '#app > div > div.container__main > div.login > div.login-form > form > div:nth-child(3) > div > button'))).click()
    except Exception as e:
        pushalert("1")
        # exit()

    # sleep必须要有，否则cookies获取不全
    time.sleep(seconds)

    cookies = driver.get_cookies()
    for c in cookies:
        requests_cookies[c['name']] = c['value']

    if requests_cookies:
        return True
    else:
        # status=2 get cookies failed
        pushalert("2")
    driver.close()


def search_product(query_word="blue"):
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": "macOS",
        "content-type": "application/json"
    }

    data = {
        "query": query_word,
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
        response_data = json.loads(response.text)
        title_list = re.findall('title\': [\'|\"](.+?)[\'|\"],', str(response_data))
        for i in title_list:
            total_title_list.append(i)
        total_statuscode_list.append(response.status_code)
    except Exception as e:
        pushalert("5")

    # if response.status_code != 200:
    #     pushalert("5")
    # exit()
    # response_data = json.loads(response.text)

    # title_list = re.findall('title\': \'(.+?)\',',str(response_data))
    # title_list = re.findall('title\': [\'|\"](.+?)[\'|\"],',str(response_data))
    # print(query_word,title_list)

    # for i in title_list:
    #     total_title_list.append(i)
    # # for j in list(str(response.status_code)):
    # total_statuscode_list.append(response.status_code)


if __name__ == "__main__":
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Begin#" * 10)
    login_get_cookies()
    while True:
        total_statuscode_list = []
        total_title_list = []
        for i in PRODUCTWORD:
            search_product(i)
        print("total_statuscode_list is:", total_statuscode_list)
        print("total_title_list is:", total_title_list)
        print("len(total_statuscode_list) is:", len(total_statuscode_list))
        print("len(total_title_list) is:", len(total_title_list))
        if total_statuscode_list.count(200) == len(PRODUCTWORD) and len(total_title_list) >= (
                len(PRODUCTWORD) - 1) * 10 and len(PRODUCTWORD) <= len(PRODUCTWORD) * 10:
            pushalert("0")
        else:
            pushalert("3")
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "end#" * 10)
