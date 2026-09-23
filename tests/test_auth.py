import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db
from app.models import User, Task  
from app.main import app

# Test database setup using StaticPool
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()



@pytest.fixture(scope="function")
def client():
    """Create clean test client for each test"""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

class TestAuth:
    def test_register_user(self, client):
        user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "securepassword123"
        }
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_duplicate_username(self, client):
        user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "securepassword123"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        user_data2 = {
            "username": "testuser",
            "email": "another@example.com",
            "password": "password456"
        }
        response = client.post("/api/v1/auth/register", json=user_data2)
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]

    def test_login_success(self, client):
        user_data = {
            "username": "loginuser",
            "email": "login@example.com",
            "password": "mypassword123"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "username": "loginuser",
            "password": "mypassword123"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 200
        token_data = response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"

    def test_login_invalid_password(self, client):
        user_data = {
            "username": "loginuser2",
            "email": "login2@example.com",
            "password": "mypassword123"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_data = {
            "username": "loginuser2",
            "password": "wrongpassword"
        }
        response = client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == 401

    def test_get_current_user_profile(self, client):
        user_data = {
            "username": "profileuser",
            "email": "profile@example.com",
            "password": "mypassword123"
        }
        client.post("/api/v1/auth/register", json=user_data)
        
        login_response = client.post("/api/v1/auth/login", data={"username": "profileuser", "password": "mypassword123"})
        token = login_response.json()["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = client.get("/api/v1/auth/me", headers=headers)
        assert profile_response.status_code == 200
        data = profile_response.json()
        assert data["username"] == "profileuser"

    def test_get_current_user_unauthorized(self, client):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

