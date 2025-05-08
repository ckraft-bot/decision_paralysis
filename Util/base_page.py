from Util import header
import os

class BasePage:

    def __init__(self, driver):
        self.driver = driver
        self.header = header

    def search(self, product_name):
        search_bar = self.driver.find_element_by_id(self.header.SEARCH_BAR)
        search_bar.clear()
        search_bar.send_keys(product_name)
        self.driver.find_element_by_id(self.header.SEARCH_BTN).click()

    def take_screenshot(self):
        try:
            root = os.path.dirname(os.path.dirname(__file__))
            screenshots_path = os.path.join(root, "screenshots")
            os.makedirs(screenshots_path)
        except OSError:
            pass

        self.driver.save_screenshot('screenshots/cart_screenshot.png')


    def goto_home(self):
        self.driver.find_element_by_id(self.header.HOME_LINK).click()

    def goto_account(self):
        self.driver.find_element_by_id(self.header.ACCOUNT_BTN).click()

    def goto_sign_in_page(self):
        self.goto_account()
        self.driver.find_element_by_xpath(self.header.SIGN_IN_BTN).click()

    def goto_cart(self):
        self.driver.find_element_by_id(self.header.CART_LINK).click()