import os
import dotenv
from celery import Celery

dotenv.load_dotenv()


celery_app = Celery(
    "main_celery",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND")
)

# Route 'scraping' and 'web_server' tasks to queues
celery_app.conf.task_routes = {
    "scraping.tasks.*": {"queue": "scraping_queue"},
    "web_server.tasks.*": {"queue": "web_server_queue"},
}

# Define Queues
celery_app.conf.task_queues = {
    "scraping_queue": {"binding_key": "scraping_queue"},
    "web_server_queue": {"binding_key": "web_server_queue"},
}

# Allow tasks to register schedules
celery_app.conf.update(timezone="UTC")

# register tasks
celery_app.autodiscover_tasks()
