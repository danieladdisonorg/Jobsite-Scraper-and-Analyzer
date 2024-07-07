import os
import dotenv

dotenv.load_dotenv()


class Config:
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Scheduling scraping x number of days
    SCRAPING_EVERY_NUM_DAY = 7

    # directory in which scraping results are contained
    SCRAPING_RESULT_DIR = os.getenv("SCRAPING_RESULT_DIR")

    # database configurations
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(basedir, "db.sqlite3")
    # SQLALCHEMY_TRACK_MODIFICATIONS = False

    # PAGINATION_MAX_PER_PAGE = 10


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")

    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True


class Debug(Config):
    DEBUG = True


config_dict = {"production": ProductionConfig, "debug": Debug}