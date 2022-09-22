#!/usr/local/bin/python3.9
import random
import time

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
PRODUCTWORD = 'red'  # 搜索商品关键词

seconds = random.randint(1, 2)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--disable-blink-features=AutomationControlled')  ## to avoid getting detected
driver = webdriver.Chrome(options=chrome_options, service=Service(ChromeDriverManager().install()))
# driver.maximize_window()
wait = WebDriverWait(driver, 10)

driver.get('https://creator.voila.love')
# 等待页面加载
time.sleep(seconds)

wait.until(EC.presence_of_element_located(
    (By.XPATH, "//*[@id=\"app\"]/div/div[2]/div[1]/div[2]/form/div[1]/div/div[1]/input"))).send_keys(USERNAME)
wait.until(EC.presence_of_element_located(
    (By.XPATH, "/html/body/div/div/div[2]/div[1]/div[2]/form/div[2]/div/div[1]/input"))).send_keys(PASSWORD)
# click "SIGN IN" button
wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                       '#app > div > div.container__main > div.login > div.login-form > form > div:nth-child(3) > div > button'))).click()
# click "Porduct" button
wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//*[@id=\"app\"]/div[1]/div[1]/div/div/div/div[1]/ul/li[2]/div/span"))).click()
wait.until(EC.element_to_be_clickable(
    (By.XPATH, "/html/body/div[1]/div[1]/div[3]/div/div[1]/div[2]/div[1]/div/div/input"))).click()
time.sleep(15)
# send "red" keyword to search
wait.until(EC.element_to_be_clickable(
    (By.XPATH, "/html/body/div[1]/div[1]/div[3]/div/div[1]/div[2]/div[1]/div/div/input"))).send_keys(PRODUCTWORD)
wait.until(EC.element_to_be_clickable(
    (By.XPATH, "/html/body/div[1]/div[1]/div[3]/div/div[1]/div[2]/div/div/div[1]/img[2]"))).click()
time.sleep(seconds)

dr = driver.find_elements(by=By.XPATH, value="//div[@class='_product__box_yov82_1']")
for son in dr:
    productData = {'brand': '', 'title': '', 'price': '', 'earning': '', 'retailer': ''}
    # brand_element = son.find_elements(by=By.XPATH,value=".//div[@class='_product__item_yov82_8']")
    brand_element = son.find_elements(by=By.XPATH, value=".//div")
    if brand_element:
        # productData['brand']=(brand_element[5].get_attribute('class')) #获取到的是该class的取值
        productData['brand'] = (brand_element[6].text)
        productData['title'] = (brand_element[7].text)
        productData['price'] = (brand_element[8].text)
        productData['earning'] = (brand_element[9].text)
        productData['retailer'] = (brand_element[10].text)
        print("productData is:", productData)
        if productData['brand'] and productData['title'] and productData['price'] and productData['earning'] and \
                productData['retailer']:
            print("ProductSearch:True")
        else:
            print("ProductSearch:Wrong")

driver.quit()
