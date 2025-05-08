import undetected_chromedriver as uc
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import os

# Walmart credentials
WALMART_USERNAME = os.getenv("WALMART_USERNAME")
WALMART_PASSWORD = os.getenv("WALMART_PASSWORD")
if not WALMART_USERNAME or not WALMART_PASSWORD:
    raise ValueError("WALMART_USERNAME and WALMART_PASSWORD must be set in environment variables.")

def get_grocery_list():
    return [
        ["bananas", "5", "2.00"],
        ["orange juice", "1", "4.00"],
        ["milk", "1", "7.00"]
    ]

def open_browser(wait_time=10):
    driver = Chrome()
    BASE_URL = 'https://www.walmart.com'
    driver.maximize_window()
    driver.get(BASE_URL)
    driver.implicitly_wait(wait_time)
    return driver


def close_browser(driver):
    driver.quit()


def sign_in(driver):
    driver.get("https://www.walmart.com/account/login")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(WALMART_USERNAME)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(WALMART_PASSWORD)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-automation-id='signin-submit-btn']"))
    ).click()
    time.sleep(5)  # Wait for login to finish


def clear_cart(driver):
    driver.get("https://www.walmart.com/cart")
    time.sleep(3)
    remove_buttons = driver.find_elements(By.XPATH, "//button[contains(text(),'Remove')]")
    for btn in remove_buttons:
        try:
            btn.click()
            time.sleep(1)
        except:
            continue


def search_item(driver, query):
    search_box = driver.find_element(By.NAME, "query")
    search_box.clear()
    search_box.send_keys(query)
    search_box.submit()
    time.sleep(3)


def choose_product_and_add_to_cart(driver, max_price, quantity):
    try:
        price_elements = driver.find_elements(By.CSS_SELECTOR, "span.price-characteristic")
        if not price_elements:
            return False
        first_add_button = driver.find_element(By.CSS_SELECTOR, "button.prod-ProductCTA--primary")
        first_add_button.click()
        time.sleep(1)
        return True
    except Exception as e:
        print(f"Failed to add item: {e}")
        return False


def take_screenshot(driver):
    driver.save_screenshot("cart_screenshot.png")


def main():
    driver = open_browser()
    try:
        sign_in(driver)
        clear_cart(driver)
        grocery_list = get_grocery_list()

        for name, quantity, max_price in grocery_list:
            search_item(driver, name)
            added = choose_product_and_add_to_cart(driver, max_price, quantity)
            if not added:
                print(f"Could not add {name} to cart")

        driver.get("https://www.walmart.com/cart")
        time.sleep(3)
        take_screenshot(driver)
    finally:
        close_browser(driver)


if __name__ == '__main__':
    main()
