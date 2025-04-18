import requests
from fastapi import APIRouter, Depends, status
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from config.mysql_connection import  get_db, engine
from .models import Base, News
from .schemas import NewsSchema
from fastapi.encoders import jsonable_encoder
from abstract.time_convart import convert_utc_to_local
from config.settings import get_settings
from abstract.api_responces import Helper
from core.oauth2 import get_current_client
from core.models import User
from config.logger import logger

settings = get_settings()
response_data = Helper()
Base.metadata.create_all(bind=engine)
news_api_v1 = APIRouter()


NEWS_API_KEY = settings.NEWS_API_KEY # 🔐 replace with your actual key
NEWSAPI_BASE = "https://newsapi.org/v2"


# GET /news
@news_api_v1.get("/", response_model=List[NewsSchema])
def get_news(
    db: Session = Depends(get_db), skip: int = 0, limit: int = 10, _: None = Depends(get_current_client)
):
    logger.debug(f"Fetching news with skip={skip}, limit={limit}")
    news_items = db.query(News).offset(skip).limit(limit).all()
    logger.info(f"Fetched {len(news_items)} news items from DB")
    return response_data.success_response(
        status_code=200,
        data=jsonable_encoder(news_items),
        message="News fetched successfully"
    )


# POST /news/save-latest
@news_api_v1.post("/save-latest")
def save_latest_news(db: Session = Depends(get_db), current_user: User = Depends(get_current_client)):
    url = f"{NEWSAPI_BASE}/top-headlines?country=us&pageSize=3&apiKey={NEWS_API_KEY}"
    logger.debug(f"Fetching latest news from: {url}")
    response = requests.get(url)

    if response.status_code != 200:
        logger.error(f"Failed to fetch news: {response.status_code} - {response.text}")
        return response_data.error_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Failed to fetch news",
            errors=[{"message": "Failed to fetch news"}]
        )

    news_data = response.json().get("articles", [])
    saved = 0
    for article in news_data:
        logger.debug(f"Processing article: {article['title']}")
        if db.query(News).filter(News.url == article["url"]).first():
            logger.info(f"Article already exists in DB: {article['url']}")
            continue
        news = News(
            title=article["title"],
            description=article["description"],
            url=article["url"],
            published_at=convert_utc_to_local(article["publishedAt"]),
            created_at=datetime.date(datetime.now()),
            created_by=current_user.id,
        )
        db.add(news)
        saved += 1
        if saved == 3:
            break

    db.commit()
    logger.info(f"Saved {saved} new articles")
    return response_data.success_response(
        status_code=200,
        data={"saved": saved},
        message="Latest news saved successfully"
    )


# GET /news/headlines/country/{country_code}
@news_api_v1.get("/headlines/country/{country_code}")
def headlines_by_country(country_code: str, _: None = Depends(get_current_client)):
    url = f"{NEWSAPI_BASE}/top-headlines?country={country_code}&apiKey={NEWS_API_KEY}"
    logger.debug(f"Fetching headlines for country: {country_code}")
    response = requests.get(url)
    if response.status_code == 200:
        logger.info(f"Successfully fetched headlines for country: {country_code}")
        return response_data.success_response(
            status_code=200,
            data=response.json(),
            message="News fetched successfully"
        )
    else:
        logger.error(f"Failed to fetch country headlines: {response.status_code} - {response.text}")
        return response_data.error_response(
            status_code=response.status_code,
            message=str(response.json().get("message")),
            errors=[{"detail": response.text}]
        )


# GET /news/headlines/source/{source_id}
@news_api_v1.get("/headlines/source/{source_id}")
def headlines_by_source(source_id: str, _: None = Depends(get_current_client)):
    url = f"{NEWSAPI_BASE}/top-headlines?sources={source_id}&apiKey={NEWS_API_KEY}"
    logger.debug(f"Fetching headlines for source: {source_id}")
    response = requests.get(url)
    if response.status_code == 200:
        logger.info(f"Successfully fetched headlines for source: {source_id}")
        return response_data.success_response(
            status_code=200,
            data=response.json(),
            message="News fetched successfully"
        )
    else:
        logger.error(f"Failed to fetch source headlines: {response.status_code} - {response.text}")
        return response_data.error_response(
            status_code=response.status_code,
            message=str(response.json().get("message")),
            errors=[{"detail": response.text}]
        )


# GET /news/headlines/filter?country=xx&source=yy
@news_api_v1.get("/headlines/filter")
def filter_headlines(
        country: Optional[str] = None, source: Optional[str] = None, _: None = Depends(get_current_client)
):
    full_url = f"{NEWSAPI_BASE}/top-headlines?apiKey={NEWS_API_KEY}"
    if country:
        full_url = f"{full_url}&country={country}"
    if source:
        full_url = f"{full_url}&sources={source}"

    logger.debug(f"Filtering headlines with URL: {full_url}")
    full_response = requests.get(full_url)

    try:
        response = full_response.json()
    except ValueError:
        logger.error("Invalid JSON response from News API")
        return response_data.error_response(
            status_code=status.HTTP_502_BAD_GATEWAY,
            message="News API did not return valid JSON",
            errors=[{"detail": full_response.text}]
        )

    if full_response.status_code == 200:
        logger.info("Filtered headlines fetched successfully")
        return response_data.success_response(
            status_code=200,
            data=response,
            message="News fetched successfully"
        )
    else:
        logger.debug(f"News API returned error: {full_response.status_code} - {full_response.text}")
        return response_data.error_response(
            status_code=full_response.status_code,
            message=str(full_response.json().get("message")),
            errors=[{"detail": full_response.text}]
        )
