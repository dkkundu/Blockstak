# config/mysql_connection.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from .settings import get_settings

settings = get_settings()

# ✅ mysql+mysqldb is correct for mysqlclient
DATABASE_URL = (
    f"mysql+mysqldb://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}"
    f"@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}"
)
# Create engine using mysqlclient
engine = create_engine(DATABASE_URL, echo=True)
# Session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Declarative base class
Base = declarative_base()

# Dependency for FastAPI routes
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

