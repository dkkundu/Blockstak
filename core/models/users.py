from sqlalchemy import Column, String, Integer, CheckConstraint
from config.mysql_connection import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    scope = Column(String(255))

    __table_args__ = (
        CheckConstraint('length(password) >= 8', name='password_min_length'),
    )