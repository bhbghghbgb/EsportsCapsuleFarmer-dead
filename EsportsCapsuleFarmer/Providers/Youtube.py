import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
class Youtube:
    def __init__(self, log, driver) -> None:
        self.driver = driver
        self.log = log
        self.providerName = "Youtube"

    def setQuality(self):
        """
        Sets the Youtube player quality to the second last setting in the video quality list.
        This corresponds to setting the video quality to the lowest value.
        """
        wait = WebDriverWait(self.driver, 10, ignored_exceptions=(NoSuchElementException, StaleElementReferenceException))
        for i in range(1, 4):
            try:
                rootElement = wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, "#video-player")))
                ActionChains(self.driver).move_to_element(rootElement).perform()
                wait.until(ec.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe#video-player-youtube")))
                break
            except TimeoutException:
                self.log.warning(f"{self.providerName} player does not exist {i}")
                raise
            except StaleElementReferenceException:
                if i == 3:
                    self.log.critical(f"{self.providerName} frame keeps staling {i}")
                    raise  
                self.log.warning(f"{self.providerName} frame is stale, refreshing {i}")
                self.driver.refresh()
        playerElement = wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, "#movie_player > div.html5-video-container > video.video-stream.html5-main-video[src^=\"blob:https://www.youtube.com/\"]")))
        ActionChains(self.driver).move_to_element(playerElement).perform()
        settingsButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "#movie_player > div.ytp-chrome-bottom > div.ytp-chrome-controls > div.ytp-right-controls > button.ytp-button.ytp-settings-button")))
        ActionChains(self.driver).move_to_element(settingsButton).click().perform()
        settingsItems = wait.until(ec.visibility_of_all_elements_located((By.CSS_SELECTOR, "#ytp-id-18 > div.ytp-panel > div.ytp-panel-menu > div.ytp-menuitem")))
        qualityButton = next((stg for stg in settingsItems if stg.find_element(By.CSS_SELECTOR, "div.ytp-menuitem-label").text.lower().startswith("quality")), None)
        ActionChains(self.driver).move_to_element(qualityButton).click().perform()
        qualityItems = wait.until(ec.visibility_of_all_elements_located((By.CSS_SELECTOR, "#ytp-id-18 > div.ytp-panel > div.ytp-panel-menu > div.ytp-menuitem")))
        lowestQualilyItem = next((qly for qly in reversed(qualityItems) if not qly.find_element(By.CSS_SELECTOR, "div.ytp-menuitem-label").text.lower().startswith("auto")), None)
        ActionChains(self.driver).move_to_element(lowestQualilyItem).click().perform()
        self.log.debug(f"{self.providerName} quality set successfully")
        time.sleep(1)
        for i in range(1, 6):
            self.driver.switch_to.default_content()
            time.sleep(1)
            wait.until(ec.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe#video-player-youtube")))
            time.sleep(1)
            try:
                playButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "button.ytp-play-button")))
            except TimeoutException:
                self.log.error(f"{self.providerName} play button not found {i}")
                continue
            self.log.debug(f"{self.providerName} play button key: {playButton.get_attribute('data-title-no-tooltip')}")
            if playButton.get_attribute("data-title-no-tooltip").lower().startswith("pause"):
                self.log.debug(f"{self.providerName} already playing {i}")
                break
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            self.log.debug(f"{self.providerName} attempting video frame clicking {i}")
            playerElement = wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, "#movie_player > div.html5-video-container > video.video-stream.html5-main-video[src^=\"blob:https://www.youtube.com/\"]")))
            # sometimes there is a thumbnail shown instead of video, if so we need to click it first
            try:
                thumbnail = self.driver.find_element(By.CSS_SELECTOR, "#movie_player > div.ytp-cued-thumbnail-overlay")
                if "display: none" in thumbnail.get_attribute("style"): # thumbnail is already hidden
                    self.log.debug(f"{self.providerName} trying to play by clicking video element {i}")
                    ActionChains(self.driver).move_to_element(playerElement).click().perform()
                else:
                    self.log.debug(f"{self.providerName} trying to play by clicking thumbnail overlay {i}")
                    ActionChains(self.driver).move_to_element(thumbnail).click().perform()
            except NoSuchElementException:
                self.log.debug(f"{self.providerName} trying to play by clicking video element {i}")
                ActionChains(self.driver).move_to_element(playerElement).click().perform()
            time.sleep(1)
            if not playButton.get_attribute("data-title-no-tooltip").lower().startswith("play"):
                continue
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            self.log.debug(f"{self.providerName} trying to play by clicking play button {i}")
            ActionChains(self.driver).move_to_element(playButton).click().perform()
            time.sleep(1)
            if not playButton.get_attribute("data-title-no-tooltip").lower().startswith("play"):
                continue
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            self.log.debug(f"{self.providerName} trying to play by key SPACE {i}")
            ActionChains(self.driver).send_keys(Keys.SPACE).perform()
            time.sleep(1)
            if not playButton.get_attribute("data-title-no-tooltip").lower().startswith("play"):
                continue
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            self.log.debug(f"{self.providerName} trying to play by key K {i}")
            ActionChains(self.driver).send_keys("k").perform()
        else:
            self.log.warning("{self.providerName} failed to play a tab")

        for i in range(1, 6):
            self.driver.switch_to.default_content()
            time.sleep(1)
            wait.until(ec.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe#video-player-youtube")))
            time.sleep(1)
            ActionChains(self.driver).move_to_element(playerElement).perform()
            try:
                speakerButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "button.ytp-mute-button")))
            except TimeoutException:
                self.log.error(f"{self.providerName} speaker button not found {i}")
                continue
            self.log.debug(f"{self.providerName} speaker button key: {speakerButton.get_attribute('data-title-no-tooltip')}")
            if speakerButton.get_attribute("data-title-no-tooltip").lower().startswith("mute"):
                self.log.debug(f"{self.providerName} unmuted {i}")
                break
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            self.log.debug(f"{self.providerName} trying to unmute by clicking {i}")
            ActionChains(self.driver).move_to_element(speakerButton).click().perform()
            time.sleep(1)
            if not speakerButton.get_attribute("data-title-no-tooltip").lower().startswith("unmute"):
                continue
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            self.log.debug(f"{self.providerName} trying to unmute by key M {i}")
            ActionChains(self.driver).send_keys("m").perform()
        else:
            self.log.warning(f"{self.providerName} failed to unmute a tab")
        self.driver.switch_to.default_content()
        ActionChains(self.driver).send_keys(Keys.ESCAPE)
