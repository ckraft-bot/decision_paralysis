
from Util.base_page import BasePage

class SignInPage(BasePage):

    # locators
    EMAIL_FIELD = "email"
    PASSWORD_FIELD = "password"
    SIGN_IN_BTN = "//button[@class='button m-margin-top text-inherit'][contains(text(),'Sign in')]"

    def __init__(self, driver):
        super().__init__(driver)

    def goto(self):
        self.goto_sign_in_page()

    def enter_email(self, email):
        self.driver.find_element_by_id(self.EMAIL_FIELD).send_keys(email)

    def enter_password(self, password):
        self.driver.find_element_by_id(self.PASSWORD_FIELD).send_keys(password)

    def sign_in(self, email, password):
        self.enter_email(email)
        self.enter_password(password)
        self.driver.find_element_by_xpath(self.SIGN_IN_BTN).click()
