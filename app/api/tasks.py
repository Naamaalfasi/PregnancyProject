from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel
from app.agent.user_profile import user_profile_manager
from app.agent.action_planner import action_planner
from app.agent.memory_manager import memory_manager
from app.utils.ai_model import ai_model

logger = logging.getLogger(__name__)

router = APIRouter()

class Task(BaseModel):
    task_id: str
    user_id: str
    title: str
    description: str
    task_type: str
    due_date: Optional[datetime]
    completed: bool = False
    priority: int = 1
    metadata: Dict[str, Any] = {}

class TaskCreate(BaseModel):
    user_id: str
    title: str
    description: str
    task_type: str
    due_date: Optional[datetime] = None
    priority: int = 1
    metadata: Dict[str, Any] = {}

class TaskUpdate(BaseModel):
    completed: Optional[bool] = None
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[int] = None

@router.get("/tasks/{user_id}", response_model=List[Task])
async def get_user_tasks(user_id: str, completed: Optional[bool] = None):
    """Get tasks for a user"""
    try:
        # Get user profile to check pregnancy week
        user_profile = await user_profile_manager.get_user_profile(user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get tasks from database (simplified - in real app would use database)
        tasks = await _get_tasks_from_database(user_id, completed)
        
        # Generate AI-recommended tasks based on pregnancy week
        if user_profile.pregnancy_week:
            ai_tasks = await _generate_ai_tasks(user_id, user_profile.pregnancy_week)
            tasks.extend(ai_tasks)
        
        return tasks
        
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/tasks", response_model=Task)
async def create_task(task: TaskCreate):
    """Create a new task"""
    try:
        # Validate user exists
        user_profile = await user_profile_manager.get_user_profile(task.user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create task
        new_task = Task(
            task_id=f"task_{datetime.utcnow().timestamp()}",
            user_id=task.user_id,
            title=task.title,
            description=task.description,
            task_type=task.task_type,
            due_date=task.due_date,
            priority=task.priority,
            metadata=task.metadata
        )
        
        # Store task (simplified - in real app would use database)
        await _store_task(new_task)
        
        # Generate AI insights for the task
        ai_insights = await ai_model.generate_task_insights(
            user_id=task.user_id,
            task=new_task.dict(),
            context={"action": "task_created"}
        )
        
        # Store memory about task creation
        await memory_manager.store_memory(
            user_id=task.user_id,
            memory_type="task",
            content=f"Created task: {task.title}",
            importance=0.6,
            metadata={"task_type": task.task_type, "ai_insights": ai_insights}
        )
        
        return new_task
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.patch("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate):
    """Update a task"""
    try:
        # Get existing task
        task = await _get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Update task fields
        if task_update.completed is not None:
            task.completed = task_update.completed
        if task_update.title is not None:
            task.title = task_update.title
        if task_update.description is not None:
            task.description = task_update.description
        if task_update.due_date is not None:
            task.due_date = task_update.due_date
        if task_update.priority is not None:
            task.priority = task_update.priority
        
        # Store updated task
        await _store_task(task)
        
        # Generate AI insights for task update
        ai_insights = await ai_model.generate_task_insights(
            user_id=task.user_id,
            task=task.dict(),
            context={"action": "task_updated"}
        )
        
        # Store memory about task update
        await memory_manager.store_memory(
            user_id=task.user_id,
            memory_type="task",
            content=f"Updated task: {task.title}",
            importance=0.5,
            metadata={"task_type": task.task_type, "ai_insights": ai_insights}
        )
        
        return task
        
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task"""
    try:
        task = await _get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Delete task (simplified - in real app would use database)
        await _delete_task(task_id)
        
        # Store memory about task deletion
        await memory_manager.store_memory(
            user_id=task.user_id,
            memory_type="task",
            content=f"Deleted task: {task.title}",
            importance=0.4
        )
        
        return {"message": "Task deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/tasks/{task_id}/complete")
async def complete_task(task_id: str):
    """Mark a task as completed"""
    try:
        task = await _get_task_by_id(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        task.completed = True
        await _store_task(task)
        
        # Generate AI insights for task completion
        ai_insights = await ai_model.generate_task_insights(
            user_id=task.user_id,
            task=task.dict(),
            context={"action": "task_completed"}
        )
        
        # Store memory about task completion
        await memory_manager.store_memory(
            user_id=task.user_id,
            memory_type="task",
            content=f"Completed task: {task.title}",
            importance=0.7,
            metadata={"task_type": task.task_type, "ai_insights": ai_insights}
        )
        
        return {"message": "Task completed successfully", "ai_insights": ai_insights}
        
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/tasks/{user_id}/recommendations")
async def get_task_recommendations(user_id: str):
    """Get AI-generated task recommendations for user"""
    try:
        user_profile = await user_profile_manager.get_user_profile(user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Generate AI recommendations based on pregnancy week
        recommendations = await _generate_task_recommendations(user_id, user_profile.pregnancy_week)
        
        return {
            "user_id": user_id,
            "pregnancy_week": user_profile.pregnancy_week,
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting task recommendations: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/tasks/{user_id}/overdue")
async def get_overdue_tasks(user_id: str):
    """Get overdue tasks for user"""
    try:
        tasks = await _get_tasks_from_database(user_id, completed=False)
        overdue_tasks = [task for task in tasks if task.due_date and task.due_date < datetime.utcnow()]
        
        return {
            "user_id": user_id,
            "overdue_tasks": overdue_tasks,
            "count": len(overdue_tasks)
        }
        
    except Exception as e:
        logger.error(f"Error getting overdue tasks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Helper functions (simplified - in real app would use database)
async def _get_tasks_from_database(user_id: str, completed: Optional[bool] = None) -> List[Task]:
    """Get tasks from database (simplified implementation)"""
    # This is a simplified implementation
    # In a real app, this would query the database
    return []

async def _store_task(task: Task):
    """Store task in database (simplified implementation)"""
    # This is a simplified implementation
    # In a real app, this would store in database
    pass

async def _get_task_by_id(task_id: str) -> Optional[Task]:
    """Get task by ID (simplified implementation)"""
    # This is a simplified implementation
    # In a real app, this would query the database
    return None

async def _delete_task(task_id: str):
    """Delete task (simplified implementation)"""
    # This is a simplified implementation
    # In a real app, this would delete from database
    pass

async def _generate_ai_tasks(user_id: str, pregnancy_week: int) -> List[Task]:
    """Generate AI-recommended tasks based on pregnancy week"""
    try:
        # Get AI recommendations for the pregnancy week
        week_recommendations = await ai_model.generate_pregnancy_week_insights(
            user_id=user_id,
            week=pregnancy_week,
            context={"task_generation": True}
        )
        
        # Create tasks based on AI recommendations
        tasks = []
        if week_recommendations.get("tests"):
            tasks.append(Task(
                task_id=f"ai_task_{pregnancy_week}_tests",
                user_id=user_id,
                title=f"בדיקות שבוע {pregnancy_week}",
                description=week_recommendations.get("tests", "בדיקות שגרתיות"),
                task_type="medical_test",
                due_date=datetime.utcnow() + timedelta(days=7),
                priority=2,
                metadata={"ai_generated": True, "pregnancy_week": pregnancy_week}
            ))
        
        if week_recommendations.get("recommendations"):
            tasks.append(Task(
                task_id=f"ai_task_{pregnancy_week}_recommendations",
                user_id=user_id,
                title=f"המלצות שבוע {pregnancy_week}",
                description=week_recommendations.get("recommendations", "המלצות בריאות"),
                task_type="health_recommendation",
                due_date=datetime.utcnow() + timedelta(days=3),
                priority=1,
                metadata={"ai_generated": True, "pregnancy_week": pregnancy_week}
            ))
        
        return tasks
        
    except Exception as e:
        logger.error(f"Error generating AI tasks: {e}")
        return []

async def _generate_task_recommendations(user_id: str, pregnancy_week: int) -> List[Dict[str, Any]]:
    """Generate task recommendations using AI"""
    try:
        # Get AI recommendations
        week_insights = await ai_model.generate_pregnancy_week_insights(
            user_id=user_id,
            week=pregnancy_week,
            context={"task_recommendations": True}
        )
        
        recommendations = []
        
        # Medical tests recommendations
        if week_insights.get("tests"):
            recommendations.append({
                "type": "medical_test",
                "title": f"בדיקות שבוע {pregnancy_week}",
                "description": week_insights.get("tests"),
                "priority": "high",
                "due_in_days": 7
            })
        
        # Health recommendations
        if week_insights.get("recommendations"):
            recommendations.append({
                "type": "health_recommendation",
                "title": f"המלצות בריאות שבוע {pregnancy_week}",
                "description": week_insights.get("recommendations"),
                "priority": "medium",
                "due_in_days": 3
            })
        
        # Tips recommendations
        if week_insights.get("tips"):
            recommendations.append({
                "type": "tip",
                "title": f"טיפים שבוע {pregnancy_week}",
                "description": week_insights.get("tips"),
                "priority": "low",
                "due_in_days": 1
            })
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating task recommendations: {e}")
        return []
