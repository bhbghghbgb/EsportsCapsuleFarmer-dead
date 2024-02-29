from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException

class Rewards:
    def __init__(self, log, driver) -> None:
        self.log = log
        self.driver = driver
        pass

    def findRewardsCheckmark(self):
        """
        Checks if the user is currently eligible to receive rewards.
        """
        wait = WebDriverWait(self.driver, 15)
        try:
            self.driver.switch_to.default_content()
            wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "div[class=status-summary] g")))
        except TimeoutException:
            return False
        return True

    def checkRewards(self, url, retries=5):
        splitUrl = url.rsplit('/',1)
        match = splitUrl[1] if 1 < len(splitUrl) else "Match "
        if self.findRewardsCheckmark():
            self.log.info(f"{match} is eligible for rewards ✓")
            return True, match
        else:
            self.log.error(f"{match} is not eligible for rewards")
            return False, match
