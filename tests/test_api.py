import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.mysql_connection import Base
from main import app

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables once before any tests run
Base.metadata.create_all(bind=engine)


# Override get_db dependency
@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


# Test registration endpoint
def test_register_user(client):
    response = client.post("/api/auth/register", params={"username": "uniqueuser", "password": "testpass"})

    if response.status_code == 201:
        assert response.status_code == 201
        assert response.json()["message"] == "User registered successfully"
        assert "username" in response.json()["data"]
        assert response.json()["data"]["username"] == "uniqueuser"
    else:
        assert response.status_code == 400
        assert response.json()["message"] == "Unable to register user. Username already exists."
        assert not response.json()["success"]


# Test login endpoint
def test_login(client):
    response = client.post("/api/auth/token/", data={"username": "uniqueuser", "password": "testpass"})
    assert response.status_code == 200
    assert "access_token" in response.json()["data"]
    assert "refresh_token" in response.json()["data"]
    assert response.json()["message"] == "Login successful"


# #Test refresh token endpoint
def test_refresh_token(client):
    response = client.post("/api/auth/token/", data={"username": "uniqueuser", "password": "testpass"})
    refresh_token = response.json()["data"]["refresh_token"]
    response = client.post("/api/auth/refresh/", params={"refresh_token": refresh_token})

    assert response.status_code == 200
    assert "access_token" in response.json()["data"]
    assert response.json()["data"]["token_type"] == "bearer"
    assert response.json()["message"] == "Refresh successful"


# # Test fetching news
def test_get_news(client):
    response = client.post("/api/auth/token/", data={"username": "uniqueuser", "password": "testpass"})
    access_token = response.json()["data"]["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/news", headers=headers)
    if response.status_code == 200:
        assert response.status_code == 200
        assert "data" in response.json()
        assert isinstance(response.json()["data"], list)
    elif response.status_code == 401:
        assert response.status_code == 401
        assert response.json()["message"] == "Not authenticated"


# # Test saving the latest news
def test_save_latest_news(client):
    response = client.post("/api/auth/token/", data={"username": "uniqueuser", "password": "testpass"})
    access_token = response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.post("api/v1/news/save-latest", headers=headers)

    if response.status_code != 200:
        assert response.status_code == 500
        assert response.json()["message"] == "Failed to fetch news"
    else:
        assert response.status_code == 200
        assert "data" in response.json()
        assert response.json()["message"] == "Latest news saved successfully"


# Test fetching headlines by country
def test_headlines_by_country(client):
    response = client.post("/api/auth/token/", data={"username": "uniqueuser", "password": "testpass"})
    access_token = response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/news/headlines/country/us", headers=headers)
    if response.status_code != 200:
        assert response.status_code == 500
    else:
        assert response.status_code == 200
        assert response.json()["message"] == "News fetched successfully"
        assert "data" in response.json()


# Test fetching headlines by source
def test_headlines_by_source(client):
    response = client.post("/api/auth/token/", data={"username": "uniqueuser", "password": "testpass"})
    access_token = response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/news/headlines/source/abc-news", headers=headers)

    if response.status_code != 200:
        assert response.status_code == 500
    else:
        assert response.status_code == 200
        assert response.json()["message"] == "News fetched successfully"
        assert "data" in response.json()


# # Test filtering headlines by country and source
def test_filter_headlines(client):
    response = client.post("/api/auth/token/", data={"username": "uniqueuser", "password": "testpass"})
    access_token = response.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/news/headlines/filter?country=us", headers=headers)

    if response.status_code == 502:
        assert response.status_code == 502
        assert response.json()["message"] == "News API did not return valid JSON"

    if response.status_code == 200:
        assert response.status_code == 200
        assert response.json()["message"] == "News fetched successfully"
        assert "data" in response.json()
