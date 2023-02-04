# -*- coding: utf-8 -*-
#########################################################
# python
import asyncio
import os
import sys
import traceback
import time
import re
import random
import urllib
from urllib.parse import urlparse

# import pip

# import urlparse
# from urllib.parse import urlparse
import json

import aiohttp


# "selenium-wire"
packages = ["beautifulsoup4", "requests-cache", "cloudscraper"]

for package in packages:
    try:
        import package

    except ModuleNotFoundError:
        if package == "playwright":
            pass
            # os.system(f"pip3 install playwright")
            # os.system(f"playwright install")
    except ImportError:
        # main(["install", package])
        if package == "playwright":
            pass
            # os.system(f"pip3 install {package}")
            # os.system(f"playwright install")
        else:
            os.system(f"pip3 install {package}")

# third-party
import requests

# from fake_useragent import UserAgent

# import requests_cache
# from requests_cache import CachedSession
from requests_cache import CachedSession

try:
    import cloudscraper
except ImportError:
    os.system(f'{app.config["config"]["pip"]} install cloudscraper')
    import cloudscraper

# import cfscrape
from lxml import html

from .lib.utils import yommi_timeit, yommi_async_timeit

try:
    from bs4 import BeautifulSoup
except ImportError:
    os.system(f'{app.config["config"]["pip"]} install BeautifulSoup4')
    from bs4 import BeautifulSoup

# import snoop
# from snoop import spy

# sjva 공용
from framework import db
from framework.util import Util
from framework.logger import get_logger

# 패키지
# from .plugin import package_name, logger
# from anime_downloader.logic_ohli24 import ModelOhli24Item
from .model import ModelSetting, ModelLinkkf, ModelLinkkfProgram
from .logic_queue import LogicQueue

#########################################################
package_name = __name__.split(".")[0]
logger = get_logger(package_name)
cache_path = os.path.dirname(__file__)


# requests_cache.install_cache("linkkf_cache", backend="sqlite", expire_after=300)


class LogicLinkkfYommi(object):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/104.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "Referer": "https://kfani.me",
        # "Cookie": "SL_G_WPT_TO=ko; SL_GWPT_Show_Hide_tmp=1; SL_wptGlobTipTmp=1",
    }

    session = None
    referer = None
    current_data = None

    @staticmethod
    def get_html(url, cached=False):

        try:
            if LogicLinkkfYommi.referer is None:
                LogicLinkkfYommi.referer = f"{ModelSetting.get('linkkf_url')}"

            # return LogicLinkkfYommi.get_html_requests(url)
            return LogicLinkkfYommi.get_html_cloudflare(url)

        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    @staticmethod
    def get_html_requests(url, cached=False):
        if LogicLinkkfYommi.session is None:
            if cached:
                logger.debug("cached===========++++++++++++")

                LogicLinkkfYommi.session = CachedSession(
                    os.path.join(cache_path, "linkkf_cache"),
                    backend="sqlite",
                    expire_after=300,
                    cache_control=True,
                )
                # print(f"{cache_path}")
                # print(f"cache_path:: {LogicLinkkfYommi.session.cache}")
            else:
                LogicLinkkfYommi.session = requests.Session()

        LogicLinkkfYommi.referer = f"{ModelSetting.get('linkkf_url')}"

        LogicLinkkfYommi.headers["Referer"] = LogicLinkkfYommi.referer

        # logger.debug(
        #     f"get_html()::LogicLinkkfYommi.referer = {LogicLinkkfYommi.referer}"
        # )
        page = LogicLinkkfYommi.session.get(url, headers=LogicLinkkfYommi.headers)
        # logger.info(f"page: {page}")

        return page.content.decode("utf8", errors="replace")

    @staticmethod
    def get_html_selenium(url, referer=None):
        from selenium.webdriver.common.by import By

        from selenium import webdriver
        from selenium_stealth import stealth
        from webdriver_manager.chrome import ChromeDriverManager

        from seleniumwire import webdriver
        import time
        import platform
        import os

        os_platform = platform.system()

        # print(os_platform)

        options = webdriver.ChromeOptions()
        # 크롬드라이버 헤더 옵션추가 (리눅스에서 실행시 필수)
        options.add_argument("start-maximized")
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        if os_platform == "Darwin":
            # 크롬드라이버 경로
            driver_bin_path = os.path.join(
                os.path.dirname(__file__), "bin", f"{os_platform}"
            )
            driver_path = f"{driver_bin_path}/chromedriver"
            driver = webdriver.Chrome(
                executable_path=driver_path, chrome_options=options
            )
            # driver = webdriver.Chrome(
            #     ChromeDriverManager().install(), chrome_options=options
            # )
        elif os_platform == "Linux":
            driver_bin_path = os.path.join(
                os.path.dirname(__file__), "bin", f"{os_platform}"
            )
            driver_path = f"{driver_bin_path}/chromedriver"
            driver = webdriver.Chrome(
                executable_path=driver_path, chrome_options=options
            )

        else:
            # driver_bin_path = os.path.join(
            #     os.path.dirname(__file__), "bin", f"{os_platform}"
            # )
            # driver_path = f"{driver_bin_path}/chromedriver"
            # driver = webdriver.Chrome(executable_path=driver_path, chrome_options=options)
            driver = webdriver.Chrome(
                ChromeDriverManager().install(), chrome_options=options
            )

        LogicLinkkfYommi.headers["Referer"] = f"{ModelSetting.get('linkkf_url')}"

        driver.header_overrides = LogicLinkkfYommi.headers
        # stealth(
        #     driver,
        #     languages=["en-US", "en"],
        #     vendor="Google Inc.",
        #     platform="Win32",
        #     webgl_vendor="Intel Inc.",
        #     renderer="Intel Iris OpenGL Engine",
        #     fix_hairline=True,
        # )
        driver.get(url)

        # driver.refresh()
        print(f"current_url:: {driver.current_url}")

        # time.sleep(1)
        elem = driver.find_element(By.XPATH, "//*")
        source_code = elem.get_attribute("outerHTML")

        time.sleep(3.0)

        return source_code.encode("utf-8")

    @staticmethod
    def get_html_playwright(url):
        from playwright.sync_api import sync_playwright
        import time

        try:

            start = time.time()
            ua = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/69.0.3497.100 Safari/537.36"
            )
            # from playwright_stealth import stealth_sync

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent=ua,
                )
                LogicLinkkfYommi.referer = f"{ModelSetting.get('linkkf_url')}"

                LogicLinkkfYommi.headers["Referer"] = LogicLinkkfYommi.referer

                logger.debug(f"headers::: {LogicLinkkfYommi.headers}")

                context.set_extra_http_headers(LogicLinkkfYommi.headers)

                page = context.new_page()

                page.set_extra_http_headers(LogicLinkkfYommi.headers)
                # stealth_sync(page)
                page.goto(url, wait_until="domcontentloaded")

                # print(page.request.headers)
                # print(page.content())

                print(f"run at {time.time() - start} sec")

                return page.content()
        except ModuleNotFoundError:
            # os.system(f"pip3 install playwright")
            # os.system(f"playwright install")
            pass

    @staticmethod
    def get_html_cloudflare(url, cached=False):
        # scraper = cloudscraper.create_scraper(
        #     # disableCloudflareV1=True,
        #     # captcha={"provider": "return_response"},
        #     delay=10,
        #     browser="chrome",
        # )
        # scraper = cfscrape.create_scraper(
        #     browser={"browser": "chrome", "platform": "android", "desktop": False}
        # )

        # scraper = cloudscraper.create_scraper(
        #     browser={"browser": "chrome", "platform": "windows", "mobile": False},
        #     debug=True,
        # )
        logger.debug("cloudflare protection bypass ==================")

        user_agents_list = [
            "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
        ]
        # ua = UserAgent(verify_ssl=False)

        LogicLinkkfYommi.headers["User-Agent"] = random.choice(user_agents_list)

        LogicLinkkfYommi.headers["Referer"] = LogicLinkkfYommi.referer

        # logger.debug(f"headers:: {LogicLinkkfYommi.headers}")

        if LogicLinkkfYommi.session is None:
            LogicLinkkfYommi.session = requests.Session()

        # LogicLinkkfYommi.session = requests.Session()
        # re_sess = requests.Session()
        # logger.debug(LogicLinkkfYommi.session)

        # sess = cloudscraper.create_scraper(
        #     # browser={"browser": "firefox", "mobile": False},
        #     browser={"browser": "chrome", "mobile": False},
        #     debug=True,
        #     sess=LogicLinkkfYommi.session,
        #     delay=10,
        # )
        # scraper = cloudscraper.create_scraper(sess=re_sess)
        scraper = cloudscraper.create_scraper(
            # debug=True,
            delay=10,
            sess=LogicLinkkfYommi.session,
            browser={
                "custom": "linkkf",
            },
        )

        # print(scraper.get(url, headers=LogicLinkkfYommi.headers).content)
        # print(scraper.get(url).content)
        # return scraper.get(url, headers=LogicLinkkfYommi.headers).content
        # logger.debug(LogicLinkkfYommi.headers)
        return scraper.get(
            url,
            headers=LogicLinkkfYommi.headers,
            timeout=10,
        ).content.decode("utf8", errors="replace")

    @staticmethod
    def get_video_url_from_url(url, url2):
        video_url = None
        referer_url = None
        vtt_url = None
        LogicLinkkfYommi.referer = url2
        # logger.info("dx download url : %s , url2 : %s" % (url, url2))
        # logger.debug(LogicLinkkfYommi.referer)

        try:
            if "ani1" in url2:
                # kfani 계열 처리 => 방문해서 m3u8을 받아온다.
                logger.debug("ani1 routine=========================")
                LogicLinkkfYommi.referer = f"{ModelSetting.get('linkkf_url')}"
                # logger.debug(f"url2: {url2}")
                ani1_html = LogicLinkkfYommi.get_html(url2)

                tree = html.fromstring(ani1_html)
                option_url = tree.xpath("//select[@id='server-list']/option[1]/@value")

                # logger.debug(f"option_url:: {option_url}")

                data = LogicLinkkfYommi.get_html(option_url[0])
                # print(type(data))
                regex2 = r'"([^\"]*m3u8)"|<source[^>]+src=\"([^"]+)'

                temp_url = re.findall(regex2, data)[0]
                video_url = ""
                ref = "https://ani1.app"
                for i in temp_url:
                    if i is None:
                        continue
                    video_url = i
                    # video_url = '{1} -headers \'Referer: "{0}"\' -user_agent "Mozilla/5.0 (Windows NT 10.0; Win64;
                    # x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3554.0 Safari/537.36"'.format(ref,
                    # video_url)

                data_tree = html.fromstring(data)
                # print(data_tree.xpath("//video/source/@src"))
                vtt_elem = data_tree.xpath("//track/@src")[0]
                # vtt_elem = data_tree.xpath("//*[contains(@src, '.vtt']")[0]

                # print(vtt_elem)

                match = re.compile(
                    r"<track.+src=\"(?P<vtt_url>.*?.vtt)\"", re.MULTILINE
                ).search(data)

                vtt_url = match.group("vtt_url")

                referer_url = "https://kfani.me/"

            elif "kfani" in url2:
                # kfani 계열 처리 => 방문해서 m3u8을 받아온다.
                logger.debug("kfani routine=================================")
                LogicLinkkfYommi.referer = url2
                # logger.debug(f"url2: {url2}")
                data = LogicLinkkfYommi.get_html(url2)
                logger.info(f"dx: data {data}")
                regex2 = r'"([^\"]*m3u8)"|<source[^>]+src=\"([^"]+)'
                regex3 = r"https:\/\/.*?m3u8"

                try:

                    temp_url = re.findall(regex2, data)[0]
                except:
                    temp_url = re.findall(regex3, data)
                logger.debug(f"temp_url: data {temp_url}")
                video_url = ""
                ref = "https://kfani.me"
                for i in temp_url:
                    if i is None:
                        continue
                    video_url = i
                    # video_url = '{1} -headers \'Referer: "{0}"\' -user_agent "Mozilla/5.0 (Windows NT 10.0; Win64;
                    # x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3554.0 Safari/537.36"'.format(ref,
                    # video_url)

                # @k45734
                vtt_url = None
                try:
                    _match1 = re.compile(
                        r"<track.+src=\"(?P<vtt_url>.*?.vtt)", re.MULTILINE
                    ).search(data)
                    vtt_url = _match1.group("vtt_url")
                except:
                    _match2 = re.compile(
                        r"url: \'(?P<vtt_url>.*?.vtt)", re.MULTILINE
                    ).search(data)
                    vtt_url = _match2.group("vtt_url")

                logger.info("vtt_url: %s", vtt_url)

                referer_url = url2

            elif "kftv" in url2:
                # kftv 계열 처리 => url의 id로 https://yt.kftv.live/getLinkStreamMd5/df6960891d226e24b117b850b44a2290 페이지
                # 접속해서 json 받아오고, json에서 url을 추출해야함
                if "=" in url2:
                    md5 = urlparse.urlparse(url2).query.split("=")[1]
                elif "embedplay" in url2:
                    md5 = url2.split("/")[-1]
                url3 = "https://yt.kftv.live/getLinkStreamMd5/" + md5
                # logger.info("download url : %s , url3 : %s" % (url, url3))
                data3 = LogicLinkkfYommi.get_html(url3)
                data3dict = json.loads(data3)
                # print(data3dict)
                video_url = data3dict[0]["file"]

            elif "k40chan" in url2:
                # k40chan 계열 처리 => 방문해서 m3u8을 받아온다.
                # k45734 님 소스 반영 (확인은 안해봄 잘 동작할꺼라고 믿고,)
                logger.debug("k40chan routine=================================")
                LogicLinkkfYommi.referer = url2
                data = LogicLinkkfYommi.get_html(url2)

                regex2 = r'"([^\"]*m3u8)"|<source[^>]+src=\"([^"]+)'

                temp_url = re.findall(regex2, data)[0]
                video_url = ""
                # ref = "https://kfani.me"
                for i in temp_url:
                    if i is None:
                        continue
                    video_url = i

                match = re.compile(r"<track.+src\=\"(?P<vtt_url>.*?.vtt)").search(data)
                vtt_url = match.group("vtt_url")

                referer_url = url2

            elif "linkkf" in url2:
                logger.deubg("linkkf routine")
                # linkkf 계열 처리 => URL 리스트를 받아오고, 하나 골라 방문 해서 m3u8을 받아온다.
                referer_url = url2
                data2 = LogicLinkkfYommi.get_html(url2)
                # print(data2)
                regex = r"cat1 = [^\[]*([^\]]*)"
                cat = re.findall(regex, data2)[0]
                # logger.info("cat: %s", cat)
                regex = r"\"([^\"]*)\""
                url3s = re.findall(regex, cat)
                url3 = random.choice(url3s)
                # logger.info("url3: %s", url3)
                # logger.info("download url : %s , url3 : %s" % (url, url3))
                if "kftv" in url3:
                    return LogicLinkkfYommi.get_video_url_from_url(url2, url3)
                elif url3.startswith("/"):
                    url3 = urlparse.urljoin(url2, url3)
                    print("url3 = ", url3)
                    LogicLinkkfYommi.referer = url2
                    data3 = LogicLinkkfYommi.get_html(url3)
                    # logger.info('data3: %s', data3)
                    # regex2 = r'"([^\"]*m3u8)"'
                    regex2 = r'"([^\"]*mp4|m3u8)"'
                    video_url = re.findall(regex2, data3)[0]
                    # logger.info('video_url: %s', video_url)
                    referer_url = url3

                else:
                    logger.error("새로운 유형의 url 발생! %s %s %s" % (url, url2, url3))
            elif "kakao" in url2:
                # kakao 계열 처리, 외부 API 이용
                payload = {"inputUrl": url2}
                kakao_url = (
                    "http://webtool.cusis.net/wp-pages/download-kakaotv-video/video.php"
                )
                data2 = requests.post(
                    kakao_url,
                    json=payload,
                    headers={
                        "referer": "http://webtool.cusis.net/download-kakaotv-video/"
                    },
                ).content
                time.sleep(3)  # 서버 부하 방지를 위해 단시간에 너무 많은 URL전송을 하면 IP를 차단합니다.
                url3 = json.loads(data2)
                # logger.info("download url2 : %s , url3 : %s" % (url2, url3))
                video_url = url3
            elif "#V" in url2:  # V 패턴 추가
                print("#v routine")

                data2 = LogicLinkkfYommi.get_html(url2)

                regex = r"cat1 = [^\[]*([^\]]*)"
                cat = re.findall(regex, data2)[0]
                regex = r"\"([^\"]*)\""
                url3s = re.findall(regex, cat)
                url3 = random.choice(url3s)
                # logger.info("download url : %s , url3 : %s" % (url, url3))
                if "kftv" in url3:
                    return LogicLinkkfYommi.get_video_url_from_url(url2, url3)
                elif url3.startswith("/"):
                    url3 = urlparse.urljoin(url2, url3)
                    LogicLinkkfYommi.referer = url2
                    data3 = LogicLinkkfYommi.get_html(url3)

                    regex2 = r'"([^\"]*mp4)"'
                    video_url = re.findall(regex2, data3)[0]
                else:
                    logger.error("새로운 유형의 url 발생! %s %s %s" % (url, url2, url3))

            elif "#M2" in url2:
                LogicLinkkfYommi.referer = url2
                data2 = LogicLinkkfYommi.get_html(url2)
                # print(data2)

                regex = r"cat1 = [^\[]*([^\]]*)"
                cat = re.findall(regex, data2)[0]
                regex = r"\"([^\"]*)\""
                url3s = re.findall(regex, cat)
                url3 = random.choice(url3s)
                # logger.info("download url : %s , url3 : %s" % (url, url3))
                if "kftv" in url3:
                    return LogicLinkkfYommi.get_video_url_from_url(url2, url3)
                elif url3.startswith("/"):
                    url3 = urlparse.urljoin(url2, url3)
                    LogicLinkkfYommi.referer = url2
                    data3 = LogicLinkkfYommi.get_html(url3)
                    # print("내용: %s", data3)
                    # logger.info("movie content: %s", data3)
                    # regex2 = r'"([^\"]*m3u8)"'
                    regex2 = r'"([^\"]*mp4)"'
                    video_url = re.findall(regex2, data3)[0]
                else:
                    logger.error("새로운 유형의 url 발생! %s %s %s" % (url, url2, url3))
            elif "😀#i" in url2:
                LogicLinkkfYommi.referer = url2
                data2 = LogicLinkkfYommi.get_html(url2)
                # logger.info(data2)

                regex = r"cat1 = [^\[]*([^\]]*)"
                cat = re.findall(regex, data2)[0]
                regex = r"\"([^\"]*)\""
                url3s = re.findall(regex, cat)
                url3 = random.choice(url3s)
                # logger.info("download url : %s , url3 : %s" % (url, url3))

            elif "#k" in url2:
                data2 = LogicLinkkfYommi.get_html(url2)
                # logger.info(data2)

                regex = r"cat1 = [^\[]*([^\]]*)"
                cat = re.findall(regex, data2)[0]
                regex = r"\"([^\"]*)\""
                url3s = re.findall(regex, cat)
                url3 = random.choice(url3s)
                # logger.info("download url : %s , url3 : %s" % (url, url3))

            elif "#k2" in url2:
                data2 = LogicLinkkfYommi.get_html(url2)
                # logger.info(data2)

                regex = r"cat1 = [^\[]*([^\]]*)"
                cat = re.findall(regex, data2)[0]
                regex = r"\"([^\"]*)\""
                url3s = re.findall(regex, cat)
                url3 = random.choice(url3s)
                # logger.info("download url : %s , url3 : %s" % (url, url3))
            elif "mopipi" in url2:
                LogicLinkkfYommi.referer = url
                data2 = LogicLinkkfYommi.get_html(url2)
                # logger.info(data2)
                match = re.compile(r"src\=\"(?P<video_url>http.*?\.mp4)").search(data2)
                video_url = match.group("video_url")

                match = re.compile(r"src\=\"(?P<vtt_url>http.*?.vtt)").search(data2)
                logger.info("match group: %s", match.group("video_url"))
                vtt_url = match.group("vtt_url")

                # logger.info("download url : %s , url3 : %s" % (url, url3))

            else:
                logger.error("새로운 유형의 url 발생! %s %s" % (url, url2))
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

        return [video_url, referer_url, vtt_url]

    # @staticmethod
    # def get_html_episode_content(url: str) -> str:
    #     if url.startswith("http"):
    #         html_data = LogicLinkkfYommi.get_html(url)
    #     else:
    #         url = f"https://linkkf.app{url}"
    #
    #         logger.info("get_video_url(): url: %s" % url)
    #         data = LogicLinkkfYommi.get_html(url)
    #
    #         tree = html.fromstring(data)
    #
    #         tree = html.fromstring(data)
    #
    #         pattern = re.compile("var player_data=(.*)")
    #
    #         js_scripts = tree.xpath("//script")
    #
    #         iframe_info = None
    #         index = 0
    #
    #         for js_script in js_scripts:
    #
    #             # print(f"{index}.. {js_script.text_content()}")
    #             if pattern.match(js_script.text_content()):
    #                 # logger.debug("match::::")
    #                 match_data = pattern.match(js_script.text_content())
    #                 iframe_info = json.loads(
    #                     match_data.groups()[0].replace("path:", '"path":')
    #                 )
    #                 # logger.debug(f"iframe_info:: {iframe_info}")
    #
    #             index += 1
    #
    #         ##################################################
    #         # iframe url:: https://s2.ani1c12.top/player/index.php?data='+player_data.url+'
    #         ####################################################
    #
    #         url = f'https://s2.ani1c12.top/player/index.php?data={iframe_info["url"]}'
    #         html_data = LogicLinkkfYommi.get_html(url)
    #
    #     return html_data

    @staticmethod
    def get_video_url(episode_url: str) -> list:
        # 메일로 커밋 정보가 날아와서 잘되는걸로 판단하고 그냥 복사 붙여넣기 하고 적용함(@k45734)
        # url2s = []
        try:
            # regex = r"^(http|https):\/\/"
            #
            # # test_str = "https://mobikf.ncctvgroup.com/player/v350205-sub-1/"
            #
            # matches = re.compile(regex, episode_url)
            #
            # print(matches)

            if episode_url.startswith("http"):
                url = episode_url
            else:
                url = f"https://mobikf.ncctvgroup.com{episode_url}"

            logger.info("get_video_url(): url: %s" % url)
            data = LogicLinkkfYommi.get_html(url)
            # print(data)
            # data = LogicLinkkfYommi.get_html_cloudflare(url)
            # logger.info(data)
            tree = html.fromstring(data)

            tree = html.fromstring(data)

            pattern = re.compile("var player_data=(.*)")

            js_scripts = tree.xpath("//script")
            # logger.info(len(js_scripts))
            # logger.info(js_scripts[10].text_content().strip())

            iframe_info = None
            index = 0

            for js_script in js_scripts:

                # print(f"{index}.. {js_script.text_content()}")
                if pattern.match(js_script.text_content()):
                    logger.debug("match::::")
                    match_data = pattern.match(js_script.text_content())
                    # print(match_data.groups())
                    # print(type(match_data.groups()[0]))
                    iframe_info = json.loads(
                        match_data.groups()[0].replace("path:", '"path":')
                    )
                    logger.info(f"iframe_info:: {iframe_info}")

                index += 1

            ##################################################
            #
            # iframe url:: https://s2.ani1c12.top/player/index.php?data='+player_data.url+'
            # 프레임이 없으면 무시하고 기존처럼 처리 하기
            try:
                iframe_url = (
                    f'https://s2.ani1c12.top/player/index.php?data={iframe_info["url"]}'
                )
            except:
                iframe_url = url
            html_data = LogicLinkkfYommi.get_html(iframe_url)

            # logger.info(html_data)

            tree = html.fromstring(html_data)

            # xpath_select_query = '//*[@id="body"]/div/span/center/select/option'
            xpath_select_query = '//*[@id="body"]/div/span/center/select/option'

            logger.debug(f"dev:: {len(tree.xpath(xpath_select_query))}")

            if len(tree.xpath(xpath_select_query)) > 0:
                pass
            else:
                print("::here")
                xpath_select_query = '//select[@class="switcher"]/option'
                xpath_select_query = "//select/option"

            logger.debug(f"dev1:: {len(tree.xpath(xpath_select_query))}")
            url2s1 = []
            # url2s2 = [tag.attrib["value"] for tag in tree.xpath(xpath_select_query)]
            # k40chan 영상주소는 ffmpeg 로 실패함 어떤 코드가 들어가야 되는지 몰라서 제외하고 영상소스를 선택할수 없어서 램덤으로 선택하여 영상소스를 선택하고 영상소가 죽었을경우에 유용?
            for tag in tree.xpath(xpath_select_query):
                url2s2 = tag.attrib["value"]
                # if 'k40chan' in url2s2:
                #    pass
                # elif 'k39aha' in url2s2:
                if "ds" in url2s2:
                    pass
                else:
                    url2s1.append(url2s2)

            # logger.info('dx: url', url)

            video_url = None
            referer_url = None  # dx
            url2s = random.sample(url2s1, 2)
            # url2s = random.choices(url2s1, k=2)
            logger.info("dx: urls2:: %s", url2s)
            for url2 in url2s:
                try:

                    if video_url is not None:
                        continue
                    logger.debug(f"url: {url}, url2: {url2}")
                    ret = LogicLinkkfYommi.get_video_url_from_url(url, url2)
                    logger.debug(f"ret::::> {ret}")

                    if ret is not None:
                        video_url = ret
                        referer_url = url2
                except Exception as e:
                    logger.error("Exception:%s", e)
                    logger.error(traceback.format_exc())

            # logger.info(video_url)

            # return [video_url, referer_url]
            return video_url
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    @staticmethod
    def apply_new_title(new_title):
        try:
            ret = {}
            if LogicLinkkfYommi.current_data is not None:
                program = (
                    db.session.query(ModelLinkkfProgram)
                    .filter_by(programcode=LogicLinkkfYommi.current_data["code"])
                    .first()
                )
                new_title = Util.change_text_for_use_filename(new_title)
                LogicLinkkfYommi.current_data["save_folder"] = new_title
                program.save_folder = new_title
                db.session.commit()

                for entity in LogicLinkkfYommi.current_data["episode"]:
                    entity["save_folder"] = new_title
                    entity["filename"] = LogicLinkkfYommi.get_filename(
                        LogicLinkkfYommi.current_data["save_folder"],
                        LogicLinkkfYommi.current_data["season"],
                        entity["title"],
                    )

                return LogicLinkkfYommi.current_data
            else:
                ret["ret"] = False
                ret["log"] = "No current data!!"
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
            ret["ret"] = False
            ret["log"] = str(e)
        return ret

    @staticmethod
    def apply_new_season(new_season):
        try:
            ret = {}
            season = int(new_season)
            if LogicLinkkfYommi.current_data is not None:
                program = (
                    db.session.query(ModelLinkkfProgram)
                    .filter_by(programcode=LogicLinkkfYommi.current_data["code"])
                    .first()
                )
                LogicLinkkfYommi.current_data["season"] = season
                program.season = season
                db.session.commit()

                for entity in LogicLinkkfYommi.current_data["episode"]:
                    entity["filename"] = LogicLinkkfYommi.get_filename(
                        LogicLinkkfYommi.current_data["save_folder"],
                        LogicLinkkfYommi.current_data["season"],
                        entity["title"],
                    )
                return LogicLinkkfYommi.current_data
            else:
                ret["ret"] = False
                ret["log"] = "No current data!!"
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
            ret["ret"] = False
            ret["log"] = str(e)
        return ret

    @staticmethod
    def add_whitelist(*args):
        ret = {}

        logger.debug(f"args: {args}")
        logger.debug(f"type:: {type(args[0])}")
        logger.debug(f"title: {args[0]['data_title']}")
        logger.debug(f"LogicLinkkfYommi.current_data:: {LogicLinkkfYommi.current_data}")
        try:

            if len(args) == 0:
                code = str(LogicLinkkfYommi.current_data["code"])
            else:
                # code = str(args[0])
                code = str(args[0]["data_code"])

            whitelist_program = ModelSetting.get("whitelist_program")
            whitelist_programs = [
                str(x.strip().replace(" ", ""))
                for x in whitelist_program.replace("\n", ",").split(",")
            ]
            if code not in whitelist_programs:
                whitelist_programs.append(code)
                whitelist_programs = filter(
                    lambda x: x != "", whitelist_programs
                )  # remove blank code
                whitelist_program = ",".join(whitelist_programs)
                entity = (
                    db.session.query(ModelSetting)
                    .filter_by(key="whitelist_program")
                    .with_for_update()
                    .first()
                )
                entity.value = whitelist_program
                db.session.commit()
                ret["ret"] = True
                ret["code"] = code
                if len(args) == 0:
                    return LogicLinkkfYommi.current_data
                else:
                    return ret
            else:
                ret["ret"] = False
                ret["log"] = "이미 추가되어 있습니다."
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
            ret["ret"] = False
            ret["log"] = str(e)
        return ret

    @staticmethod
    async def fetch_url(session, url):
        async with session.get(url) as resp:
            # print(type(resp.text()))
            data = []
            html_content = await resp.text()
            tree = html.fromstring(html_content)
            tmp_items = tree.xpath('//div[@class="myui-vodlist__box"]')
            for item in tmp_items:
                entity = {}
                entity["link"] = item.xpath(".//a/@href")[0]
                entity["code"] = re.search(r"[0-9]+", entity["link"]).group()
                data.append(entity["code"])
            return data

    @staticmethod
    # def flatten_list(nested_list):
    #     flat_list = []
    #     if isinstance(nested_list, list):
    #         for sublist in nested_list:
    #             flat_list.extend(flatten_list(sublist))
    #     else:
    #         flat_list.append(nested_list)
    #     return flat_list
    def flatten_list(nested_list):
        flat_list = []
        for sublist in nested_list:
            for item in sublist:
                flat_list.append(item)
        return flat_list

    @staticmethod
    @yommi_async_timeit
    async def get_airing_code():
        try:
            data = []
            url = f"https://mobikf.ncctvgroup.com/airing/page/1/"

            html_content = LogicLinkkfYommi.get_html(url)
            tree = html.fromstring(html_content)
            tmp_total = tree.xpath("//div[@id='wp_page']/a[last()]/text()")
            total_page = int(tmp_total[0])
            # logger.debug(tmp_total[0])

            async with aiohttp.ClientSession() as session:
                tasks = [
                    LogicLinkkfYommi.fetch_url(
                        session, f"https://mobikf.ncctvgroup.com/airing/page/{page}/"
                    )
                    for page in range(1, total_page + 1)
                ]
                responses = await asyncio.gather(*tasks)
                data = LogicLinkkfYommi.flatten_list(responses)
                logger.debug(responses)

            # logger.debug(urls)

            # for i in range(1, total_page + 1):
            #     url = f"https://mobikf.ncctvgroup.com/airing/page/{i}/"
            #     logger.debug(url)
            #     html_content = LogicLinkkfYommi.get_html(url)
            #     logger.debug(html_content)
            #     tree = html.fromstring(html_content)
            #     tmp_items = tree.xpath('//div[@class="item"]')
            #     for item in tmp_items:
            #         entity = {}
            #         entity["link"] = item.xpath(".//a/@href")[0]
            #         entity["code"] = re.search(r"[0-9]+", entity["link"]).group()
            #         data.append(entity["code"])

            logger.debug(data)
            return data

        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    @staticmethod
    def get_airing_info():
        try:
            url = f"{ModelSetting.get('linkkf_url')}/airing"
            html_content = LogicLinkkfYommi.get_html(url)
            download_path = ModelSetting.get("download_path")
            tree = html.fromstring(html_content)
            tmp_items = tree.xpath('//div[@class="item"]')
            # logger.info('tmp_items:::', tmp_items)

            data = {"ret": "success"}

            if tree.xpath('//*[@id="wp_page"]//text()'):
                data["total_page"] = tree.xpath('//*[@id="wp_page"]//text()')[-1]
            else:
                data["total_page"] = 0

            data["episode_count"] = len(tmp_items)
            data["episode"] = []

            for item in tmp_items:
                entity = {}
                entity["link"] = item.xpath(".//a/@href")[0]
                entity["code"] = re.search(r"[0-9]+", entity["link"]).group()
                entity["title"] = item.xpath('.//span[@class="name-film"]//text()')[
                    0
                ].strip()
                entity["image_link"] = item.xpath(
                    './/img[@class="photo"]/@data-lazy-src'
                )[0]
                entity["chapter"] = item.xpath(".//a/button/span//text()")[0]
                # logger.info('entity:::', entity['title'])
                data["episode"].append(entity)

            json_file_path = os.path.join(download_path, "airing_list.json")
            # logger.debug("json_file_path:: %s", json_file_path)

            if os.path.is_file(json_file_path):
                # logger.debug("airing_list.json file deleted.")
                os.remove(json_file_path)

            with open(json_file_path, "w") as outfile:
                json.dump(data, outfile)

            return data

        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    @staticmethod
    def get_search_result(query):

        try:
            # query = query.encode("utf-8")
            _query = urllib.parse.quote(query)
            url = f"{ModelSetting.get('linkkf_url')}/?s={_query}"
            logger.debug("search url::> %s", url)
            # html_content = LogicLinkkfYommi.get_html(url)
            html_content = LogicLinkkfYommi.get_html(url)
            download_path = ModelSetting.get("download_path")
            tree = html.fromstring(html_content)
            tmp_items = tree.xpath('//div[@class="myui-vodlist__box"]')
            title_xpath = './/a[@class="text-fff"]//text()'

            data = {"ret": "success", "query": query}

            if tree.xpath('//*[@id="wp_page"]//text()'):
                data["total_page"] = tree.xpath('//*[@id="wp_page"]//text()')[-1]
            else:
                data["total_page"] = 0

            data["episode_count"] = len(tmp_items)
            data["episode"] = []

            for item in tmp_items:
                entity = {}

                entity["link"] = item.xpath(".//a/@href")[0]
                # logger.debug(f"link()::entity['link'] => {entity['link']}")
                entity["code"] = re.search(r"[0-9]+", entity["link"]).group()
                entity["title"] = item.xpath(title_xpath)[0].strip()
                # print(entity["title"])
                # print(type(item.xpath("./a/@style")))

                if len(item.xpath("./a/@style")) > 0:
                    print(
                        re.search(
                            r"url\(((http|https|ftp|ftps)\:\/\/[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(\/\S*)?)\)",
                            item.xpath("./a/@style")[0],
                        ).group()
                    )
                if item.xpath(".//a/@data-original"):
                    entity["image_link"] = item.xpath(".//a/@data-original")[0]

                else:
                    entity["image_link"] = ""
                entity["chapter"] = (
                    item.xpath("./a/span//text()")[0]
                    if len(item.xpath("./a/span//text()")) > 0
                    else ""
                )
                # logger.info('entity:::', entity['title'])
                data["episode"].append(entity)

            json_file_path = os.path.join(download_path, "airing_list.json")
            # logger.debug("json_file_path:: %s", json_file_path)

            with open(json_file_path, "w") as outfile:
                json.dump(data, outfile)

            return data

        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    @staticmethod
    def get_anime_list_info(cate, page):
        logger.debug(f"get_anime_list_info():: ===============")
        logger.debug(f"cate:: {cate}")
        logger.debug(f"page:: {page}")
        items_xpath = ""
        title_xpath = ""
        url = ""

        # Todo:
        #   Query the received result value with db and compare the difference
        #
        # query = (
        #     db.session.query(ModelLinkkf)
        #     .order_by(ModelLinkkf.created_time)
        #     .slice(0, 5)
        #     .all()
        # )
        # logger.debug(query)
        # logger.debug(len(query))
        # latest_download_data = db.session.commit(query)
        # logger.debug(latest_download_data)
        try:
            if cate == "ing":
                url = f"{ModelSetting.get('linkkf_url')}/airing/page/{page}"
                items_xpath = '//div[@class="myui-vodlist__box"]'
                title_xpath = './/a[@class="text-fff"]//text()'
            elif cate == "movie":
                url = f"{ModelSetting.get('linkkf_url')}/ani/page/{page}"
                # items_xpath = '//div[@class="item"]'
                # title_xpath = './/span[@class="name-film"]//text()'
                items_xpath = '//div[@class="myui-vodlist__box"]'
                title_xpath = './/a[@class="text-fff"]//text()'
            elif cate == "complete":
                url = f"{ModelSetting.get('linkkf_url')}/anime-list/page/{page}"
                items_xpath = '//div[@class="myui-vodlist__box"]'
                title_xpath = './/a[@class="text-fff"]//text()'
            elif cate == "top_view":
                url = f"{ModelSetting.get('linkkf_url')}/topview/page/{page}"
                items_xpath = '//div[@class="myui-vodlist__box"]'
                title_xpath = './/a[@class="text-fff"]//text()'

            logger.debug(f"get_anime_list_info():url >> {url}")

            if LogicLinkkfYommi.referer is None:
                LogicLinkkfYommi.referer = f"{ModelSetting.get('linkkf_url')}"

            html_content = LogicLinkkfYommi.get_html(url, cached=False)
            # html_content = LogicLinkkfYommi.get_html_cloudflare(url, cached=False)
            data = {"ret": "success", "page": page}

            tree = html.fromstring(html_content)

            # if (cate == 'top_view'):
            tmp_items = tree.xpath(items_xpath)
            # logger.info(f"tmp_items::: {tmp_items}")

            if tree.xpath('//div[@id="wp_page"]//text()'):
                data["total_page"] = tree.xpath('//div[@id="wp_page"]//text()')[-1]
            else:
                data["total_page"] = 0
            data["episode_count"] = len(tmp_items)
            data["episode"] = []

            for item in tmp_items:
                entity = dict()
                entity["link"] = item.xpath(".//a/@href")[0]
                entity["code"] = re.search(r"[0-9]+", entity["link"]).group()
                entity["title"] = item.xpath(title_xpath)[0].strip()
                entity["image_link"] = item.xpath("./a/@data-original")[0]
                entity["chapter"] = (
                    item.xpath("./a/span//text()")[0]
                    if len(item.xpath("./a/span//text()")) > 0
                    else ""
                )
                # logger.info('entity:::', entity['title'])
                data["episode"].append(entity)

            return data

        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    @staticmethod
    def get_screen_movie_info(page):
        try:
            url = f"{ModelSetting.get('linkkf_url')}/ani/page/{page}"

            html_content = LogicLinkkfYommi.get_html(url, cached=True)
            # html_content = LogicLinkkfYommi.get_html_cloudflare(url, cached=False)
            download_path = ModelSetting.get("download_path")
            tree = html.fromstring(html_content)
            tmp_items = tree.xpath('//div[@class="myui-vodlist__box"]')
            title_xpath = './/a[@class="text-fff"]//text()'
            # logger.info('tmp_items:::', tmp_items)
            data = dict()
            data = {"ret": "success", "page": page}

            data["episode_count"] = len(tmp_items)
            data["episode"] = []

            for item in tmp_items:
                entity = {}
                entity["link"] = item.xpath(".//a/@href")[0]
                entity["code"] = re.search(r"[0-9]+", entity["link"]).group()
                entity["title"] = item.xpath(title_xpath)[0].strip()
                if len(item.xpath("./a/@style")) > 0:
                    print(
                        re.search(
                            r"url\(((http|https|ftp|ftps)\:\/\/[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(\/\S*)?)\)",
                            item.xpath("./a/@style")[0],
                        ).group()
                    )

                if item.xpath(".//a/@data-original"):
                    entity["image_link"] = item.xpath(".//a/@data-original")[0]

                else:
                    entity["image_link"] = ""
                # entity["image_link"] = item.xpath("./a/@data-original")[0]
                entity["chapter"] = (
                    item.xpath("./a/span//text()")[0]
                    if len(item.xpath("./a/span//text()")) > 0
                    else ""
                )
                # logger.info('entity:::', entity['title'])
                data["episode"].append(entity)

            json_file_path = os.path.join(download_path, "airing_list.json")
            logger.debug("json_file_path:: %s", json_file_path)

            with open(json_file_path, "w") as outfile:
                json.dump(data, outfile)

            return data

        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    @staticmethod
    def get_complete_anilist_info(page):
        try:
            url = f"{ModelSetting.get('linkkf_url')}/anime-list/page/{page}"

            html_content = LogicLinkkfYommi.get_html(url)
            # html_content = LogicLinkkfYommi.get_html_cloudflare(url)
            download_path = ModelSetting.get("download_path")
            tree = html.fromstring(html_content)
            # tmp_items = tree.xpath('//div[@class="item"]')
            tmp_items = tree.xpath('//div[@class="myui-vodlist__box"]')
            title_xpath = './/a[@class="text-fff"]//text()'
            # logger.info('tmp_items:::', tmp_items)

            data = {"ret": "success", "page": page}

            data["episode_count"] = len(tmp_items)
            logger.debug(f'episode_count:: {data["episode_count"]}')
            data["episode"] = []

            if tree.xpath('//*[@id="wp_page"]//text()'):
                data["total_page"] = tree.xpath('//div[@id="wp_page"]//text()')[-1]
            else:
                data["total_page"] = 0

            for item in tmp_items:
                entity = {}
                entity["link"] = item.xpath(".//a/@href")[0]
                # logger.debug(f"link()::entity['link'] => {entity['link']}")
                entity["code"] = re.search(r"[0-9]+", entity["link"]).group()
                entity["title"] = item.xpath(title_xpath)[0].strip()
                entity["image_link"] = item.xpath("./a/@data-original")[0]
                entity["chapter"] = (
                    item.xpath("./a/span//text()")[0]
                    if len(item.xpath("./a/span//text()")) > 0
                    else ""
                )
                # entity["link"] = item.xpath(".//a/@href")[0]
                # entity["code"] = re.search(r"[0-9]+", entity["link"]).group()
                # entity["title"] = item.xpath('.//span[@class="name-film"]//text()')[
                #     0
                # ].strip()
                # entity["image_link"] = item.xpath(
                #     './/img[@class="photo"]/@data-lazy-src'
                # )[0]
                # logger.info('entity:::', entity['title'])
                data["episode"].append(entity)

            # json_file_path = os.path.join(download_path, "airing_list.json")
            # logger.debug("json_file_path:: %s", json_file_path)
            #
            # with open(json_file_path, "w") as outfile:
            #     json.dump(data, outfile)

            return data

        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    @staticmethod
    def get_title_info(code):
        try:
            if (
                LogicLinkkfYommi.current_data is not None
                and LogicLinkkfYommi.current_data["code"] == code
                and LogicLinkkfYommi.current_data["ret"]
            ):
                return LogicLinkkfYommi.current_data
            url = "%s/%s" % (ModelSetting.get("linkkf_url"), code)
            logger.info(url)

            # logger.debug(f"LogicLinkkfYommi.headers: {LogicLinkkfYommi.headers}")

            html_content = LogicLinkkfYommi.get_html(url, cached=False)
            # html_content = LogicLinkkfYommi.get_html_playwright(url)
            # html_content = LogicLinkkfYommi.get_html_cloudflare(url, cached=False)

            sys.setrecursionlimit(10**7)
            # logger.info(html_content)
            tree = html.fromstring(html_content)
            # tree = etree.fromstring(
            #     html_content, parser=etree.XMLParser(huge_tree=True)
            # )
            # tree1 = BeautifulSoup(html_content, "lxml")

            soup = BeautifulSoup(html_content, "html.parser")
            # tree = etree.HTML(str(soup))
            # logger.info(tree)

            data = {"code": code, "ret": False}

            tmp2 = soup.select("ul > a")
            if len(tmp2) == 0:
                tmp = soup.select("u > a")
            else:
                tmp = soup.select("ul > a")

            # logger.debug(f"tmp1 size:=> {str(len(tmp))}")

            try:
                tmp = (
                    tree.xpath('//div[@class="hrecipe"]/article/center/strong')[0]
                    .text_content()
                    .strip()
                )
            except IndexError:
                tmp = tree.xpath("//article/center/strong")[0].text_content().strip()

            # print(tmp)
            # logger.info(tmp)
            match = re.compile(r"(?P<season>\d+)기").search(tmp)
            if match:
                data["season"] = match.group("season")
            else:
                data["season"] = "1"

            # replace_str = f'({data["season"]}기)'
            # logger.info(replace_str)
            data["_id"] = str(code)
            data["title"] = tmp.replace(data["season"] + "기", "").strip()
            data["title"] = data["title"].replace("()", "").strip()
            data["title"] = (
                Util.change_text_for_use_filename(data["title"])
                .replace("OVA", "")
                .strip()
            )
            # logger.info(f"title:: {data['title']}")
            try:
                data["poster_url"] = tree.xpath(
                    '//div[@class="myui-content__thumb"]/a/@data-original'
                )
                # print(tree.xpath('//div[@class="myui-content__detail"]/text()'))
                if len(tree.xpath('//div[@class="myui-content__detail"]/text()')) > 3:
                    data["detail"] = [
                        {
                            "info": tree.xpath(
                                '//div[@class="myui-content__detail"]/text()'
                            )[3]
                        }
                    ]
                else:
                    data["detail"] = [{"정보없음": ""}]
            except Exception as e:
                logger.error(e)
                data["detail"] = [{"정보없음": ""}]
                data["poster_url"] = None

            data["rate"] = tree.xpath('span[@class="tag-score"]')

            tag_score = tree.xpath('//span[@class="taq-score"]')[0].text_content()
            # logger.debug(tag_score)
            tag_count = (
                tree.xpath('//span[contains(@class, "taq-count")]')[0]
                .text_content()
                .strip()
            )
            data_rate = tree.xpath('//div[@class="rating"]/div/@data-rate')

            tmp2 = soup.select("ul > a")
            if len(tmp) == 0:
                tmp = soup.select("u > a")
            else:
                tmp = soup.select("ul > a")

            if tmp is not None:
                data["episode_count"] = str(len(tmp))
            else:
                data["episode_count"] = "0"

            data["episode"] = []
            # tags = tree.xpath(
            #     '//*[@id="syno-nsc-ext-gen3"]/article/div[1]/article/a')
            # tags = tree.xpath("//ul/a")
            tags = soup.select("ul > u > a")
            if len(tags) > 0:
                pass
            else:
                tags = soup.select("ul > a")

            logger.debug(len(tags))

            # logger.info("tags", tags)
            # re1 = re.compile(r'\/(?P<code>\d+)')
            re1 = re.compile(r"\-([^-])+\.")

            data["save_folder"] = data["title"]
            # logger.debug(f"save_folder::> {data['save_folder']}")

            program = (
                db.session.query(ModelLinkkfProgram).filter_by(programcode=code).first()
            )

            if program is None:
                program = ModelLinkkfProgram(data)
                db.session.add(program)
                db.session.commit()
            else:
                data["save_folder"] = program.save_folder
                data["season"] = program.season

            idx = 1
            for t in tags:
                entity = {
                    "_id": data["code"],
                    "program_code": data["code"],
                    "program_title": data["title"],
                    "save_folder": Util.change_text_for_use_filename(
                        data["save_folder"]
                    ),
                    "title": t.text.strip(),
                    # "title": t.text_content().strip(),
                }
                # entity['code'] = re1.search(t.attrib['href']).group('code')

                # logger.debug(f"title ::>{entity['title']}")

                # 고유id임을 알수 없는 말도 안됨..
                # 에피소드 코드가 고유해야 상태값 갱신이 제대로 된 값에 넣어짐
                p = re.compile(r"([0-9]+)화?")
                m_obj = p.match(entity["title"])
                # logger.info(m_obj.group())
                # entity['code'] = data['code'] + '_' +str(idx)

                episode_code = None
                # logger.debug(f"m_obj::> {m_obj}")
                if m_obj is not None:
                    episode_code = m_obj.group(1)
                    entity["code"] = data["code"] + episode_code.zfill(4)
                else:
                    entity["code"] = data["code"]

                # logger.info('episode_code', episode_code)
                # entity["url"] = t.attrib["href"]
                check_url = t["href"]
                if check_url.startswith("http"):
                    entity["url"] = t["href"]
                else:
                    entity["url"] = f"{ModelSetting.get('linkkf_url')}{t['href']}"
                entity["season"] = data["season"]

                # 저장경로 저장
                tmp_save_path = ModelSetting.get("download_path")
                if ModelSetting.get("auto_make_folder") == "True":
                    program_path = os.path.join(tmp_save_path, entity["save_folder"])
                    entity["save_path"] = program_path
                    if ModelSetting.get("linkkf_auto_make_season_folder"):
                        entity["save_path"] = os.path.join(
                            entity["save_path"], "Season %s" % int(entity["season"])
                        )

                data["episode"].append(entity)
                entity["image"] = data["poster_url"]

                entity["filename"] = LogicLinkkfYommi.get_filename(
                    data["save_folder"], data["season"], entity["title"]
                )
                idx = idx + 1
            data["ret"] = True
            # logger.info('data', data)
            LogicLinkkfYommi.current_data = data

            # srt 파일 처리

            return data
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
            data["log"] = str(e)
            data["ret"] = "error"
            return data
        except IndexError as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())
            data["log"] = str(e)
            data["ret"] = "error"
            return data

    @staticmethod
    def get_filename(maintitle, season, title):
        try:
            # logger.debug("get_filename()===")
            # logger.info("title:: %s", title)
            # logger.info("maintitle:: %s", maintitle)
            match = re.compile(
                r"(?P<title>.*?)\s?((?P<season>\d+)기)?\s?((?P<epi_no>\d+)화?)"
            ).search(title)
            if match:
                epi_no = int(match.group("epi_no"))
                if epi_no < 10:
                    epi_no = "0%s" % epi_no
                else:
                    epi_no = "%s" % epi_no

                if int(season) < 10:
                    season = "0%s" % season
                else:
                    season = "%s" % season

                # title_part = match.group('title').strip()
                # ret = '%s.S%sE%s%s.720p-SA.mp4' % (maintitle, season, epi_no, date_str)
                ret = "%s.S%sE%s.720p-LK.mp4" % (maintitle, season, epi_no)
            else:
                logger.debug("NOT MATCH")
                ret = "%s.720p-LK.mp4" % maintitle

            return Util.change_text_for_use_filename(ret)
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    @staticmethod
    def download_subtitle(info):
        # logger.debug(info)
        ani_url = LogicLinkkfYommi.get_video_url(info["url"])
        # logger.debug(f"ani_url: {ani_url}")

        referer = None

        # vtt file to srt file
        from framework.common.util import write_file, convert_vtt_to_srt
        from urllib import parse

        if ani_url[1] is not None:
            referer = ani_url[1]

        logger.debug(f"referer:: {referer}")
        referer = "https://kfani.me"

        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/71.0.3554.0 Safari/537.36Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3554.0 Safari/537.36",
            "Referer": f"{referer}",
        }
        # logger.debug(headers)

        save_path = ModelSetting.get("download_path")
        if ModelSetting.get("auto_make_folder") == "True":
            program_path = os.path.join(save_path, info["save_folder"])
            save_path = program_path
            if ModelSetting.get("linkkf_auto_make_season_folder"):
                save_path = os.path.join(save_path, "Season %s" % int(info["season"]))

        ourls = parse.urlparse(ani_url[1])
        # print(ourls)
        # logger.info('ourls:::>', ourls)
        base_url = f"{ourls.scheme}://{ourls.netloc}"
        # logger.info('base_url:::>', base_url)

        # vtt_url = base_url + ani_url[2]
        # https://kfani.me/s/354776m5.vtt
        vtt_url = "https://kfani.me" + ani_url[2]

        # logger.debug(f"srt:url => {vtt_url}")
        srt_filepath = os.path.join(
            save_path, info["filename"].replace(".mp4", ".ko.srt")
        )
        # logger.info('srt_filepath::: %s', srt_filepath)
        if ani_url[2] is not None and not os.path.exists(srt_filepath):
            res = requests.get(vtt_url, headers=headers)
            vtt_data = res.text
            vtt_status = res.status_code
            if vtt_status == 200:
                srt_data = convert_vtt_to_srt(vtt_data)
                write_file(srt_data, srt_filepath)
            elif vtt_status == 404:
                pass
            else:
                logger.debug("자막 파일 받을수 없슴")

    @staticmethod
    def chunks(l, n):
        n = max(1, n)
        return (l[i : i + n] for i in range(0, len(l), n))

    @staticmethod
    def get_info_by_code(code):
        logger.debug("get_info_by_code: %s", code)

        try:
            if LogicLinkkfYommi.current_data is not None:
                for t in LogicLinkkfYommi.current_data["episode"]:
                    if t["code"] == code:
                        return t
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    @staticmethod
    def scheduler_function():
        try:
            logger.debug("Linkkf scheduler_function start..")

            whitelist_program = ModelSetting.get("whitelist_program")
            whitelist_programs = [
                x.strip().replace(" ", "")
                for x in whitelist_program.replace("\n", ",").split(",")
            ]

            logger.debug(f"whitelist_programs: {whitelist_programs}")

            for code in whitelist_programs:
                logger.info("auto download start : %s", code)
                downloaded = (
                    db.session.query(ModelLinkkf)
                    .filter(ModelLinkkf.completed.is_(True))
                    .filter_by(programcode=code)
                    .with_for_update()
                    .all()
                )
                logger.debug(f"downloaded:: {downloaded}")
                dl_codes = [dl.episodecode for dl in downloaded]
                # logger.debug("dl_codes:: %s", dl_codes)
                logger.info("downloaded codes :%s", dl_codes)

                # if len(dl_codes) > 0:
                data = LogicLinkkfYommi.get_title_info(code)
                logger.debug(f"data:: {data}")

                for episode in data["episode"]:
                    e_code = episode["code"]
                    if e_code not in dl_codes:
                        logger.info("Logic Queue added :%s", e_code)

                        logger.debug(f"episode:: {episode}")
                        print("temp==============")
                        LogicQueue.add_queue(episode)

            logger.debug("========================================")
        except Exception as e:
            logger.error("Exception:%s", e)
            logger.error(traceback.format_exc())

    @staticmethod
    def reset_db() -> bool:
        db.session.query(ModelLinkkf).delete()
        db.session.commit()
        return True
