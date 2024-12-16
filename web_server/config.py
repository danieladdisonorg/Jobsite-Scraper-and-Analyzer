import os
import dotenv
from datetime import timedelta

dotenv.load_dotenv()


class Config:
    basedir = os.path.abspath(os.path.dirname(__file__))

    # set cache time for querying DB for scraping data file names
    # which allows users to choose files it wants to analyze
    # and since we are scraping every number of day 'SCRAPING_EVERY_NUM_DAY'
    # that means we will update choices for users as soon as new
    # scraping data file is created
    FILES_NAME_CHOICES_CACHE_TIME = timedelta(
        days=float(os.getenv("SCRAPING_EVERY_NUM_DAY"))
    )
    EXPLAIN_TEMPLATE_LOADING = False

    SECRET_KEY = os.getenv("SECRET_KEY")

    # database configurations
    SQLALCHEMY_DATABASE_URL = "sqlite:///" + os.path.join(basedir, "db.sqlite3")
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    # PAGINATION_MAX_PER_PAGE = 10


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True


class Debug(Config):
    DEBUG = True
    EXPLAIN_TEMPLATE_LOADING = True


config_dict = {"production": ProductionConfig, "debug": Debug}
