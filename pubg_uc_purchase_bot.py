import random
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import Proxy, ProxyType


def close_popup(driver):
    pass


def sign_in(driver, email, password):
    pass

def choose_iraq(driver):
    pass


def send_player_id(driver, player_id):
    pass

def choose_amount(driver):
    pass

def choose_mobile_payment(driver):
    pass

def agree_to_terms(driver):
    pass

def close_cookies_popup(driver):
    try:
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '.eea-pop .close-btn')))
        driver.find_element(By.CSS_SELECTOR, '.eea-pop .close-btn').click()
        # # click accept all cookies
        # driver.find_element(By.CSS_SELECTOR, '.pop-content > div:nth-child(4) > div:nth-child(1)').click()
        time.sleep(1)
    except:
        pass


def send_payment_code(driver, code):
    pass


def verify_payment(driver):
    try:
        WebDriverWait(driver, 40).until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#payment_status')))
        # if driver.find_element(By.CSS_SELECTOR, '#payment_status').text == 'تمت عملية الشراء بنجاح':
        if driver.find_element(By.CSS_SELECTOR, '#payment_status').text.find('بنجاح') != -1:
            return 'success'
        else:
            return 'invalid'
    except Exception as e:
        return 'error'


def close_popup_after_first_purchase(driver):
    pass


def open_pubg_pay_page(driver):
    driver.get('https://www.pubgmobile.com/pay/')
    main_iframe = driver.find_element(By.CSS_SELECTOR, 'iframe')
    driver.switch_to.frame(main_iframe)
    time.sleep(1)


def purchase(driver, code):
    pass


def click_back(driver):
    pass

