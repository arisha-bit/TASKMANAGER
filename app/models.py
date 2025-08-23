from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId

class Task(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    title: str
    date: str
    original_text: Optional[str] = None
    extracted_at: Optional[str] = None
    completed: bool = False
    priority: str = "medium"  # low, medium, high
    status: str = "pending"   # pending, in_progress, completed, cancelled
    description: Optional[str] = None
    tags: List[str] = []
    google_calendar_id: Optional[str] = None
    google_task_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "title": "Submit Project Report",
                "date": "2024-01-15",
                "priority": "high",
                "status": "pending",
                "description": "Final project report submission",
                "tags": ["work", "project", "deadline"]
            }
        }

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    date: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class TaskResponse(BaseModel):
    id: str
    title: str
    date: str
    completed: bool
    priority: str
    status: str
    description: Optional[str] = None
    tags: List[str] = []
    created_at: str
    updated_at: str
