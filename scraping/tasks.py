import os
import logging
from datetime import timedelta

from celery import shared_task
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from scraping.spiders.vc_scraper import VacancyScraper


logging.info("Tasks module loaded!")


@shared_task(queue="scraping_queue")
def start_scraping():
    logging.info("Scraping task started!")

    process = CrawlerProcess(get_project_settings())
    process.crawl(VacancyScraper)
    process.start()

    logging.info("Scraping task finished!")


# set up scraping_schedule schedule to run every 'SCRAPING_EVERY_NUM_DAY'
start_scraping_schedule = {
    "scrapy_every_num_days": {
        "task": "scraping.task.start_scraping",
        "schedule": timedelta(
            days=int(os.getenv("SCRAPING_EVERY_NUM_DAY"))
        )
    }
}

# also when web application is up.
# We should run 'start_scraping' manually ones
# and next run we wait every 'SCRAPING_EVERY_NUM_DAY'.
start_scraping.delay()
