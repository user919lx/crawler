from scrapy import Spider
from switch.db import MySQLStorage
from switch.settings import MYSQL_CONFIG
from urllib.parse import urlparse, parse_qs
from scrapy import FormRequest
import json
from switch.items import PriceItem


class PriceSpider(Spider):
    name = "price"

    price_url = "https://api.ec.nintendo.com/v1/price"
    custom_settings = {"CONCURRENT_REQUESTS_PER_DOMAIN": "1", "DOWNLOAD_DELAY": "1"}

    def __init__(self):
        self.db = MySQLStorage(MYSQL_CONFIG)

    def start_requests(self):
        self.db.open()
        rows = self.db.fetchall("eshop", filter_clause="is_active=1")
        region_alpha2_list = {}
        for row in rows:
            alpha2 = row["alpha2"]
            region = row["region"]
            if not region_alpha2_list.get(region):
                region_alpha2_list[region] = []
            region_alpha2_list[region].append(alpha2)

        region_data_list = []
        for region, alpha2_list in region_alpha2_list.items():
            nsuid_list = [row["nsuid"] for row in self.db.fetchall(f"game_{region}") if row["nsuid"]]
            data = {
                "region": region,
                "alpha2_list": alpha2_list,
                "nsuid_list": nsuid_list,
            }
            region_data_list.append(data)
        self.db.close()
        for data in region_data_list:
            alpha2_list = data["alpha2_list"]
            nsuid_list = data["nsuid_list"]
            nsuid_count = len(nsuid_list)
            count_per_page = 50
            page_count = int(nsuid_count / count_per_page)+1
            for page in range(page_count+1):
                idx1 = page * count_per_page
                idx2 = (page + 1) * count_per_page
                nsuid_slice = nsuid_list[idx1:idx2]
                for alpha2 in alpha2_list:
                    if nsuid_slice:
                        params = {"lang": "en", "ids": nsuid_slice, "country": alpha2}
                        yield FormRequest(url=self.price_url, method="GET", formdata=params, callback=self.parse)

    def parse(self, response):
        alpha2 = parse_qs(urlparse(response.url).query)["country"][0]
        if response.status == 200:
            jdict = json.loads(response.text)
            if jdict.get("prices"):
                for row in jdict.get("prices"):
                    data = {"nsuid": row["title_id"], "alpha2": alpha2, "raw_data": json.dumps(row, ensure_ascii=True)}
                    item = PriceItem(**data)
                    yield item


# class PriceItem(Item):
#     nsuid = Field()
#     alpha2 = Field()
#     raw_data = Field()
