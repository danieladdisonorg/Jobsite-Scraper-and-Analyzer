import os
import dotenv

from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from sqlalchemy import create_engine


dotenv.load_dotenv()

engine = create_engine(
    url=os.getenv("DATABASE_URL"),
    # TODO: find out am i actually using advantage of pool
    pool_size=10,  # Number of connections to keep in the pool
    max_overflow=20,  # Number of connections to allow in overflow
    # Number of seconds to wait before giving up on a connection
    pool_timeout=30,
    pool_recycle=1800  # Number of seconds to recycle a connection
)
session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine)
)

Base = declarative_base()
