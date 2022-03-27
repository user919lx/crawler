from scrapy import Spider
from switch.db import MySQLStorage
from switch.settings import MYSQL_CONFIG
from scrapy import FormRequest
from switch.items import GameNAMultItem
from bs4 import BeautifulSoup
import re


class GameNAMultSpider(Spider):
    name = "game_na_mult"

    custom_settings = {"CONCURRENT_REQUESTS_PER_DOMAIN": "1", "DOWNLOAD_DELAY": "1"}

    def __init__(self):
        self.db = MySQLStorage(MYSQL_CONFIG)

    def start_requests(self):
        self.db.open()
        rows = self.db.fetchall("game_na")
        for row in rows:
            url = row["url"]
            yield FormRequest(url=url, method="GET", callback=self.parse)

    def parse(self, response):
        url = response.url
        data = {
            "url": url,
            "local": None,
            "wireless": None,
            "online": None,
        }

        soup = BeautifulSoup(response.text, "html.parser")
        alist = soup.find_all(
            lambda tag: tag.name == "a"
            and bool(tag.attrs.get("href"))
            and bool(re.search(r"search.*playerCount", tag.attrs.get("href")))
        )
        pat_local = re.compile(r"Single System \((.*)\)")
        pat_wireless = re.compile(r"Local wireless \((.*)\)")
        pat_online = re.compile(r"Online \((.*)\)")
        for a in alist:
            text = a.text.strip()
            m_local = pat_local.search(text)
            m_wireless = pat_wireless.search(text)
            m_online = pat_online.search(text)
            if m_local:
                data["local"] = m_local.group(1)
            if m_wireless:
                data["wireless"] = m_wireless.group(1)
            if m_online:
                data["online"] = m_online.group(1)
        item = GameNAMultItem(**data)
        yield item
