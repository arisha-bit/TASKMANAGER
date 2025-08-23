from fastapi import FastAPI, Request, UploadFile, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import logging
from typing import List, Optional
import json

from app.ocr import extract_tasks_from_image
from app.database import (
    get_tasks, get_task_by_id, create_task, update_task, 
    delete_task, get_task_statistics, search_tasks
)
from app.google_auth import get_credentials
from app.google_calendar import add_event_to_calendar
from app.google_tasks import add_task_to_google_tasks
from app.models import Task, TaskUpdate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Enhanced Task Manager", version="2.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Main page with upload functionality"""
    try:
        stats = get_task_statistics()
        return templates.TemplateResponse("index.html", {"request": request, "stats": stats})
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return templates.TemplateResponse("index.html", {"request": request, "stats": {}})

@app.post("/upload", response_class=HTMLResponse)
async def upload(request: Request, file: UploadFile):
    """Upload and process image to extract tasks"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Extract tasks from image
        tasks = extract_tasks_from_image(file.file)
        
        if not tasks:
            return templates.TemplateResponse("upload.html", {
                "request": request, 
                "tasks": [], 
                "message": "No tasks found in the image. Please try with a clearer image."
            })
        
        # Get Google credentials
        creds = get_credentials()
        
        # Save tasks in MongoDB and Google Calendar/Tasks
        saved_tasks = []
        for task_data in tasks:
            try:
                # Create task in MongoDB
                task_id = create_task(task_data)
                if task_id:
                    task_data['_id'] = task_id
                    saved_tasks.append(task_data)
                    
                    # Add to Google Calendar and Tasks
                    if creds:
                        try:
                            add_event_to_calendar(task_data['title'], task_data['date'], creds)
                            add_task_to_google_tasks(task_data['title'], task_data['date'], creds)
                        except Exception as e:
                            logger.warning(f"Failed to add to Google services: {e}")
                            
            except Exception as e:
                logger.error(f"Error saving task: {e}")
                continue
        
        return templates.TemplateResponse("upload.html", {
            "request": request, 
            "tasks": saved_tasks,
            "message": f"Successfully extracted {len(saved_tasks)} tasks from the image!"
        })
        
    except Exception as e:
        logger.error(f"Error in upload route: {e}")
        return templates.TemplateResponse("upload.html", {
            "request": request, 
            "tasks": [], 
            "error": f"Error processing image: {str(e)}"
        })

@app.get("/tasks", response_class=HTMLResponse)
async def tasks_page(request: Request, 
                    status: Optional[str] = None,
                    priority: Optional[str] = None,
                    search: Optional[str] = None):
    """Tasks page with filtering and search"""
    try:
        filters = {}
        if status:
            filters["status"] = status
        if priority:
            filters["priority"] = priority
            
        if search:
            tasks = search_tasks(search)
        else:
            tasks = get_tasks(filters=filters, sort_by="date", sort_order=1)
            
        stats = get_task_statistics()
        
        return templates.TemplateResponse("tasks.html", {
            "request": request, 
            "tasks": tasks, 
            "stats": stats,
            "current_filters": {"status": status, "priority": priority, "search": search}
        })
    except Exception as e:
        logger.error(f"Error in tasks route: {e}")
        return templates.TemplateResponse("tasks.html", {
            "request": request, 
            "tasks": [], 
            "stats": {},
            "error": f"Error loading tasks: {str(e)}"
        })

@app.post("/tasks/complete")
async def mark_complete(task_id: str = Form(...)):
    """Mark a task as complete"""
    try:
        success = update_task(task_id, {"completed": True, "status": "completed"})
        if success:
            return RedirectResponse("/tasks", status_code=303)
        else:
            raise HTTPException(status_code=400, detail="Failed to update task")
    except Exception as e:
        logger.error(f"Error marking task complete: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/tasks/delete")
async def delete_task_endpoint(task_id: str = Form(...)):
    """Delete a task"""
    try:
        success = delete_task(task_id)
        if success:
            return RedirectResponse("/tasks", status_code=303)
        else:
            raise HTTPException(status_code=400, detail="Failed to delete task")
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/tasks/update")
async def update_task_endpoint(task_id: str = Form(...), 
                              title: str = Form(...),
                              date: str = Form(...),
                              priority: str = Form(...),
                              status: str = Form(...),
                              description: str = Form(None)):
    """Update task details"""
    try:
        update_data = {
            "title": title,
            "date": date,
            "priority": priority,
            "status": status
        }
        if description:
            update_data["description"] = description
            
        success = update_task(task_id, update_data)
        if success:
            return RedirectResponse("/tasks", status_code=303)
        else:
            raise HTTPException(status_code=400, detail="Failed to update task")
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/tasks")
async def api_get_tasks(status: Optional[str] = None, 
                        priority: Optional[str] = None,
                        limit: int = 100):
    """API endpoint to get tasks"""
    try:
        filters = {}
        if status:
            filters["status"] = status
        if priority:
            filters["priority"] = priority
            
        tasks = get_tasks(filters=filters, sort_by="date", sort_order=1)
        return {"tasks": tasks[:limit], "total": len(tasks)}
    except Exception as e:
        logger.error(f"Error in API get tasks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/tasks/{task_id}")
async def api_get_task(task_id: str):
    """API endpoint to get a specific task"""
    try:
        task = get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except Exception as e:
        logger.error(f"Error in API get task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/stats")
async def api_get_stats():
    """API endpoint to get task statistics"""
    try:
        stats = get_task_statistics()
        return stats
    except Exception as e:
        logger.error(f"Error in API get stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard with statistics and overview"""
    try:
        stats = get_task_statistics()
        recent_tasks = get_tasks(sort_by="created_at", sort_order=-1)[:5]
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request, 
            "stats": stats,
            "recent_tasks": recent_tasks
        })
    except Exception as e:
        logger.error(f"Error in dashboard route: {e}")
        return templates.TemplateResponse("dashboard.html", {
            "request": request, 
            "stats": {},
            "recent_tasks": [],
            "error": f"Error loading dashboard: {str(e)}"
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
