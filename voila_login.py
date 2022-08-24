#!/usr/local/bin/python3.9
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import random
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager




USERNAME = 'xiao20090813xiao@163.com' # 输入账号
PASSWORD = 'sunsh1ne0sunny' # 输入密码
PRODUCTWORD = 'red' #搜索商品关键词

# 随机时间，防止过快被检测
seconds = random.randint(1, 2)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()
wait = WebDriverWait(driver, 10)

driver.get('https://creator.voila.love')
time.sleep(seconds) #等待页面加载

#通过classname进行判断，没判断对哪个是classname等着实习web知识吧
#if driver.find_element(by=By.CLASS_NAME,value='s-top-loginbtn'):
#    try:
#        driver.find_element(by=By.PARTIAL_LINK_TEXT,value='登录').click()
#except也没用对，需要重新看下
#    except selenium.common.exceptions.NoSuchElementException:
#        print('NoSuchElementException')

# time.sleep(seconds)
wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id=\"app\"]/div/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/input"))).send_keys(USERNAME)
# time.sleep(seconds)
# wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id="'<value>'"]"))).send_keys(PASSWORD)
wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div[2]/div[1]/div[2]/form/div[2]/div/div[1]/input"))).send_keys(PASSWORD)
#wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#\31 Xncqr_xlAQipC6_VibTE'))).send_keys(PASSWORD)
# time.sleep(seconds)
# 点击登录按钮
wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#app > div > div.container__main > div.login > div.login-form > form > div:nth-child(3) > div > button'))).click()
# time.sleep(seconds)

wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id=\"app\"]/div[1]/div[1]/div/div/div/div[1]/ul/li[2]/div/span"))).click()
wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div[3]/div/div[1]/div[2]/div[1]/div/div/input"))).click()
time.sleep(5)
wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div[3]/div/div[1]/div[2]/div[1]/div/div/input"))).send_keys(PRODUCTWORD)
wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div[3]/div/div[1]/div[2]/div/div/div[1]/img[2]"))).click()
time.sleep(15)
# wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#kw.s_ipt'))).send_keys('python')
# time.sleep(seconds)
# wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#su.btn.self-btn.bg.s_btn'))).click()
