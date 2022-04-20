
# Nintendo Eshop Crawler

任天堂Eshop 相关信息爬虫，请结合[switch_etl](https://github.com/user919lx/switch_etl)使用

支持爬取的内容：

* 已开放eshop的国家/地区
* 日区、美区、港区、欧区的游戏信息
* 所有可用商店的游戏价格

**注：因为港服页面提供的游戏清单太少，这个部分的数据有大量缺失，还在寻找新的方案**


## 使用前的配置

### 爬虫相关配置

* 修改位于`switch/settings.py`下的`MYSQL_CONFIG`，填入你自己的MySQL数据库参数
* 安装pipenv，并切换到项目环境下使用，已配置好`Pipfile`


### MySQL建表

查看`switch/ddl`，复制ddl建表
* eshop: 记录eshop开放的国家/地区
* game_raw: 存储爬取到的游戏信息原始数据
* price_raw: 存储爬取到的价格信息原始数据

## 使用方法

使用pipenv进入项目环境

```bash
cd switch
scrapy crawl xxx # 替换成自己需要的
```

### crawler列表


* eshop_spider: 获取可用商店，存入eshop表
* game_deku_spider:获取dekudeals.com网站的的游戏信息。此网站仅作为数据补充，主要补充多人游戏信息，媒体评分，游戏时长信息。从美区游戏列表同步，每个游戏只获取一次。
* game_eu_spider: 获取欧区游戏信息，存入game_raw，region='eu'
* game_hk_spider: 获取港区游戏信息，存入game_raw，region='hk'
* game_jp_spider: 获取日区游戏信息，存入game_raw，region='jp'
* price: 获取价格信息，存入price_raw

注：美区的数据获取较麻烦，放在项目switch_etl中
