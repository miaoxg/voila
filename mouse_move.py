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
from selenium.webdriver import ActionChains




driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
action = ActionChains(driver)
# sli_ele = driver.find_element_by_id('tcaptcha_drag_thumb')
# sli_ele = driver.find_element(By.ID, '#tcaptcha_drag_thumb')
# action.click_and_hold(sli_ele)

driver.get("https://voila.love/shaynehydn1")
# action.move_by_offset(500,0)
driver.execute_script('window.scrollBy(0, 1000)')
time.sleep(20)
driver.quit()

