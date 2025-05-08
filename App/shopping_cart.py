import sys
import os
from selenium.webdriver import Chrome, Firefox
from loguru import logger
import time

import Util
from Util.sign_in_page import SignInPage
from Util.result_page import ResultPage
from Util.product_page import ProductPage
from Util.cart_page import CartPage

# Configure loguru: custom format to stdout
logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {module}:{function}:{line} - {message}",
    level="INFO",
)

# Walmart credentials
WALMART_USERNAME = os.getenv("WALMART_USERNAME")
WALMART_PASSWORD = os.getenv("WALMART_PASSWORD")
if not WALMART_USERNAME or not WALMART_PASSWORD:
    logger.error("WALMART_USERNAME and WALMART_PASSWORD must be set in environment variables.")
    raise ValueError("WALMART_USERNAME and WALMART_PASSWORD must be set in environment variables.")

def get_grocery_list():
    logger.info("Fetching grocery list.")
    return [
        ["bananas", "5", "2.00"],
        ["orange juice", "1", "4.00"],
        ["milk", "1", "7.00"]
    ]

def open_browser(browser="chrome", wait_time=10):
    logger.info(f"Opening {browser} browser.")
    if browser == 'chrome':
        driver = Chrome()
    elif browser == 'firefox':
        driver = Firefox()
    else:
        logger.error(f"Unsupported browser: {browser}")
        raise Exception(f"Unsupported browser: {browser}")
    
    BASE_URL = 'https://www.walmart.com'
    driver.maximize_window()
    driver.get(BASE_URL)
    driver.implicitly_wait(wait_time)
    logger.info("Browser initialized and Walmart homepage loaded.")
    return driver

def close_browser(driver):
    logger.info("Closing browser.")
    driver.quit()

def main():
    logger.info("Automation script started.")
    driver = open_browser()
    sign_in = SignInPage(driver)
    res = ResultPage(driver)
    cart = CartPage(driver)
    product_page = ProductPage(driver)

    try:
        logger.info("Signing in.")
        sign_in.goto()
        sign_in.sign_in(WALMART_USERNAME, WALMART_PASSWORD)

        logger.info("Clearing shopping cart.")
        cart.goto()
        cart.clear_cart()

        grocery_list = get_grocery_list()

        for name, quantity, max_price in grocery_list:
            logger.info(f"Searching for '{name}' ({quantity}) under ${max_price}.")
            sign_in.search(name)
            r = res.choose_product(max_price)
            if r:
                logger.info(f"Adding '{name}' to cart.")
                product_page.add_to_cart(quantity)
            else:
                logger.warning(f"No product found for '{name}' under ${max_price}.")

        logger.info("Navigating to cart for screenshot.")
        cart.goto()
        sign_in.take_screenshot()
    except Exception as e:
        logger.exception("Unhandled exception during automation.")
    finally:
        close_browser(driver)
        logger.info("Automation script finished.")

if __name__ == '__main__':
    main()
