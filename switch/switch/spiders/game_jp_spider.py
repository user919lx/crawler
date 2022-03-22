import json

from bs4 import BeautifulSoup
from scrapy import Spider
from switch.items import GameRawItem


class GameJPSpider(Spider):
    name = "game_jp"

    start_urls = ["https://www.nintendo.co.jp/data/software/xml/switch.xml"]

    def __parse_raw_data(self, game):
        raw_data = {}
        for col in game.children:
            key = col.name
            value = col.text
            if key == "linkurl":
                nsuid = value.split("/")[-1]
                raw_data["nsuid"] = nsuid
                raw_data["url"] = f"https://ec.nintendo.com/JP/ja/titles/{nsuid}"
            else:
                raw_data[key] = value
        return raw_data

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        game_list = list(soup.children)[1].children
        for game in game_list:
            raw_data = self.__parse_raw_data(game)
            nsuid = raw_data["nsuid"]
            if nsuid:
                item = GameRawItem(unique_id=nsuid, region="jp", raw_data=json.dumps(raw_data, ensure_ascii=True))
                yield item
