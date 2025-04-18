import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.mysql_connection import Base, get_db
from main import app

# Mock the get_db dependency to avoid using the actual DB
@pytest.fixture
def override_get_db():
    # Create an in-memory SQLite engine for testing purposes
    engine = create_engine("sqlite:///:memory:")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Create all tables in the database
    Base.metadata.create_all(bind=engine)

    # Dependency override
    def get_db_override():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    return get_db_override


# Test client
@pytest.fixture
def client(override_get_db):
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)


# Test registration endpoint
def test_register_user(client):
    response = client.post("/api/auth/register", data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 201
    assert response.json()["message"] == "User registered successfully"
    assert "username" in response.json()["data"]
    assert response.json()["data"]["username"] == "testuser"


# Test login endpoint
def test_login(client):
    # Register user first
    client.post("/api/auth/register", data={"username": "testuser", "password": "testpass"})
    response = client.post("/api/auth/token", data={"username": "testuser", "password": "testpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]
    assert "refresh_token" in response.json()["data"]


# Test refresh token endpoint
def test_refresh_token(client):
    client.post("/api/auth/register", data={"username": "testuser", "password": "testpass"})
    login_response = client.post("/api/auth/token", data={"username": "testuser", "password": "testpass"})
    refresh_token = login_response.json()["data"]["refresh_token"]

    response = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]
    assert response.json()["message"] == "Refresh successful"


# Test fetching news
def test_get_news(client):
    response = client.get("/api/v1/news")
    assert response.status_code == 200
    assert "data" in response.json()
    assert isinstance(response.json()["data"], list)


# Test saving the latest news
def test_save_latest_news(client):
    response = client.post("/api/v1/news/save-latest")
    assert response.status_code == 200
    assert response.json()["message"] == "Latest news saved successfully"
    assert "saved" in response.json()["data"]


# Test fetching headlines by country
def test_headlines_by_country(client):
    response = client.get("/api/v1/news/headlines/country/us")
    assert response.status_code == 200
    assert "data" in response.json()


# Test fetching headlines by source
def test_headlines_by_source(client):
    response = client.get("/api/v1/news/headlines/source/abc-news")
    assert response.status_code == 200
    assert "data" in response.json()


# Test filtering headlines by country and source
def test_filter_headlines(client):
    response = client.get("/api/v1/news/headlines/filter?country=us&source=bbc-news")
    assert response.status_code == 200
    assert "data" in response.json()
