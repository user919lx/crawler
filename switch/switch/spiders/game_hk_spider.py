import re
import json
from scrapy import Spider
from switch.items import GameRawItem


class GameHKSpider(Spider):
    name = "game_hk"

    start_urls = ["https://www.nintendo.com.hk/data/json/switch_software.json"]

    def parse(self, response):
        jdict = response.json()
        for row in jdict:
            media = row["media"]
            link = row["link"]
            m = re.match(r"https://store.nintendo.com.hk/(\d+)", link)
            if media == "eshop" and m:
                unique_id = m.group(1)
                raw_str = json.dumps(row, ensure_ascii=True)
                item = GameRawItem(unique_id=unique_id, region="hk", raw_data=raw_str)
                yield item
