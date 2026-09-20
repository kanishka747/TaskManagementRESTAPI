from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate
from typing import List, Optional
from datetime import datetime

class TaskService:
    """Task business logic service layer"""
    
    @staticmethod
    def create_task(db: Session, task: TaskCreate) -> Task:
        """Create a new task"""
        db_task = Task(
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def get_task(db: Session, task_id: int) -> Optional[Task]:
        """Get a task by ID"""
        return db.query(Task).filter(Task.id == task_id, Task.is_active == True).first()
    
    @staticmethod
    def get_tasks(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> tuple[List[Task], int]:
        """Get paginated tasks with optional filters"""
        query = db.query(Task).filter(Task.is_active == True)
        
        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        
        total = query.count()
        tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
        
        return tasks, total
    
    @staticmethod
    def update_task(
        db: Session,
        task_id: int,
        task_update: TaskUpdate
    ) -> Optional[Task]:
        """Update an existing task"""
        db_task = TaskService.get_task(db, task_id)
        if not db_task:
            return None
        
        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if value is not None:
                setattr(db_task, field, value)
        
        db.commit()
        db.refresh(db_task)
        return db_task
    
    @staticmethod
    def delete_task(db: Session, task_id: int) -> bool:
        """Soft delete a task"""
        db_task = TaskService.get_task(db, task_id)
        if not db_task:
            return False
        
        db_task.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def get_task_statistics(db: Session) -> dict:
        """Get task statistics"""
        total = db.query(func.count(Task.id)).filter(Task.is_active == True).scalar()
        by_status = db.query(Task.status, func.count(Task.id)) \
            .filter(Task.is_active == True) \
            .group_by(Task.status).all()
        by_priority = db.query(Task.priority, func.count(Task.id)) \
            .filter(Task.is_active == True) \
            .group_by(Task.priority).all()
        
        return {
            "total": total,
            "by_status": dict(by_status),
            "by_priority": dict(by_priority)
        }
