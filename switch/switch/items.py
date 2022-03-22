from scrapy.item import Item, Field


class EshopItem(Item):
    country = Field()
    alpha2 = Field()
    currency = Field()
    region = Field()
    is_active = Field()


class GameRawItem(Item):
    unique_id = Field()
    region = Field()
    raw_data = Field()


class GameJPItem(Item):
    nsuid = Field()
    code = Field()
    name = Field()
    maker = Field()
    makerkana = Field()
    price = Field()
    release_date = Field()
    soft_type = Field()
    platform_id = Field()
    dliconflg = Field()
    url = Field()
    img = Field()


class PriceItem(Item):
    nsuid = Field()
    alpha2 = Field()
    raw_data = Field()
