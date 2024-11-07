from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

DB_USER = os.environ["DB_USER"]         # "gustavo" 
DB_PASS = os.environ["DB_PASSWORD"]     # "1234" 
DB_HOST = os.environ["DB_HOST"]         # "127.0.0.1" 
PORT = "5432"
DB_BASE = os.environ["DB_BASE"]         # "db_comp_aerea" 

# DB_USER = "gustavo" 
# DB_PASS = "1234" 
# DB_HOST = "127.0.0.1" 
# PORT = "5432"
# DB_BASE = "db_comp_aerea" 


SQLALCHEMY_DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{PORT}/{DB_BASE}"

logging.info("Subindo o banco de dados.")
engine = create_engine(SQLALCHEMY_DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
