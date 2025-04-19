from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class NewsSchema(BaseModel):
    title: str
    description: str
    url: Optional[str]
    published_at: datetime
    created_at: datetime
    created_by: int

    class Config:
        orm_mode = True
