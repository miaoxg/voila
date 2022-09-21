#!/usr/local/bin/python3.9
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
        metric_name="bio_login_status",
        metric_value=status,
        job_name="bio_login",
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
        pushalert("1")
    # 等待页面加载
    time.sleep(seconds)

    try:
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[@id=\"app\"]/div/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/input"))).send_keys(USERNAME)
        time.sleep(seconds)
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div/div/div[2]/div[1]/div[2]/form/div[2]/div/div[1]/input"))).send_keys(PASSWORD)
        time.sleep(seconds)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                               '#app > div > div.container__main > div.login > div.login-form > form > div:nth-child(3) > div > button'))).click()
        time.sleep(seconds)
    except Exception as e:
        pushalert("2")

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


def get_user_info():
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": "macOS",
        "content-type": "application/json"
    }

    try:
        response = requests.get('https://creator.voila.love/_/voila/v1/who', cookies=requests_cookies, headers=headers)
        response_data = json.loads(response.text)
        email = re.findall('email\': [\'|\"](.+?)[\'|\"],', str(response_data))
        if email[0] == "xiao20090813xiao@163.com" and response.status_code == 200:
            pushalert("0")
    except Exception as e:
        pushalert("3")


if __name__ == "__main__":
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "Begin#" * 10)
    requests_cookies = {}
    login_get_cookies()
    while True:
        get_user_info()
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "end#" * 10)
        time.sleep(30)
