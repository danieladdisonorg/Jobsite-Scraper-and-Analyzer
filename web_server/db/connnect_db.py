import os
import dotenv

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


dotenv.load_dotenv()

engine = create_engine(url=os.getenv("DATABASE_URI"))
session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
