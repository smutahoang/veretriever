import requests
import time
import datetime
from random import randrange
import fake_useragent
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
# from utils import os_utilities
import platform
import json
import logging
from selenium.webdriver.remote.remote_connection import LOGGER

LOGGER.setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def generate_ua():
    ua = fake_useragent.UserAgent(cache=False, use_cache_server=False, verify_ssl=False)
    return ua.random


# def generate_proxy(res,anonimity):
#     randint=randrange(len(res))
#     while 1:
#         if anonimity == 1:
#             if res[randint]['Anonymity'] == "transparent":
#                 return res[randint]['IP Address']+":"+res[randint]['Port']
#         if anonimity == 2:
#             if res[randint]['Anonymity'] == "anonymous":
#                 return res[randint]['IP Address']+":"+res[randint]['Port']
#         if anonimity == 3:
#             if res[randint]['Anonymity'] == "high anonymity":
#                 return res[randint]['IP Address']+":"+res[randint]['Port']
#         else:
#             randint=randrange(len(res))


def gen_driver(pref=""):
    # proxies_path="proxies.json"
    # f = open(proxies_path)
    # res = json.load(f)
    # f.close()
    driver_path = "resources/selenium_drivers/chromedriver"
    if platform.system() == 'windows':
        driver_path = "resources/selenium_drivers/chromedriver.exe"
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
    #     if enable_proxies:
    #         PROXY=generate_proxy(res,anonimity)
    #         webdriver.DesiredCapabilities.CHROME['proxy'] = {
    #         "httpProxy": PROXY,
    #         "ftpProxy": PROXY,
    #         "sslProxy": PROXY,
    #         "proxyType": "MANUAL",}
    #         webdriver.DesiredCapabilities.CHROME['acceptSslCerts']=True
    # #         options.add_argument("--proxy-server={0}".format(proxy))
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


def free_proxy_list_crawl():
    url = 'https://free-proxy-list.net'
    driver = gen_driver()
    driver.get(url)
    table = driver.find_element_by_tag_name("table")
    tds = table.find_elements_by_tag_name('td')
    res = []
    for i in range(len(tds)):
        if i % 8 == 0:
            item = {}
            item['IP Address'] = tds[i].text
            item['Port'] = tds[i + 1].text
            #             item['Code'] = tds[i+2].text
            #         item['Country'] = tds[i+3].text
            if tds[i + 4].text == "elite proxy":
                item['Anonymity'] = "high anonymity"
            else:
                item['Anonymity'] = tds[i + 4].text
            #             item['Google'] = tds[i+5].text
            #             item['Https'] = tds[i+6].text
            item['Last Checked'] = time_formater(tds[i + 7].text)
            res.append(item)
    driver.quit()
    return res


def getproxylist_crawl():
    res = []
    check = True
    url = "https://api.getproxylist.com/proxy"
    driver = gen_driver()
    driver.get(url)
    while (check):
        try:
            obj = requests.get("https://api.getproxylist.com/proxy")
            a = obj.json()
            item = {}
            item['IP Address'] = a["ip"]
            item['Port'] = a["port"]
            item['Anonymity'] = a["anonymity"]
            item['Last Checked'] = a['lastTested']
            res.append(item)
            # print("done ",item['IP Address'])
            driver.quit()
            time.sleep(2)
        except:
            check = False
    return res

# if __name__ == '__main__':
#     # print(os.listdir(""))
#     file=open("proxies.txt","w")
#     lst1=free_proxy_list_crawl()
#     lst2=getproxylist_crawl()
#     res=lst1+lst2
#     for dct in res:
#         file.write(dct)
#     file.close()
#     print(res)
