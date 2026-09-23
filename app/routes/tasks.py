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
    """Create a new task."""
    return TaskService.create_task(db, task)

@router.get("/", response_model=TaskListResponse)
def get_tasks(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max items to return"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db)
):
    """Fetch paginated tasks with optional status and priority filters."""
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
    """Get overall task statistics grouped by status and priority."""
    return TaskService.get_task_statistics(db)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """Fetch single task details by ID."""
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
    """Update task attributes."""
    task = TaskService.update_task(db, task_id, task_update)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return task

@router.delete("/{task_id}", response_model=Message)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """Soft delete a task by marking it inactive."""
    if not TaskService.delete_task(db, task_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return Message(message=f"Task {task_id} deleted successfully")

