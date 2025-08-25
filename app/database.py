from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection string
MONGO_URI = "YOUR URL"

try:
    client = MongoClient(MONGO_URI)
    # Test connection
    client.admin.command('ping')
    logger.info("Successfully connected to MongoDB")
except ConnectionFailure as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    client = None

if client:
    db = client["task_manager"]
    tasks_collection = db["tasks"]
    
    # Create indexes for better performance
    try:
        tasks_collection.create_index([("date", ASCENDING)])
        tasks_collection.create_index([("completed", ASCENDING)])
        tasks_collection.create_index([("priority", ASCENDING)])
        tasks_collection.create_index([("status", ASCENDING)])
        tasks_collection.create_index([("created_at", DESCENDING)])
        logger.info("Database indexes created successfully")
    except OperationFailure as e:
        logger.warning(f"Failed to create indexes: {e}")

def get_tasks(filters: Optional[Dict[str, Any]] = None, sort_by: str = "date", sort_order: int = ASCENDING) -> List[Dict[str, Any]]:
    """Get tasks with optional filtering and sorting"""
    try:
        if not filters:
            filters = {}
        
        cursor = tasks_collection.find(filters).sort(sort_by, sort_order)
        tasks = list(cursor)
        
        # Convert ObjectId to string for JSON serialization
        for task in tasks:
            task['_id'] = str(task['_id'])
        
        return tasks
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        return []

def get_task_by_id(task_id: str) -> Optional[Dict[str, Any]]:
    """Get a single task by ID"""
    try:
        from bson.objectid import ObjectId
        task = tasks_collection.find_one({"_id": ObjectId(task_id)})
        if task:
            task['_id'] = str(task['_id'])
        return task
    except Exception as e:
        logger.error(f"Error fetching task {task_id}: {e}")
        return None

def create_task(task_data: Dict[str, Any]) -> Optional[str]:
    """Create a new task"""
    try:
        # Add timestamps
        task_data['created_at'] = datetime.now().isoformat()
        task_data['updated_at'] = datetime.now().isoformat()
        
        result = tasks_collection.insert_one(task_data)
        logger.info(f"Task created with ID: {result.inserted_id}")
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return None

def update_task(task_id: str, update_data: Dict[str, Any]) -> bool:
    """Update an existing task"""
    try:
        from bson.objectid import ObjectId
        
        # Add update timestamp
        update_data['updated_at'] = datetime.now().isoformat()
        
        result = tasks_collection.update_one(
            {"_id": ObjectId(task_id)},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            logger.info(f"Task {task_id} updated successfully")
            return True
        else:
            logger.warning(f"No changes made to task {task_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        return False

def delete_task(task_id: str) -> bool:
    """Delete a task"""
    try:
        from bson.objectid import ObjectId
        
        result = tasks_collection.delete_one({"_id": ObjectId(task_id)})
        
        if result.deleted_count > 0:
            logger.info(f"Task {task_id} deleted successfully")
            return True
        else:
            logger.warning(f"Task {task_id} not found for deletion")
            return False
            
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        return False

def get_task_statistics() -> Dict[str, Any]:
    """Get task statistics for dashboard"""
    try:
        total_tasks = tasks_collection.count_documents({})
        completed_tasks = tasks_collection.count_documents({"completed": True})
        pending_tasks = tasks_collection.count_documents({"completed": False})
        
        # Priority distribution
        high_priority = tasks_collection.count_documents({"priority": "high", "completed": False})
        medium_priority = tasks_collection.count_documents({"priority": "medium", "completed": False})
        low_priority = tasks_collection.count_documents({"priority": "low", "completed": False})
        
        return {
            "total": total_tasks,
            "completed": completed_tasks,
            "pending": pending_tasks,
            "high_priority": high_priority,
            "medium_priority": medium_priority,
            "low_priority": low_priority,
            "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        }
    except Exception as e:
        logger.error(f"Error getting task statistics: {e}")
        return {}

def search_tasks(query: str) -> List[Dict[str, Any]]:
    """Search tasks by title or description"""
    try:
        from bson.regex import Regex
        
        # Create case-insensitive regex pattern
        regex_pattern = Regex(query, "i")
        
        cursor = tasks_collection.find({
            "$or": [
                {"title": regex_pattern},
                {"description": regex_pattern},
                {"tags": regex_pattern}
            ]
        }).sort("created_at", DESCENDING)
        
        tasks = list(cursor)
        
        # Convert ObjectId to string
        for task in tasks:
            task['_id'] = str(task['_id'])
        
        return tasks
    except Exception as e:
        logger.error(f"Error searching tasks: {e}")
        return []
