# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
from datetime import datetime
from itemadapter import ItemAdapter
from scrapy import Item, Spider

from pyarrow import feather
import pandas as pd

from mysql import connector
from mysql.connector import errorcode


class FeatherMySQLItemPipeline:
    """
    Item Pipeline for storing metedata in MySQL (like
     date of file creation, name of file etc.) and formating and storing
    result of scraping in format Feather.
    """
    def __init__(self) -> None:
        self.items = []
        self.result_dir = "scraping_results"

    @staticmethod
    def serialize_item(item: Item) -> dict:
        return {
            field_name: (
                item.fields[field_name]["serializer"](field_value)
                if "serializer" in item.fields[field_name]
                else field_value
            )
            for field_name, field_value in item.items()
            if field_name in item.fields
        }

    def process_item(self, item: Item, spider: Spider) -> None:
        self.items.append(item)

    def close_spider(self, spider: Spider) -> None:
        """
        Convert scraped items to Feather format and save metadat to MySQL DB.
        :param spider:
        :return:
        """
        df = pd.DataFrame(self.items)

        file_name = f"vacancies_{datetime.utcnow().strftime('%Y_%m_%d')}.feather"
        df.to_feather(path=os.path.join(self.result_dir, file_name))
