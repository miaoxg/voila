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

USERNAME = 'miaoxiaoguang'
PASSWORD = '#jzwC6gx'

requests_cookies={}
seconds = random.randint(5, 9)
chrome_options = Options()
#不加载ui
#chrome_options.add_argument("--headless --ignore-certificate-errors")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--ignore-certificate-errors")


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
        driver.get('https://ipa.voiladev.xyz/ipa/ui/')
    except Exception as e:
        print(e)
        # exit()
    #等待页面加载
    time.sleep(seconds)

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"username1\"]"))).send_keys(USERNAME)
    except Exception as e:
        # pushalert("voila_searchretailer_status","2","voila_searchretailer")
        # exit()
        print(e)
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"password2\"]"))).send_keys(PASSWORD)
    except Exception as e:
        # pushalert("voila_searchretailer_status","3","voila_searchretailer")
        # exit()
        print(e)
    #click "SIGN IN" button
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#simple-container > div > div > div.login-pf > div > div > div > div.col-sm-7.col-md-7.col-lg-6.login > div.row > div > button:nth-child(3)'))).click()
    except Exception as e:
        print(e)
        # pushalert("voila_searchretailer_status","4","voila_searchretailer")
        # exit()

    print("has login")

    #sleep必须要有，否则cookies获取不全
    time.sleep(10)

    cookies = driver.get_cookies()
    for c in cookies:
        requests_cookies[c['name']] = c['value']
    print("cookies is :", cookies)
    print(requests_cookies)

    if requests_cookies:
        return True
    else:
        # status=5 get cookies failed
        # pushalert("voila_searchretailer_status","5","voila_searchretailer")
        print(e)


def search_user():

    url="https://ipa.voiladev.xyz/ipa/session/json"
    headers={
        "Accept": "application/json, text/javascript, */*",
        "Accept-Language": "en,zh;q=0.9,zh-CN;q=0.8",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Origin": "https://ipa.voiladev.xyz",
        "Referer": "https://ipa.voiladev.xyz/ipa/ui/",
        "sec-ch-ua": "Google Chrome\";v=\"105\", \"Not)A;Brand\";v=\"8\", \"Chromium\";v=\"105\"",
        "sec-ch-ua-platform": "macOS"
    }

    data={
        "method": "user_find",
        "params": [
            [
                "zhangka"
            ],
            {
                "pkey_only": bool(1),
                "sizelimit": 0,
                "version": "2.240"
            }
        ]
    }

    response=requests.post(url,headers=headers,cookies=requests_cookies, json=data, verify=False)
    print("search_user response.text is :",response.text)

if __name__ == '__main__':
    login_get_cookies()
#    time.sleep(20)
    search_user()
    driver.quit()