# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from switch.db import MySQLStorage


class MySQLPipeline:
    def __init__(self, mysql_config):
        self.storage = MySQLStorage(mysql_config)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get("MYSQL_CONFIG"))

    def open_spider(self, spider):
        self.storage.open()

    def close_spider(self, spider):
        self.storage.close()

    def process_item(self, item, spider):
        item_dict = ItemAdapter(item).asdict()
        if spider.name == "eshop":
            self.storage.save("eshop", item_dict)
        elif spider.name == "price":
            self.storage.save("price_raw", item_dict)
        elif spider.name in ("game_eu", "game_hk", "game_jp"):
            self.storage.save("game_raw", item_dict, compress_keys=["raw_data"])
        elif spider.name == "game_na_mult":
            self.storage.save("game_na_mult", item_dict)
        return item
