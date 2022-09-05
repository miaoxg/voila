#!/usr/local/bin/python3.9
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
import re
# from pushgateway_client import CollectorRegistry,Gauge,push_to_gateway,client
from pushgateway_client import client

USERNAME = 'xiao20090813xiao@163.com'
PASSWORD = 'sunsh1ne0sunny'

requests_cookies={}
response_data = {}
seconds = random.randint(5, 9)
chrome_options = Options()
#不加载ui
chrome_options.add_argument("--headless")

# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

driver = webdriver.Chrome(options=chrome_options,service=Service(ChromeDriverManager().install()))
#可控制窗口大小
# driver.maximize_window()
wait = WebDriverWait(driver, 10)

def pushalert(metric_name="test",metric_value="-1",job_name="job_name"):
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
    # load page
    try:
        driver.get('https://creator.voila.love')
    except Exception as e:
        pushalert("voila_searchretailer_status","1","voila_searchretailer")
        # exit()
    #等待页面加载
    time.sleep(seconds)

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"app\"]/div/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/input"))).send_keys(USERNAME)
    except Exception as e:
        pushalert("voila_searchretailer_status","2","voila_searchretailer")
        # exit()
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div[2]/div[1]/div[2]/form/div[2]/div/div[1]/input"))).send_keys(PASSWORD)
    except Exception as e:
        pushalert("voila_searchretailer_status","3","voila_searchretailer")
        # exit()
    #click "SIGN IN" button
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#app > div > div.container__main > div.login > div.login-form > form > div:nth-child(3) > div > button'))).click()
    except Exception as e:
        pushalert("voila_searchretailer_status","4","voila_searchretailer")
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
        pushalert("voila_searchretailer_status","5","voila_searchretailer")

def search_retailers():

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": "macOS",
        "content-type": "application/json",
        "referer": "https://creator.voila.love/bio/"
    }

    data = {
        "query": "shoes",
        "sort":"SortTypeDefault",
        "page":1,
        "pageSize":1,
        "cursor":"",
        "filtration": "Filtration",
        "postId": 0,
        "attributes":[],
        "categoryIds":[],
        "brands":[],
        "retailers":[],
        "price":{"min":0,"max":0},
        "discount":[]
    }

    url = "https://creator.voila.love/_/voila/v2/retailers?page=1&count=30&sort=DEFAULT&weight=false&query=&isReturnAllData=true"
    try:
        response = requests.get(url,cookies=requests_cookies,headers=headers)
    except Exception as e:
        pushalert("voila_searchretailer_status","6","voila_searchretailer")
    repsonse_data=json.loads(response.text)
    total_retailers=repsonse_data['pagination'].get('total')
    # print("response.status_code is: ",response.status_code)
    # print("total_retailers: ",total_retailers)
    if response.status_code == 200 and total_retailers > 20000:
        pushalert("voila_searchretailer_status","0","voila_searchretailer")
    else:
        pushalert("voila_searchretailer_status","7","voila_searchretailer")

if __name__ == "__main__":
    login_get_cookies()
    while True:
        search_retailers()
        time.sleep(60)
    driver.quit()