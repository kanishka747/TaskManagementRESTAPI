from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db import get_db
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskListResponse, Message
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new task.
    
    **Example Request Body:**
    ```json
    {
        "title": "Fix login bug",
        "description": "Users cannot login with special characters",
        "status": "pending",
        "priority": "high",
        "due_date": "2024-01-15T10:00:00"
    }
    ```
    
    **Returns:** Created task with ID and timestamps.
    """
    task = TaskService.create_task(db, task)
    return task

@router.get("/", response_model=TaskListResponse)
def get_tasks(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max items to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db)
):
    """
    Get all tasks with pagination and filtering.
    
    **Query Parameters:**
    - `skip`: Number of items to skip (default: 0)
    - `limit`: Maximum items to return (default: 10)
    - `status_filter`: Filter by task status
    - `priority`: Filter by priority
    
    **Returns:** Paginated list of tasks with metadata.
    """
    tasks, total = TaskService.get_tasks(db, skip, limit, status_filter, priority)
    total_pages = (total + limit - 1) // limit
    
    return {
        "total": total,
        "page": (skip // limit) + 1,
        "page_size": limit,
        "total_pages": total_pages,
        "items": tasks
    }

@router.get("/stats", response_model=dict)
def get_statistics(db: Session = Depends(get_db)):
    """
    Get task statistics and analytics.
    
    **Returns:** Dictionary with total tasks, counts by status and priority.
    """
    return TaskService.get_task_statistics(db)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """
    Get a specific task by ID.
    
    **Returns:** Task details if found.
    
    **Raises:** 404 if task not found.
    """
    task = TaskService.get_task(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing task.
    
    **Example Request Body:**
    ```json
    {
        "title": "Updated title",
        "status": "in_progress"
    }
    ```
    
    **Returns:** Updated task.
    
    **Raises:** 404 if task not found.
    """
    task = TaskService.update_task(db, task_id, task_update)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.delete("/{task_id}", response_model=Message)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Delete a task (soft delete).
    
    **Returns:** Confirmation message.
    
    **Raises:** 404 if task not found.
    """
    if not TaskService.delete_task(db, task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return Message(message=f"Task {task_id} deleted successfully")

