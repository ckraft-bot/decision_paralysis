from Util import header
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:

    def __init__(self, driver):
        self.driver = driver
        self.header = header

    def search(self, product_name):
        search_bar = self.driver.find_element(By.ID, self.header.SEARCH_BAR)
        search_bar.clear()
        search_bar.send_keys(product_name)
        self.driver.find_element(By.ID, self.header.SEARCH_BTN).click()

    def take_screenshot(self):
        try:
            root = os.path.dirname(os.path.dirname(__file__))
            screenshots_path = os.path.join(root, "screenshots")
            os.makedirs(screenshots_path, exist_ok=True)
        except OSError:
            pass

        self.driver.save_screenshot('screenshots/cart_screenshot.png')

    def goto_home(self):
        self.driver.find_element(By.ID, self.header.HOME_LINK).click()

    # def goto_account(self):
    #     self.driver.find_element(By.ID, self.header.ACCOUNT_BTN).click()

    def goto_account(self):
        wait = WebDriverWait(self.driver, 10)
        account_button = wait.until(EC.presence_of_element_located((By.ID, self.header.ACCOUNT_BTN)))
        account_button.click()

    def goto_sign_in_page(self):
        self.goto_account()
        self.driver.find_element(By.XPATH, self.header.SIGN_IN_BTN).click()

    def goto_cart(self):
        self.driver.find_element(By.ID, self.header.CART_LINK).click()