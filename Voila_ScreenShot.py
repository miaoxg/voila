#!/usr/local/bin/python3.9
# coding=utf-8
from __future__ import division
import time
from selenium import webdriver
import random
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from pushgateway_client import client
import os
from concurrent.futures import ThreadPoolExecutor

download_path = os.popen("pwd").read().split('\n')[0] + '/vip_screenshot/'
# os.system("mkdir -p " + "download_path" + " && find download_path -type f -ctime +7 -name \"*.png\" -exec rm {} \;")
os.system(
    "mkdir -p " + download_path + " && find " + download_path + " -type f -ctime +7 -name \"*.png\" -exec rm {} \;")

md5sum_result = []

seconds = random.randint(10, 15)
chrome_options = Options()
# 不加载ui
chrome_options.add_argument("--headless")

# 启动要放入函数中，否则while true再执行时因为前面已经driver.quit()浏览器已退出，无法再通过chromedriver发起新的链接
# driver = webdriver.Chrome(options=chrome_options,service=Service(ChromeDriverManager().install()))
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver = None
# 可控制窗口大小
# driver.maximize_window()
wait = WebDriverWait(driver, 20)

# blogger=['tiamcintosh','sheldon']
# blogger=['tiamcintosh']

# 订单量最多的10个博主
blogger = ['tiamcintosh', 'sheldon', 'clairesmanson', 'shaynehydn1', 'Mommaneedssomegrace', 'Simpleandsweetblog',
           'oksarahpan', 'laurajfarr', 'itsjing', 'sarahbelleelizabeth']


def pushalert(status="-1"):
    result = client.push_data(
        url="pushgateway.voiladev.xyz:32684",
        metric_name="voila_screenshot_status",
        metric_value=status,
        job_name="voila_screenshot",
        timeout=5,
        labels={
            "env": "prod"
        }
    )


def get_md5sum():
    # def get_md5sum(vip):
    vipa_screenshot_list = {}
    vipb_screenshot_list = {}

    # 启动要放入函数中，否则while true再执行时因为前面已经driver.quit()浏览器已退出，无法再通过chromedriver发起新的链接
    driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))

    for vipa in blogger:
        try:
            print("vipa is: ", vipa)
            url = 'https://voila.love/' + vipa + '/'
            print("url is:", url)
            driver.get(url)
        except Exception as e:
            pushalert("1")
        # 等待页面加载
        time.sleep(seconds)

        now = str(int(time.time()))
        #        driver.get_screenshot_as_file(dir_path + "/vip_screenshot" + vipa + now + ".png")
        #        vip_md5sum=os.popen("md5sum ./vip_screenshot" + vipa + now + ".png | awk '{print $1}'").read().strip('\n')
        driver.get_screenshot_as_file(download_path + vipa + now + ".png")
        vip_md5sum = os.popen("md5sum " + download_path + vipa + now + ".png | awk '{print $1}'").read().strip('\n')
        vipa_screenshot_list[vipa] = [now, vip_md5sum]

    # 生成快照的两次间隔
    time.sleep(86400)

    for vipb in blogger:
        try:
            print("vipb is ", vipb)
            url = 'https://voila.love/' + vipb + '/'
            print("url is:", url)
            driver.get(url)
        except Exception as e:
            pushalert("1")
        # 等待页面加载
        time.sleep(seconds)

        now = str(int(time.time()))
        driver.get_screenshot_as_file("./vip_screenshot" + vipb + now + ".png")
        vipb_md5sum = os.popen("md5sum ./vip_screenshot" + vipb + now + ".png | awk '{print $1}'").read().strip('\n')
        vipb_screenshot_list[vipb] = [now, vipb_md5sum]

    print("vipa_screenshot_list is: ", vipa_screenshot_list)
    print("vipb_screenshot_list is: ", vipb_screenshot_list)

    for vip in blogger:
        print("vip is: ", vip)
        print("vipa_screenshot_list.get(vip) is: ", vipa_screenshot_list.get(vip))
        print("vipa_screenshot_list.get(vip)[1] is: ", vipa_screenshot_list.get(vip)[1])
        print("vipb_screenshot_list.get(vip) is: ", vipb_screenshot_list.get(vip))
        print("vipb_screenshot_list.get(vip)[1] is: ", vipb_screenshot_list.get(vip)[1])
        if vipa_screenshot_list.get(vip)[1] == vipb_screenshot_list.get(vip)[1]:
            md5sum_result.append("same")
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "get result:" + vip + '_same')
        else:
            md5sum_result.append("different")
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "get result:" + vip + '_different')

    print(md5sum_result)

    # 如果成帖子未变更的博主数量占比超过6成即异常
    if md5sum_result.count('same') > len(blogger) * 0.6:
        pushalert("2")
    else:
        pushalert("0")

    time.sleep(120)
    driver.close()


while True:
    get_md5sum()

# print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),md5sum_result)
