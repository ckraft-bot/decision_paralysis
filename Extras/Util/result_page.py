from Util.base_page import BasePage
from selenium.webdriver.support.ui import Select

class ResultPage(BasePage):
    
    # locators
    PRODUCTS_LINK = "//a[@class='product-title-link line-clamp line-clamp-2 truncate-title'][1]"
    PRODUCTS_PRICE = "//span[@class='price-main-block'][1]"
    SORT_SELECT = "//div[@class='desktop-bar-sort']//select"


    def __init__(self, driver):
        super().__init__(driver)

    def sort_by_price(self):
        sort_select = Select(self.driver.find_element_by_xpath(self.SORT_SELECT))
        sort_select.select_by_visible_text('Price: low to high')

    def choose_product(self, max_price):
        self.sort_by_price()
        if not max_price:
            product = self.driver.find_element_by_xpath(self.PRODUCTS_LINK)
            product.click()
        else:
            price = self.driver.find_element_by_xpath(self.PRODUCTS_PRICE)
            f_price = price.text.strip()[1:4]
            if float(f_price) <= float(max_price):
                product = self.driver.find_element_by_xpath(self.PRODUCTS_LINK)
                product.click()
                return True
            else:
                return False