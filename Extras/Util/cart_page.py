from Util.base_page import BasePage

class CartPage(BasePage):

    # locators
    REMOVE_BTN = "//button[@class='button button--link']//span[contains(text(), 'Remove')]"

    def __init__(self, driver):
        super().__init__(driver)

    def goto(self):
        self.goto_cart()

    def clear_cart(self):
        items = self.driver.find_elements_by_xpath(self.REMOVE_BTN)
        for item in items:
            
            max_tries = 3
            try_num = 0
            while try_num < max_tries:
                try:
                    item.click()
                    break
                except Exception as e:
                    try_num += 1
            else:
                raise Exception(f"failed to click on elements:: {locator} after {max_tries} tries")