from itertools import count
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import argparse

# Classes
from EsportsCapsuleFarmer.Setup.LoginHandler import LoginHandler
from EsportsCapsuleFarmer.Setup.Webdriver import Webdriver
from EsportsCapsuleFarmer.Setup.Logger.Logger import Logger
from EsportsCapsuleFarmer.Setup.Config import Config
from EsportsCapsuleFarmer.Setup.Locale import Locale
from EsportsCapsuleFarmer.Match import Match

###################################################

CURRENT_VERSION = 4.0

parser = argparse.ArgumentParser(prog='CapsuleFarmer.exe', description='Farm Esports Capsules by watching lolesports.com.')
parser.add_argument('-b', '--browser', dest="browser", choices=['chrome', 'firefox', 'edge'], default="chrome",
                    help='Select one of the supported browsers')
parser.add_argument('-c', '--config', dest="configPath", default="./config.yaml",
                    help='Path to a custom config file')
parser.add_argument('-d', '--delay', dest="delay", default=600, type=int,
                    help='Time spent sleeping between match checking (in seconds)')
parser.add_argument('-sd', '--session-dir', dest="session_dir", default="./ucSession",
                    help='Dir to be used as chrome profile')
args = parser.parse_args()

print("*********************************************************")
print(f"*        Thank you for using Capsule Farmer v{CURRENT_VERSION}!       *")
print("* Please consider supporting League of Poro on YouTube. *")
print("*    If you need help with the app, join our Discord    *")
print("*             https://discord.gg/ebm5MJNvHU             *")
print("*********************************************************")
print()

# Mutes preexisting loggers like selenium_driver_updater
log = Logger().createLogger()
config = Config(log=log, args=args).readConfig()
hasAutoLogin, isHeadless, username, password, browser, delay = config.getArgs()
delayRngs = config.getDelayRngs()

for i in count(1):
    log.debug(f"In main.py loop {i}")
    driver = None
    try:
        try:
            driver = Webdriver(log=log, browser=browser, headless=isHeadless and hasAutoLogin, profile_dir=args.session_dir).createWebdriver()
        except Exception as ex:
            print(ex)
            print("CANNOT CREATE A WEBDRIVER! Are you running the latest browser version? Check the configured browser for any updates!\nPress any key to exit...")
            input()
            break

        loginHandler = LoginHandler(log=log, driver=driver)
        locale = Locale(log=log, driver=driver)

        driver.get("https://lolesports.com/schedule")

        # Handle login
        if hasAutoLogin:
            try:
                loginHandler.automaticLogIn(username, password)
            except TimeoutException:
                log.error("Automatic login failed, incorrect credentials?")
                if isHeadless:
                    driver.quit()
                    log.info("Exiting...")
                    exit()

        while not driver.find_elements(by=By.CSS_SELECTOR, value="div.riotbar-summoner-name"):
            if not hasAutoLogin:
                log.info("Waiting for login")
            else: 
                log.warning("Please log in manually")
            time.sleep(5)
        log.debug("Logged in")
        locale.forceLocale()
        log.debug("Forced locale")
        
        Match(log=log, driver=driver).watchForMatches(delay=delay, delayRngs=delayRngs)
        # Match(log=log, driver=driver).watchForMatches(10, (0,0))
    except Exception as e:
        log.critical("Exception propagated to main.py")
        log.exception(e)
    finally:
        if driver:
            driver.quit()
