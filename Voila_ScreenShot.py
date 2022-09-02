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


os.system("mkdir -p vip_screenshot && find vip_screenshot -type f -ctime +7 -name \"*.png\" -exec rm {} \;")

seconds = random.randint(2, 5)
chrome_options = Options()
#不加载ui
chrome_options.add_argument("--headless")

driver = webdriver.Chrome(options=chrome_options,service=Service(ChromeDriverManager().install()))
#可控制窗口大小
# driver.maximize_window()
wait = WebDriverWait(driver, 10)

#订单量最多的10个博主
blogger=['tiamcintosh','sheldon','clairesmanson','shaynehydn1','Mommaneedssomegrace','Simpleandsweetblog','oksarahpan','laurajfarr','itsjing','sarahbelleelizabeth']
# blogger=['tiamcintosh']

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

md5sum_result=[]


def get_md5sum(vip):
    try:
        url='https://voila.love/' + vip + '/'
        driver.get(url)
    except Exception as e:
        pushalert("1")
    # 等待页面加载
    time.sleep(seconds)

    num=0
    vip_screenshot_list=[]

    while num <2:
        now = str(int(time.time()))
        driver.get_screenshot_as_file("./vip_screenshot" + vip + now + ".png")
        vip_md5sum=os.popen("md5sum ./vip_screenshot" + vip + now + ".png | awk '{print $1}'").read().strip('\n')
        vip_screenshot_list.append(vip_md5sum)
        num+=1
        # 控制生成两次截图时间间隔
        time.sleep(10)
        if num == 2:
            if vip_screenshot_list[0]==vip_screenshot_list[1]:
                md5sum_result.append("same")
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "get result:" + vip + 'same' )
            else:
                md5sum_result.append("diffrent")
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), "get result:" + vip + 'diffrent' )

while True:

    with ThreadPoolExecutor() as pool:
        pool.map(get_md5sum,blogger)

    #如果成帖子未变更的博主数量占比超过6成即异常
    if md5sum_result.count('same') > len(blogger)*0.6:
        pushalert("2")
    else:
        pushalert("0")

    driver.quit()

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),md5sum_result)
