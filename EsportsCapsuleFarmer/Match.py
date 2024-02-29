import random
from selenium.webdriver.common.by import By
import time
from datetime import datetime, timedelta
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException, WebDriverException

from EsportsCapsuleFarmer.Rewards import Rewards
from EsportsCapsuleFarmer.Providers.Twitch import Twitch
from EsportsCapsuleFarmer.Providers.Youtube import Youtube

class Match:
    # Force Twitch player
    OVERRIDES = {
        "https://lolesports.com/live/lck_challengers_league":"https://lolesports.com/live/lck_challengers_league/lckcl",
        "https://lolesports.com/live/lpl":"https://lolesports.com/live/lpl/lpl",
        "https://lolesports.com/live/lck":"https://lolesports.com/live/lck/lck",
        "https://lolesports.com/live/lec":"https://lolesports.com/live/lec/lec",
        "https://lolesports.com/live/lcs":"https://lolesports.com/live/lcs/lcs",
        "https://lolesports.com/live/lco":"https://lolesports.com/live/lco/lco",
        "https://lolesports.com/live/cblol_academy":"https://lolesports.com/live/cblol_academy/cblol",
        "https://lolesports.com/live/cblol":"https://lolesports.com/live/cblol/cblol",
        "https://lolesports.com/live/lla":"https://lolesports.com/live/lla/lla",
        "https://lolesports.com/live/ljl-japan/ljl":"https://lolesports.com/live/ljl-japan/riotgamesjp",
        "https://lolesports.com/live/ljl-japan":"https://lolesports.com/live/ljl-japan/riotgamesjp",
        "https://lolesports.com/live/turkiye-sampiyonluk-ligi":"https://lolesports.com/live/turkiye-sampiyonluk-ligi/riotgamesturkish",
        "https://lolesports.com/live/cblol-brazil":"https://lolesports.com/live/cblol-brazil/cblol",
        "https://lolesports.com/live/pcs/lXLbvl3T_lc":"https://lolesports.com/live/pcs/lolpacific",
        "https://lolesports.com/live/pcs/d63-YWJVaY0":"https://lolesports.com/live/pcs/lolpacific",
        "https://lolesports.com/live/pcs/hGHa-VrIVbI":"https://lolesports.com/live/pcs/lolpacificTW",
        "https://lolesports.com/live/pcs/gH3NnNeJaMc":"https://lolesports.com/live/pcs/lolpacifichk",
        "https://lolesports.com/live/ljl_academy/ljl":"https://lolesports.com/live/ljl_academy/riotgamesjp",
        "https://lolesports.com/live/european-masters":"https://lolesports.com/live/european-masters/EUMasters",
        "https://lolesports.com/live/worlds":"https://lolesports.com/live/worlds/riotgames",
    }

    def __init__(self, log, driver) -> None:
        self.log = log
        self.driver = driver
        self.rewards = Rewards(log=log, driver=driver)
        self.twitch = Twitch(log=log, driver=driver)
        self.youtube = Youtube(log=log, driver=driver)

        self.currentWindows = {}
        self.originalWindow = self.driver.current_window_handle

    def watchForMatches(self, delay, delayRngs):
        self.currentWindows = {}
        self.originalWindow = self.driver.current_window_handle

        while True:
            self.driver.switch_to.window(self.originalWindow) # just to be sure
            time.sleep(2)
            self.driver.get("https://lolesports.com/schedule")
            time.sleep(5)
            liveMatches = self.getLiveMatches()
            self.log.info(f"There are {len(liveMatches)} matches live: {', '.join(liveMatches) or None}")

            self.closeFinishedMatches(liveMatches=liveMatches)
            self.openNewMatches(liveMatches=liveMatches)
            self.driver.switch_to.window(self.originalWindow)

            offsetLeft, offsetRight = delayRngs
            rngedDelay = delay + random.randint(-offsetLeft, offsetRight)
            self.log.info(f"Next check: {datetime.now() + timedelta(seconds=rngedDelay)} ({rngedDelay}s from now)")
            time.sleep(rngedDelay)
            self.log.debug("Done sleeping")

    def getLiveMatches(self):
        """
        Fetches all the current/live esports matches on the LoL Esports website.
        """
        matches = []
        elements = self.driver.find_elements(by=By.CSS_SELECTOR, value=".live.event")
        for element in elements:
            matches.append(element.get_attribute("href"))
        return matches

    def closeFinishedMatches(self, liveMatches):
        toRemove = []
        for k in self.currentWindows.keys():
            self.driver.switch_to.window(self.currentWindows[k])
            if k not in liveMatches or not self.rewards.checkRewards(k)[0]:
                self.log.info(f"{k} has finished or hasn't been eligible for rewards and will be retried")
                self.driver.close()
                toRemove.append(k)
                self.driver.switch_to.window(self.originalWindow)
                time.sleep(5)
        for k in toRemove:
            self.currentWindows.pop(k, None)
        self.driver.switch_to.window(self.originalWindow)  

    def openNewMatches(self, liveMatches):
        newLiveMatches = set(liveMatches) - set(self.currentWindows.keys())
        for match in newLiveMatches:
            # if "vcs" not in match:
            #     continue
            self.driver.switch_to.new_window('tab')
            time.sleep(2)
            self.currentWindows[match] = self.driver.current_window_handle
            if match in self.OVERRIDES:
                url = self.OVERRIDES[match]
                self.log.info(f"Overriding {match} to {url}")
            else:
                self.log.debug(f"Override not found for {match}")
                url = match
            self.driver.get(url)
            for i in range(1, 4):
                for j, provider in enumerate((self.twitch, self.youtube), 1):
                    self.log.debug(f"Probing provider {provider.__class__.__name__}{j} {i}")
                    try:
                        provider.setQuality()
                        break
                    except TimeoutException:
                        self.log.warning(f"Cannot set quality for provider {provider.__class__.__name__}{j} {i}")
                        continue
                    except (NoSuchElementException, StaleElementReferenceException) as e:
                        self.log.warning("Known exception:")
                        self.log.exception(e)
                    except WebDriverException as e:
                        self.log.critical("Unknown shit happened:")
                        self.log.exception(e)
                else:
                    self.log.critical(f"Provider unknown {i}, all expected providers failed")
                eligible, matchName = self.rewards.checkRewards(url)
                if eligible:
                    break
                self.log.info(f"Refreshing {matchName} {i}")
                self.driver.refresh()
            else:
                self.log.error(f"Max retires reached {i}. {matchName} is really not eligible for rewards")
            time.sleep(5)
