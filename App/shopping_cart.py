import sys
import os
from selenium.webdriver import Chrome, Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger
import time
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

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

class SignInPage:
    def __init__(self, driver):
        self.driver = driver

    def goto(self):
        logger.info("Navigating to the sign-in page.")
        
        # Wait until the "hf-account-flyout" element is clickable
        try:
            account_flyout = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "hf-account-flyout"))
            )
            account_flyout.click()
        except Exception as e:
            logger.error(f"Error navigating to sign-in page: {e}")
            raise

    def sign_in(self, WALMART_USERNAME, WALMART_PASSWORD):
        try:
            # Wait for the email input to be visible
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "sign-in-email"))
            )
            self.driver.find_element(By.ID, "sign-in-email").send_keys(WALMART_USERNAME)
            self.driver.find_element(By.ID, "sign-in-password").send_keys(WALMART_PASSWORD)
            self.driver.find_element(By.ID, "sign-in-button").click()
        except Exception as e:
            logger.error(f"Error signing in: {e}")
            raise

    def search(self, search_query):
        search_box = self.driver.find_element(By.ID, "global-search-input")
        search_box.clear()
        search_box.send_keys(search_query)
        search_box.submit()


class ResultPage:
    def __init__(self, driver):
        self.driver = driver

    def choose_product(self, max_price):
        try:
            products = self.driver.find_elements(By.CLASS_NAME, "product-tile")  # Update with correct element
            for product in products:
                price = float(product.find_element(By.CLASS_NAME, "price").text.replace('$', ''))  # Update with correct element
                if price <= float(max_price):
                    product.click()  # Click the product
                    return True
            return False
        except Exception as e:
            logger.error(f"Error choosing product: {e}")
            return False


class ProductPage:
    def __init__(self, driver):
        self.driver = driver

    def add_to_cart(self, quantity):
        try:
            quantity_field = self.driver.find_element(By.ID, "quantity")  # Update with correct element
            quantity_field.clear()
            quantity_field.send_keys(quantity)
            self.driver.find_element(By.ID, "add-to-cart").click()  # Update with correct element
        except Exception as e:
            logger.error(f"Error adding product to cart: {e}")


class CartPage:
    def __init__(self, driver):
        self.driver = driver

    def goto(self):
        self.driver.find_element(By.ID, "hf-cart-flyout").click()  # Update with correct element

    def clear_cart(self):
        try:
            cart_items = self.driver.find_elements(By.CLASS_NAME, "cart-item")  # Update with correct element
            for item in cart_items:
                item.find_element(By.CLASS_NAME, "remove-item").click()  # Update with correct element
            logger.info("Cart cleared.")
        except Exception as e:
            logger.error(f"Error clearing cart: {e}")

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
        cart.take_screenshot()
    except Exception as e:
        logger.exception("Unhandled exception during automation.")
    finally:
        close_browser(driver)
        logger.info("Automation script finished.")


if __name__ == '__main__':
    main()
