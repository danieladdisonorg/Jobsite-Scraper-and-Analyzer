from scraping import tasks as scr_tasks
from web_server import tasks as web_tasks

"""
Allow Celery to discover tasks
"""

__all__ = ["scr_tasks", "web_tasks"]
