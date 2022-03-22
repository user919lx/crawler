from scrapy import Spider
from switch.items import GameRawItem
from scrapy import FormRequest
import json


class GameEUSpider(Spider):
    name = "game_eu"
    row_num_per_page = 100

    request_params = {
        "rows": str(row_num_per_page),
        "fq": "type:GAME AND system_type:nintendoswitch* AND product_code_txt:*",
        "q": "*",
        "sort": "sorting_title asc",
        "start": "0",
        "wt": "json",
    }
    url = "http://search.nintendo-europe.com/en/select"

    def start_requests(self):
        yield FormRequest(url=self.url, method="GET", formdata=self.request_params, callback=self.parse)

    def __parse_raw_dict(self, raw_dict):
        data = {
            "unique_id": raw_dict["fs_id"],
            "region": "eu",
            "raw_data": json.dumps(raw_dict, ensure_ascii=True),
        }
        return data

    def parse(self, response):
        jdict = response.json()["response"]
        for raw_dict in jdict["docs"]:
            data = self.__parse_raw_dict(raw_dict)
            item = GameRawItem(**data)
            yield item

        total_num = int(jdict["numFound"])
        offset = int(jdict["start"])
        page_num = int(offset / self.row_num_per_page)
        if (page_num + 1) * self.row_num_per_page < total_num:
            offset += self.row_num_per_page
            self.request_params["start"] = str(offset)
            yield FormRequest(url=self.url, method="GET", formdata=self.request_params, callback=self.parse)
