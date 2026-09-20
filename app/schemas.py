from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List
from app.models import TaskStatus

class TaskBase(BaseModel):
    """Base schema for task creation/update"""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    status: str = Field("pending", description="Task status: pending, in_progress, completed, cancelled")
    priority: str = Field("medium", description="Priority: low, medium, high")
    due_date: Optional[datetime] = Field(None, description="Task due date")

class TaskCreate(TaskBase):
    """Schema for creating a new task"""
    pass

class TaskUpdate(TaskBase):
    """Schema for updating a task"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[str] = Field(None)
    priority: Optional[str] = Field(None)
    due_date: Optional[datetime] = Field(None)

class TaskResponse(TaskBase):
    """Schema for task response"""
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    """Schema for paginated task list response"""
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[TaskResponse]

class Message(BaseModel):
    """Generic message response"""
    message: str
