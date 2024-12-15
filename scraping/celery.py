import os
import dotenv
from celery import Celery
from datetime import timedelta

dotenv.load_dotenv()


celery_app = Celery(
    "scraping",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND")
)

celery_app.conf.beat_schedule = {
    "scrapy_every_num_days": {
        "task": "scraping.task.start_scraping",
        "schedule": timedelta(
            days=int(os.getenv("SCRAPING_EVERY_NUM_DAY"))
        )
    }
}

celery_app.conf.timezone = "UTC"
