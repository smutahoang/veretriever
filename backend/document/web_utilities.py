import os

from selenium import webdriver
from selenium.webdriver.chrome import service
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import fake_useragent

import logging
from selenium.webdriver.remote.remote_connection import LOGGER

LOGGER.setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def generate_ua():
    ua = fake_useragent.UserAgent(cache=False, use_cache_server=False, verify_ssl=False)
    return ua.random


def create_selenium_webdriver():
    print('creating selenium driver:')
    driver_path = "resources/selenium_drivers/chromedriver"
    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

    options = webdriver.ChromeOptions()
    options.add_argument("--disable-application-cache")
    options.add_argument('--no-sandbox')
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--incognito")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--window-size=1920,1080")
    print('\t faking a user agent')
    try:
        user_agent = generate_ua()
        if user_agent:
            options.add_argument(f'user-agent={user_agent}')
    except:
        pass

    chrome_prefs = {}
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
    options.experimental_options["prefs"] = chrome_prefs

    # driver = webdriver.Chrome(driver_path, options=options, desired_capabilities=capabilities)
    driver = webdriver.Chrome(driver_path, options=options)
    print('driver is created')
    return driver


def url_normalize(url):
    if url.startswith('http'):
        return url
    else:
        url = 'https://www.' + url
    return url
