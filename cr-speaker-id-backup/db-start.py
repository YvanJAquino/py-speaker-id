import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from modules.sql_models import create_tables

# Reserved for database configuration
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")
DB_CNST = os.environ.get("DB_CNST") # DB_CNST = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Database engine and session objects
engine = create_engine(DB_CNST)
Session = sessionmaker(engine)

# Create the tables!
create_tables(engine)

print("Tables created.  please check your DB.")