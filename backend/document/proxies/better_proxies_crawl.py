import requests
import time
import datetime
from random import randrange
import fake_useragent
import platform
# from utils import os_utilities

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json

import logging
from selenium.webdriver.remote.remote_connection import LOGGER

LOGGER.setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def generate_ua():
    ua = fake_useragent.UserAgent(cache=False, use_cache_server=False, verify_ssl=False)
    return ua.random


def generate_proxy(res, anonimity):
    randint = randrange(len(res))
    while 1:
        if anonimity == 1:
            if res[randint]['Anonymity'] == "transparent":
                return res[randint]['IP Address'] + ":" + res[randint]['Port']
        if anonimity == 2:
            if res[randint]['Anonymity'] == "anonymous":
                return res[randint]['IP Address'] + ":" + res[randint]['Port']
        if anonimity == 3:
            if res[randint]['Anonymity'] == "high anonymity" or res[randint]['Anonymity'] == "elite proxy":
                return res[randint]['IP Address'] + ":" + res[randint]['Port']
        else:
            randint = randrange(len(res))


def gen_driver(enable_proxies, anonimity, pref=""):
    driver_path = "resources/selenium_drivers/chromedriver"
    if platform.system() == 'windows':
        driver_path = "resources/selenium_drivers/chromedriver.exe"
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-application-cache")
    options.add_argument('--no-sandbox')
    # options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--incognito")
    options.add_argument("--disable-dev-shm-usage")
    if enable_proxies:
        proxies_path = "free_proxies.json"
        f = open(proxies_path)
        res = json.load(f)
        f.close()
        PROXY = generate_proxy(res, anonimity)
        webdriver.DesiredCapabilities.CHROME['proxy'] = {
            "httpProxy": PROXY,
            "ftpProxy": PROXY,
            "sslProxy": PROXY,
            "proxyType": "MANUAL", }
        webdriver.DesiredCapabilities.CHROME['acceptSslCerts'] = True
    #         options.add_argument("--proxy-server={0}".format(proxy))
    if pref != "":
        options.add_experimental_option("prefs", pref)
    try:
        user_agent = generate_ua()
        if user_agent:
            options.add_argument(f'user-agent={user_agent}')
    except:
        pass
    driver = webdriver.Chrome(driver_path, options=options)
    return driver


def time_formater(str):
    now = datetime.datetime.now()
    time = int(str.split(" ")[0])
    if 'secs' in str:
        return (now - datetime.timedelta(seconds=time)).strftime("%Y,%m,%d, %H:%M:%S")
    if 'sec' in str:
        return (now - datetime.timedelta(seconds=1)).strftime("%Y,%m,%d, %H:%M:%S")
    if 'mins' in str:
        return (now - datetime.timedelta(minutes=time)).strftime("%Y,%m,%d, %H:%M:%S")
    if 'min' in str:
        return (now - datetime.timedelta(minutes=1)).strftime("%Y,%m,%d, %H:%M:%S")
    if 'hours' in str:
        return (now - datetime.timedelta(hours=time)).strftime("%Y,%m,%d, %H:%M:%S")
    if 'hour' in str:
        return (now - datetime.timedelta(hours=1)).strftime("%Y,%m,%d, %H:%M:%S")
    return


def hidemy_name_crawl(enable_proxies=False, anonimity=1):
    # turn off headless options to work
    res = []
    name_gen = 0
    check = True
    while check:
        try:
            url = "https://hidemy.name/en/proxy-list/" + "?start={0}#list".format(name_gen)
            name_gen += 64
            driver = gen_driver(enable_proxies, anonimity)
            driver.get(url)
            time.sleep(5)
            table = driver.find_elements_by_tag_name("table")
            tds = table[0].find_elements_by_tag_name('td')
            if len(tds) < 10:
                check = False
            for i in range(6, len(tds)):
                if i % 7 == 0:
                    item = {}
                    item['IP Address'] = tds[i].text
                    item['Port'] = tds[i + 1].text
                    #                     item['Country'] = tds[i+2].text
                    item['Anonymity'] = tds[i + 5].text
                    item['Last Checked'] = tds[i + 6].text
                    res.append(item)
            print("done ", str(name_gen))
            driver.quit()
        except:
            check = False
    return res


def free_proxy_cz_crawl(enable_proxies=False, anonimity=3):
    res = []
    check = True
    name_gen = 1
    while (check):
        try:
            if name_gen < 151:
                url = "http://free-proxy.cz/en/proxylist/main/{0}".format(name_gen)
                driver = gen_driver(enable_proxies, anonimity)
                driver.get(url)
                table = driver.find_element_by_id("proxy_list")
                tds = table.find_elements_by_tag_name('td')
                for i in range(len(tds) - 3):
                    if i % 11 == 0:
                        if i > 43:
                            i = i + 1
                        if i > 243:
                            i += 1
                        item = {}
                        item['IP Address'] = tds[i].text
                        item['Port'] = tds[i + 1].text
                        item['Anonymity'] = tds[i + 6].text
                        item['Last Checked'] = time_formater(tds[i + 10].text)
                        item["order"] = i
                        res.append(item)
                print("done ", str(name_gen))
                name_gen += 1
                driver.quit()
        except:
            name_gen += 1
            continue
    return res
