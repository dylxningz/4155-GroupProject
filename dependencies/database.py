from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dependencies.config import conf
from urllib.parse import quote_plus

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{conf.db_user}:{quote_plus(conf.db_password)}@{conf.db_host}:{conf.db_port}/?charset=utf8mb4"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

print("Checking Database...")
db = engine.connect()
db_table = db.execute(text(f"SHOW DATABASES LIKE '{conf.db_name}';")).fetchone()

# If result is None, the database doesn't exist, so create it
if db_table is None:
    print("Creating Database Table...")
    db.execute(text(f"CREATE DATABASE {conf.db_name};"))
    print("Database Table Created!")

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{conf.db_user}:{quote_plus(conf.db_password)}@{conf.db_host}:{conf.db_port}/{conf.db_name}?charset=utf8mb4"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

print("Database Setup Complete!")

def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
