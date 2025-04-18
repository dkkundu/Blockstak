from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, declarative_base
from core.models.users import User
from config.mysql_connection import Base

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(225))
    description = Text()
    url = Column(String(225), nullable=True)
    published_at = Column(DateTime)
    created_at = Column(DateTime)
    created_by = Column(Integer, ForeignKey(User.id))

    user = relationship(User)
