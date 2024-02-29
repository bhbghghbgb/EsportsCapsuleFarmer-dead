# TODO: <iframe id="video-player-afreeca-vod-1679743316825" frameborder="0" allowfullscreen="1" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" title="AfreecaTV Player" width="100%" height="100%" src="//play.afreecatv.com/ljl/direct?fromApi=1"></iframe>
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
class Youtube:
    def __init__(self, log, driver) -> None:
        self.driver = driver
        self.log = log

    def setYoutubeQuality(self):
        """
        Sets the Youtube player quality to the second last setting in the video quality list.
        This corresponds to setting the video quality to the lowest value.
        """
        self.log.debug("Assuming youtube player second")
        wait = WebDriverWait(self.driver, 10)
        try:
            wait.until(ec.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe#video-player-youtube")))
        except TimeoutException:
            self.log.info("Youtube player does not exist")
            self.log.critical("Cannot determine which type of stream this is")
        else:
            settingsButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "button.ytp-settings-button")))
            self.driver.execute_script("arguments[0].click();", settingsButton)
            qualityButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "div.ytp-panel-menu > div:last-child")))
            self.driver.execute_script("arguments[0].click();", qualityButton)
            qualityOptions = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "div.ytp-menuitem")))
            self.driver.execute_script("arguments[0].click();", qualityOptions[-2])
            self.log.debug("Youtube quality set successfully")
            time.sleep(1)
            for i in range(1, 6):
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                self.driver.switch_to.frame(self.driver.find_element_by_css_selector("iframe#video-player-youtube"))
                time.sleep(2)
                try:
                    playButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "button.ytp-play-button")))
                except TimeoutException:
                    self.log.error(f"Youtube play button not found {i}")
                    continue
                self.log.debug(f"Youtube play button key: {playButton.get_attribute('data-title-no-tooltip')}")
                if playButton.get_attribute("data-title-no-tooltip").lower().startswith("dừng"):
                    self.log.debug(f"Youtube already playing {i}")
                    break
                self.log.debug(f"Youtube trying to play by clicking {i}")
                self.driver.execute_script("arguments[0].click();", playButton)
                time.sleep(2)
                if playButton.get_attribute("data-title-no-tooltip").lower().startswith("phát"):
                    self.log.debug(f"Youtube trying to play by key SPACE {i}")
                    ActionChains(self.driver).send_keys(Keys.SPACE).perform()
                    time.sleep(2)
                    if playButton.get_attribute("data-title-no-tooltip").lower().startswith("phát"):
                        self.log.debug(f"Youtube trying to play by key K {i}")
                        ActionChains(self.driver).send_keys("k").perform()
            else:
                self.log.warning("Youtube failed to play a tab")
            for i in range(1, 6):
                time.sleep(2)
                try:
                    speakerButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "button.ytp-mute-button")))
                except TimeoutException:
                    self.log.error(f"Youtube speaker button not found {i}")
                    continue
                self.log.debug(f"Youtube speaker button key: {speakerButton.get_attribute('data-title-no-tooltip')}")
                if speakerButton.get_attribute("data-title-no-tooltip").lower().startswith("tắt"):
                    self.log.debug(f"Youtube unmuted {i}")
                    break
                self.log.debug(f"Youtube trying to unmute by clicking {i}")
                self.driver.execute_script("arguments[0].click();", speakerButton)
                time.sleep(2)
                if speakerButton.get_attribute("data-title-no-tooltip").lower().startswith("bật"):
                    self.log.debug(f"Youtube trying to unmute by key M {i}")
                    ActionChains(self.driver).send_keys("m").perform()
            else:
                self.log.warning("Youtube failed to unmute a tab")
        finally:
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            self.driver.switch_to.default_content()
