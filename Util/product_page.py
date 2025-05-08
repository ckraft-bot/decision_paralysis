from Util.base_page import BasePage
from selenium.webdriver.support.ui import Select

class ProductPage(BasePage):

    # locators
    QUANTITY_SELECT = "//div//select[@class='field-input field-input--secondary']"
    ADD_TO_CART_BTN = "//div[@class='prod-product-cta-add-to-cart display-inline-block']//button[@type='button']"

    def __init__(self, driver):
        super().__init__(driver)

    def select_quantity(self, quantity):
        if quantity > 1 and len(self.driver.find_elements_by_xpath(self.QUANTITY_SELECT)) > 0:
            quantity_select = Select(self.driver.find_element_by_xpath(self.QUANTITY_SELECT))
            quantity_select.select_by_visible_text(str(quantity))

    def click_add_to_cart_btn(self):
        if len(self.driver.find_elements_by_xpath(self.ADD_TO_CART_BTN)) > 0:
            self.driver.find_element_by_xpath(self.ADD_TO_CART_BTN).click()

    def add_to_cart(self, quantity):
        if not quantity: quantity = 1
        self.select_quantity(quantity)
        self.click_add_to_cart_btn()