#!/usr/local/bin/python3.9
# coding=utf-8
import time, datetime
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

USERNAME = 'miaoxiaoguang'
PASSWORD = 'M$@qenZ4#jzwC6gx'

seconds = random.randint(5, 9)
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))
wait = WebDriverWait(driver, 10)

requests_cookies = {}

blogger = "tiamcintosh"
creatorId = ""


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
        driver.get('https://dashboard.voila.love')
    except Exception as e:
        pushalert("voila_bloggerdata_status", "1", "voila_bloggerdata")
        # exit()
    #等待页面加载
    time.sleep(seconds)

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"loginUserName\"]"))).send_keys(USERNAME)
    except Exception as e:
        pushalert("voila_bloggerdata_status", "2", "voila_bloggerdata")
        # exit()
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"loginPassWord\"]"))).send_keys(PASSWORD)
    except Exception as e:
        pushalert("voila_bloggerdata_status", "3", "voila_bloggerdata")
        # exit()
    #click "SIGN IN" button
    try:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#btnLogin'))).click()
    except Exception as e:
        pushalert("voila_bloggerdata_status", "4", "voila_bloggerdata")
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
        pushalert("voila_bloggerdata_status", "5", "voila_bloggerdata")

def get_creatorId():

    global creatorId

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": "macOS",
        "content-type": "application/json; charset=UTF-8",
        "referer": "https://dashboard.voila.love/data/",
        "origin": "https://dashboard.voila.love",
        "authority": "dashboard.voila.love",
        "accept": "application/json, text/plain, */*"
    }

    data = {
        "query": {
            "and": {
                "values": [
                    {
                        "condition": {
                            "key": "info",
                            "operator": "ne",
                            "values": [
                                "platform",
                                "ldap"
                            ]
                        }
                    },
                    {
                        "condition": {
                            "key": "name",
                            "operator": "startswith",
                            "values": [
                                blogger
                            ]
                        }
                    }
                ]
            }
        },
        "sort": {
            "rules": [
                {
                    "key": "createTime",
                    "descending": bool(1)
                }
            ]
        },
        "start": 0,
        "size": 50
    }

    url = "https://dashboard.voila.love/_/security/identity/user/list"

    try:
        response = requests.post(url, json=data, headers=headers, cookies=requests_cookies)
        creatorId = json.loads(response.text).get("users")[0].get('id')
    except Exception as e:
        print(e)

    if response.status_code == 200 and creatorId:
        print("get creatorid successfully :", creatorId)
    else:
        print("response.status_code is :", response.status_code)
        print("creatorId is :", creatorId)

def get_bloggerdata():
    pv_list = []
    uv_list = []

    today = str(datetime.date.today()) + " 08:00:00"
    format_today = time.mktime(time.strptime(today, "%Y-%m-%d %H:%M:%S"))
    unix_today = str(format_today).split('.')[0]
    unix_7_day_before = str(format_today - 86400*7).split('.')[0]

    headers = {
        "authority": "dashboard.voila.love",
        "accept": "*/*",
        "accept-language": "en,zh;q=0.9,zh-CN;q=0.8",
        "content-type": "application/json",
        "referer": "https://dashboard.voila.love/creator/",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }

    try:
        url = "https://dashboard.voila.love/_/voila/v2/metrics/user/core?beginDate=" + unix_7_day_before + "&endDate=" + unix_today + "&creatorId=" + creatorId
        response = requests.get(url, cookies=requests_cookies , headers=headers)
        response_data = json.loads(response.text).get("daily")
    except Exception as e:
        print(e)

    for i in response_data:
        pv_list.append(i.get("pv"))
        uv_list.append(i.get("uv"))

    print(pv_list, uv_list)

    if response.status_code == 200 and pv_list.count(0) < 3 and uv_list.count(0) < 3 and len(uv_list) == 8 and len(pv_list) == 8:
        # pushalert()
        print("success")
    else:
        # pushalert()
        print("error")

if __name__ == "__main__":
    login_get_cookies()
    while True:
        get_creatorId()
        get_bloggerdata()
        time.sleep(10)
    driver.quit()