from scrapy import Spider
from scrapy import FormRequest
import json
from switch.items import EshopItem
from switch.constants import REGIONS, COUNTRY_REGION
import iso3166
from urllib.parse import urlparse, parse_qs


class EshopSpider(Spider):
    name = "eshop"

    custom_settings = {"CONCURRENT_REQUESTS_PER_DOMAIN": "1", "DOWNLOAD_DELAY": "1", "HTTPERROR_ALLOWED_CODES": [404]}

    def start_requests(self):
        region_check_nsuid = {
            "hk": "70010000033861",
            "jp": "70010000038434",
            "na": "70010000000185",
            "eu": "70010000000184",
        }
        url = "https://api.ec.nintendo.com/v1/price"
        for region, country_list in REGIONS.items():
            nsuid = region_check_nsuid[region]
            for alpha2 in country_list:
                params = {"lang": "en", "ids": [nsuid], "country": alpha2}
                yield FormRequest(url=url, method="GET", formdata=params, callback=self.parse)

    def parse(self, response):
        alpha2 = parse_qs(urlparse(response.url).query)["country"][0]
        country = iso3166.countries_by_alpha2[alpha2].name
        region = COUNTRY_REGION[alpha2]
        data = {
            "country": country,
            "alpha2": alpha2,
            "currency": None,
            "region": region,
            "is_active": False,
        }
        if response.status == 200:
            jdict = json.loads(response.text)
            if jdict.get("prices"):
                data["is_active"] = True
                if jdict["prices"][0]["sales_status"] != "not_found":
                    data["currency"] = jdict["prices"][0]["regular_price"]["currency"]
                else:
                    data["currency"] = None
        item = EshopItem(**data)
        return item
