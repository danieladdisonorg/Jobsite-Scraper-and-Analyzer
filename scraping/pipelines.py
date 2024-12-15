# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import dotenv
from datetime import date
from scrapy import Item, Spider

import pandas as pd

from common.db.models import ScrapingResultFileMetaData
from common.db.connnect_db import session

dotenv.load_dotenv()


class FeatherMySQLItemPipeline:
    """
    Item Pipeline for storing metedata in MySQL (like
     date of file creation, name of file etc.) and formating and storing
    result of scraping in format Feather.
    """
    def __init__(self) -> None:
        self.items = []
        self.result_dir = os.getenv("SCRAPING_RESULT_DIR")

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

    def process_item(self, item: Item, spider: Spider) -> Item:
        serialized_item = self.serialize_item(item)
        self.items.append(serialized_item)
        return item

    def close_spider(self, spider: Spider) -> None:
        """
        Convert scraped items to Feather format and save metadat to MySQL DB.
        :param spider:
        :return:
        """
        df = pd.DataFrame(self.items)

        created_at = date.today().strftime('%Y_%m_%d')
        file_name = f"vacancies_{created_at}.feather"

        # saving scraped data in feather file, because I do not have
        # Cloud Storage where I could save files.
        df.to_feather(path=os.path.join(self.result_dir, file_name))

        # save metadata about created scraping result in DB
        result_metadata = ScrapingResultFileMetaData(
            file_name=file_name,
            created_at=created_at
        )
        session.add(result_metadata)
        session.commit()
        session.close()
