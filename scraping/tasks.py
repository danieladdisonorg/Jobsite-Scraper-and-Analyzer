import os
from dotenv import load_dotenv
import logging
from datetime import timedelta
from typing import Any

from celery import shared_task, Celery
from celery.signals import worker_ready
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from scraping.spiders.vc_scraper import VacancyScraper
from main_celery.celery import celery_app

load_dotenv()
logging.info("Tasks module loaded!")


@shared_task(queue="scraping_queue")
def start_scraping():
    logging.info("Scraping task started!")

    process = CrawlerProcess(get_project_settings())
    process.crawl(VacancyScraper)
    process.start()

    logging.info("Scraping task finished!")


@worker_ready.connect
def at_start(sender: Celery, **kwargs: Any):
    """Run this task when worker is ready"""
    with sender.app.connection() as conn:
        # Run task as soon as worker ready
        sender.app.send_task("scraping.tasks.start_scraping", connection=conn)


# set up scraping_schedule schedule to run every 'SCRAPING_EVERY_DAYS'
celery_app.conf.beat_schedule.update({
    "scrapy_every_num_days": {
        "task": "scraping.tasks.start_scraping",
        "schedule": timedelta(
            days=int(
                # by default 7 days is max
                os.getenv("SCRAPING_EVERY_DAYS", 604800)
            ),
        )
    }
})
