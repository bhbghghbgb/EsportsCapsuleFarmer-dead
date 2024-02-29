from time import sleep
class Locale:
    def __init__(self, log, driver) -> None:
        self.log = log
        self.driver = driver

    def getCurrentLocale(self):
        locale = self.driver.execute_script("return window.localStorage['selected-locale'];")
        self.log.debug(f"Current locale: {locale}")
        return locale
    
    def setLocale(self, locale):
        self.driver.execute_script(f"window.localStorage['selected-locale'] = '{locale}';")
        self.log.debug(f"Locale set: {locale}")

    def checkLocale(self):
        return self.getCurrentLocale() == 'en-US'
    
    def forceLocale(self):
        if not self.checkLocale():
            self.setLocale('en-US')
            sleep(1)
            self.driver.refresh()
