import re

from bs4 import BeautifulSoup
from scrapy import FormRequest, Spider
from slugify import slugify
from switch.db import MySQLStorage
from switch.items import GameRawItem
from switch.settings import MYSQL_CONFIG
import html
import json


class GameDekuSpider(Spider):
    name = "game_deku"

    custom_settings = {"CONCURRENT_REQUESTS_PER_DOMAIN": "1", "DOWNLOAD_DELAY": "1"}

    slug_dict = {
        "Pokémon Sword + Pokémon Sword Expansion Pass": "pokmon-sword-plus-expansion-pass",
        "Pokémon Shield + Pokémon Shield Expansion Pass": "pokmon-shield-plus-expansion-pass",
        "BOXBOY! + BOXGIRL!": "boxboy-and-boxgirl",
    }

    def __init__(self):
        self.db = MySQLStorage(MYSQL_CONFIG)

    def __get_slug(self, text):
        map_slug = self.slug_dict.get(text)
        if map_slug:
            return map_slug
        text = re.sub("[™®]", "", text)
        slug = slugify(text, replacements=[["+", "plus"], ["〇", "o"], ["＆", "and"]])
        return slug

    def __get_name(self, soup):
        s = soup.find("title")
        name = "-".join(s.text.split("-")[:-1]).strip()
        return name

    def __get_price_data(self, soup):
        history_tag = soup.find("script", {"id": "price_history_data"})
        if history_tag:
            jdict = json.loads(history_tag.text)
            return json.dumps(jdict["data"])
        else:
            return "[]"

    def __get_next_sibling_text(self, tag):
        if tag.next_sibling:
            return html.unescape(tag.next_sibling.text)
        else:
            return None

    def __get_info(self, soup):
        item_list = soup.find_all("li", {"class": "list-group-item"})
        data = {}
        for item in item_list:
            strong = item.strong
            key = strong.text.replace(":", "").strip().lower().replace(" ", "_")
            if key in ["demo_available", "download_size", "esrb_rating", "play_modes", "languages"]:
                value = self.__get_next_sibling_text(strong)
                data[key] = value
            elif key in ["released", "number_of_players"]:
                if item.ul:
                    sub_data = []
                    for subitem in item.ul.find_all("li"):
                        sub_strong = subitem.strong
                        sub_key = sub_strong.text.replace(":", "")
                        sub_value = html.unescape(sub_strong.next_sibling.text)
                        sub_data.append({"key": sub_key.strip(), "value": sub_value.strip()})
                    data[key] = json.dumps(sub_data)
                else:
                    data[key] = self.__get_next_sibling_text(strong)
            elif key in ["genre"]:
                value = [a.text for a in item.find_all("a")]
                data[key] = value
            elif key in ["developer", "publisher"]:
                value = item.a.text
                data[key] = value
            elif key in ["metacritic"]:
                url = item.a.attrs["href"]
                span_list = item.find_all("span")
                data["metacritic_url"] = url
                data["metacritic_media"] = span_list[0].text.strip()
                data["metacritic_user"] = span_list[1].text.strip()
            elif key in ["how_long_to_beat"]:
                url = item.a.attrs["href"]
                data["how_long_to_beat_url"] = url
                sub_data = []
                for subitem in item.ul.find_all("li"):
                    sub_strong = subitem.strong
                    sub_key = sub_strong.text.replace(":", "")
                    sub_value = self.__get_next_sibling_text(sub_strong)
                    sub_data.append({"key": sub_key.strip(), "value": sub_value.strip()})
                data["how_long_to_beat"] = json.dumps(sub_data)
        return data

    def start_requests(self):
        self.db.open()
        sql = """
            select gn.name, gn.slug
                from (select *,replace(substring_index(url,'/',-2),'-switch/','') slug from game_na) gn
                left join (select unique_id from game_raw where region='deku') raw on gn.slug = raw.unique_id
            where raw.unique_id is null
            """
        rows = self.db.query(sql)
        self.db.close()
        origin_slug_set = set([row["slug"] for row in rows])
        parse_slug_set = set([self.__get_slug(row["name"]) for row in rows])
        all_slug_set = origin_slug_set | parse_slug_set
        for slug in all_slug_set:
            url = f"https://www.dekudeals.com/items/{slug}"
            yield FormRequest(url=url, method="GET", callback=self.parse)

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")
        slug = response.url.split("/")[-1]
        name = self.__get_name(soup)
        if "Search - " not in name:
            info_data = self.__get_info(soup)
            history_price_data = self.__get_price_data(soup)
            data = {"name": name, "history_price": history_price_data}
            data.update(info_data)
            raw_str = json.dumps(data, ensure_ascii=True)
            item = GameRawItem(unique_id=slug, region="deku", raw_data=raw_str)
            yield item
