import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys

class LoginHandler: 
    def __init__(self, log, driver) -> None:
        self.log = log
        self.driver = driver

    def automaticLogIn(self, username, password):
        """
        Automatically logs into the user's account on the LoL Esports website.
        """
        self.driver.get("https://lolesports.com/schedule")
        time.sleep(2)

        self.log.info("Moving to login page")
        el = None
        try:
            el = self.driver.find_element(by=By.CSS_SELECTOR, value="a[data-riotbar-link-id=login]")
        except NoSuchElementException:
            self.log.error("Login button not found, might have logged in already")
            try:
                self.log.debug(f"Logged in name: {self.driver.find_element(by=By.CSS_SELECTOR, value='div.riotbar-summoner-name').text}")
                return
            except NoSuchElementException:
                self.log.critical("Log in failed")
                raise
        self.driver.execute_script("arguments[0].click();", el)

        self.log.info("Logging in")

        wait = WebDriverWait(self.driver, 20)
        usernameInput = None
        try:
            usernameInput = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "input[name=username]")))
        except TimeoutException:
            try:
                self.log.debug(f"Login process short-circuted, name: {self.driver.find_element(by=By.CSS_SELECTOR, value='div.riotbar-summoner-name').text}")
                return
            except NoSuchElementException as e:
                self.log.critical("Login failed")
                raise
        usernameInput.click()
        usernameInput.send_keys(Keys.CONTROL + "a")
        usernameInput.send_keys(Keys.BACKSPACE)
        usernameInput.clear()
        usernameInput.send_keys(username)
        passwordInput = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "input[name=password]")))
        passwordInput.click()
        passwordInput.send_keys(Keys.CONTROL + "a")
        passwordInput.send_keys(Keys.DELETE)
        passwordInput.clear()
        passwordInput.send_keys(password)
        if "mobile-checkbox--checked" not in wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, "div.mobile-checkbox.signin-checkbox"))).get_attribute("class"):
            rememberMeCheckbox = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "label.signin-checkbox.mobile-checkbox__label.mobile-checkbox")))
            rememberMeCheckbox.click()
        submitButton = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "button[type=submit]")))
        self.driver.execute_script("arguments[0].click();", submitButton)
        self.log.debug("Credentials submitted")

        # check for 2FA
        time.sleep(5)
        if len(self.driver.find_elements(by=By.CSS_SELECTOR, value="div.text__web-code")) > 0:
            self.insertTwoFactorCode()

        # wait until the login process finishes
        wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "div.riotbar-summoner-name")))

    def insertTwoFactorCode(self):
        wait = WebDriverWait(self.driver, 20)
        authText = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "h5.grid-panel__subtitle")))
        self.log.info(f'Enter 2FA code ({authText.text})')
        code = input('Code: ')
        codeInput = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "div.codefield__code--empty > div > input")))
        codeInput.send_keys(code)

        submitButton = wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, "button[type=submit]")))
        self.driver.execute_script("arguments[0].click();", submitButton)
        self.log.debug("Code submitted")
