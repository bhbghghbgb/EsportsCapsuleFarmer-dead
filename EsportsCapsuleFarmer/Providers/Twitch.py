import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
#<div class="click-to-unmute__container"><div class="Layout-sc-1xcs6mc-0 MIEJo player-overlay-background player-overlay-background--darkness-5"><figure class="ScFigure-sc-a7mori-0 gJgjXg tw-svg"><svg width="35" height="35" viewBox="0 0 20 20" fill="currentColor"><path d="m5 7 4.146-4.146a.5.5 0 0 1 .854.353v13.586a.5.5 0 0 1-.854.353L5 13H4a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2h1zm7 1.414L13.414 7l1.623 1.623L16.66 7l1.414 1.414-1.623 1.623 1.623 1.623-1.414 1.414-1.623-1.623-1.623 1.623L12 11.66l1.623-1.623L12 8.414z"></path></svg></figure><div class="Layout-sc-1xcs6mc-0 fVcPlA"><p class="CoreText-sc-1txzju1-0 iuqcsF">Click to unmute</p></div></div></div>
class Twitch:
    def __init__(self, log, driver) -> None:
        self.driver = driver
        self.log = log

    def setQuality(self):
        """
        Sets the Twitch player quality to the last setting in the video quality list.
        This corresponds to setting the video quality to the lowest value.
        """
        wait = WebDriverWait(self.driver, 10)
        try:
            wait.until(ec.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[title=Twitch]")))
        except TimeoutException:
            self.log.warning("Twitch player does not exist")
            raise
        else:
            settingsButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "button[data-a-target=player-settings-button]")))
            self.driver.execute_script("arguments[0].click();", settingsButton)
            qualityButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "button[data-a-target=player-settings-menu-item-quality]")))
            self.driver.execute_script("arguments[0].click();", qualityButton)
            options = wait.until(ec.presence_of_all_elements_located((By.CSS_SELECTOR, "input[data-a-target=tw-radio]")))
            self.driver.execute_script("arguments[0].click();", options[-1])
            self.log.debug("Twitch quality set successfully")
            time.sleep(1)
            for i in range(1, 6):
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                self.driver.switch_to.default_content()
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                wait.until(ec.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[title=Twitch]")))
                time.sleep(2)
                try:
                    playButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "button[data-a-target=player-play-pause-button]")))
                except TimeoutException:
                    self.log.error(f"Twitch play button not found {i}")
                    continue
                self.log.debug(f"Twitch play button key: {playButton.get_attribute('data-a-player-state')} | {playButton.get_attribute('aria-label')}")
                if playButton.get_attribute("data-a-player-state").lower().startswith("playing") or playButton.get_attribute("aria-label").lower().startswith("pause"):
                    self.log.debug(f"Twitch already playing {i}")
                    break
                self.log.debug(f"Twitch trying to play by clicking {i}")
                self.driver.execute_script("arguments[0].click();", playButton)
                time.sleep(2)
                if playButton.get_attribute("data-a-player-state").lower().startswith("paused") or playButton.get_attribute("aria-label").lower().startswith("play"):
                    self.log.debug(f"Twitch trying to play by key SPACE {i}")
                    ActionChains(self.driver).send_keys(Keys.SPACE).perform()
                    time.sleep(2)
                    if playButton.get_attribute("data-a-player-state").lower().startswith("paused") or playButton.get_attribute("aria-label").lower().startswith("play"):
                        self.log.debug(f"Twitch trying to play by key K {i}")
                        ActionChains(self.driver).send_keys("k").perform()
            else:
                self.log.warning("Twitch failed to play a tab")
            for i in range(1, 6):
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                self.driver.switch_to.default_content()
                ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
                wait.until(ec.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[title=Twitch]")))
                time.sleep(2)
                speakerButton = wait.until(ec.presence_of_element_located((By.CSS_SELECTOR, "button[data-a-target=player-mute-unmute-button]")))
                self.log.debug(f"Twitch speaker button key: {speakerButton.get_attribute('aria-label')}")
                if speakerButton.get_attribute("aria-label").lower().startswith("mute"):
                    self.log.debug("Twitch unmuted")
                    break
                self.log.debug(f"Twitch trying to unmute by clicking {i}")
                self.driver.execute_script("arguments[0].click();", speakerButton)
                time.sleep(2)
                if speakerButton.get_attribute("aria-label").lower().startswith("unmute"):
                    self.log.debug(f"Twitch trying to unmute by key M {i}")
                    ActionChains(self.driver).send_keys("m").perform()
            else:
                self.log.warning(f"Twitch failed to unmute a tab")
        finally:
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            self.driver.switch_to.default_content()
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
