# app/main.py
from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from api.news_v1.router import news_api_v1
from core.oauth2 import oauth2_router
from config.settings import get_settings

settings = get_settings()
WHITE_LIST =  settings.WHITE_LIST.split(",")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

app = FastAPI(title=settings.PROJECT_NAME, debug=settings.DEBUG)
app.add_middleware(
    CORSMiddleware,
    allow_origins=WHITE_LIST,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(oauth2_router, prefix="/api/auth")
app.include_router(news_api_v1, prefix="/api/v1/news")
