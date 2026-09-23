import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from app.db import Base, get_db
from app.models import Task
from app.main import app

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},
    poolclass=StaticPool)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override database for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client():
    """Create test client"""
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_task():
    """Create sample task data"""
    return {
        "title": "Test Task",
        "description": "This is a test task",
        "status": "pending",
        "priority": "medium"
    }

class TestTaskCRUD:
    def test_create_task(self, client, sample_task):
        response = client.post("/api/v1/tasks/", json=sample_task)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_task["title"]
        assert data["status"] == sample_task["status"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_task_validation(self, client):
        invalid_task = {
            "title": "", 
            "status": "invalid_status"
        }
        response = client.post("/api/v1/tasks/", json=invalid_task)
        assert response.status_code == 422  
    
    def test_get_all_tasks(self, client, sample_task):
        client.post("/api/v1/tasks/", json=sample_task)
        response = client.get("/api/v1/tasks/")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert len(data["items"]) == 1
    
    def test_get_task_by_id(self, client, sample_task):
        create_response = client.post("/api/v1/tasks/", json=sample_task)
        task_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
    
    def test_get_task_not_found(self, client):
        response = client.get("/api/v1/tasks/999")
        assert response.status_code == 404
    
    def test_update_task(self, client, sample_task):
        create_response = client.post("/api/v1/tasks/", json=sample_task)
        task_id = create_response.json()["id"]
        
        update_data = {
            "title": "Updated Title",
            "status": "in_progress"
        }
        response = client.put(f"/api/v1/tasks/{task_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "in_progress"
    
    def test_delete_task(self, client, sample_task):
        create_response = client.post("/api/v1/tasks/", json=sample_task)
        task_id = create_response.json()["id"]
        
        response = client.delete(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 200
        
        get_response = client.get(f"/api/v1/tasks/{task_id}")
        assert get_response.status_code == 404
    
    def test_task_statistics(self, client, sample_task):
        for i in range(5):
            task_data = sample_task.copy()
            task_data["title"] = f"Task {i}"
            task_data["status"] = "pending" if i % 2 == 0 else "in_progress"
            task_data["priority"] = "high" if i % 2 == 0 else "low"
            client.post("/api/v1/tasks/", json=task_data)
        
        response = client.get("/api/v1/tasks/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert "by_status" in data
        assert "by_priority" in data

class TestPagination:
    def test_pagination_skip_limit(self, client, sample_task):
        for i in range(15):
            task_data = sample_task.copy()
            task_data["title"] = f"Task {i}"
            client.post("/api/v1/tasks/", json=task_data)
        
        response = client.get("/api/v1/tasks/?skip=0&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["page"] == 1
        assert data["total_pages"] == 3

class TestFiltering:
    def test_filter_by_status(self, client, sample_task):
        client.post("/api/v1/tasks/", json=sample_task.copy())
        task2 = sample_task.copy()
        task2["status"] = "in_progress"
        client.post("/api/v1/tasks/", json=task2)
        
        response = client.get("/api/v1/tasks/?status_filter=in_progress")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["status"] == "in_progress"

