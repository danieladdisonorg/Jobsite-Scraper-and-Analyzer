import logging
from celery import shared_task
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from scraping.spiders.vc_scraper import VacancyScraper


logging.info("Tasks module loaded!")


@shared_task
def start_scraping():
    logging.info("Scraping task started!")

    process = CrawlerProcess(get_project_settings())
    process.crawl(VacancyScraper)
    process.start()

    logging.info("Scraping task finished!")
