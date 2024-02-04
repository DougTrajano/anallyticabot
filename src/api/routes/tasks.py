"""Tasks endpoints."""
import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from worker.tasks.factory import TaskFactory
from api.backends.factory import BackendFactory
from api.utils.logger import logger
from api.utils.misc import is_valid_uuid, check_task_exists
from api.utils.settings import WorkerSettings
from api.database.base import get_async_session
from api.database.models.task import (
    Task,
    TaskCreate,
    TaskUpdate,
    TaskRead,
    TaskOutput,
    TaskInput
)


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}}
)

backend = BackendFactory.create_backend(WorkerSettings().WORKER_BACKEND)

@router.get("/", response_model=List[TaskRead])
async def read_tasks(
    session: AsyncSession = Depends(get_async_session)):
    """Get all tasks.
    
    Returns:
        List[TaskRead]: List of tasks.
    """
    logger.info("Getting all tasks.")
    async with session.begin():
        stmt = select(Task)
        results = await session.exec(stmt)
        results = results.all()
        logger.info("Found %s tasks.", len(results))
        logger.debug("Tasks found: %s", results)
        return results

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    session: AsyncSession = Depends(get_async_session)):
    """Create a new task.

    Args:
        task (TaskCreate): Task to create.

    Returns:
        dict: Response message.
    """
    logger.info("Starting create_task endpoint: %s", task)

    # Validations
    if not check_task_exists(task.name):
        logger.info("Task %s not exist.", task.name)
        raise HTTPException(status_code=400, detail=f"Task {task.name} not exist.")

    task: Task = Task(**task.model_dump())
    worker_task = TaskFactory.create_executor(task.id, task.name)

    # Create task in database
    async with session:
        task.version = worker_task.version
        task.start_time = datetime.datetime.now()

        logger.debug("Creating task: %s in database.", task.model_dump())
        session.add(task)
        await session.commit()
        await session.refresh(task)
        logger.debug("Task %s created in database.", task.id)

    # Send task to worker and update task status
    try:
        # Prepare task to be sent to worker
        if not isinstance(worker_task.environment, dict):
            worker_task.environment = {}
        worker_task.environment["WORKER_API_ENDPOINT"] = WorkerSettings().WORKER_API_ENDPOINT
        if WorkerSettings().WORKER_API_TOKEN:
            worker_task.environment["WORKER_API_TOKEN"] = WorkerSettings().WORKER_API_TOKEN

        logger.info("Sending task %s to worker.", task.id)
        response = backend.run(worker_task)
        logger.info("Task %s sent to worker. Response: %s", task.id, response)

        # Update task status
        task.status = "RUNNING"
        task.status_desc = "Task is running."
        task.start_time = datetime.datetime.now()
        async with session:
            session.add(task)
            await session.commit()
            await session.refresh(task)
            logger.info("Task updated: %s", task)
        return {"message": f"Task {task.id} created."}

    except Exception as e:
        logger.error("Error: %s", e)

        # Update task status
        task.status = "FAILED"
        task.status_desc = f"Error: {e}"
        task.end_time = datetime.datetime.now()
        async with session:
            session.add(task)
            await session.commit()
            await session.refresh(task)
            logger.info("Task updated: %s", task)
        raise HTTPException(status_code=500, detail="Task creation failed.") from e

@router.put("/", status_code=status.HTTP_200_OK)
async def update_task(
    task: TaskUpdate,
    session: AsyncSession = Depends(get_async_session)):
    """Create or update a task.

    Args:
        task (TaskUpdate): Task to update.

    Returns:
        dict: Response message.
    """
    logger.info("Updating task: %s", task)

    async with session.begin():
        stmt = select(Task).where(Task.id == task.id)
        result = await session.exec(stmt)
        if not result.first():
            logger.info("Task %s not found. Creating it.", task.id)
            session.add(task)
            await session.refresh(task)
            logger.info("Task created: %s", task)
            return {
                "message": "Task created.",
                "task_id": task.id
            }
        else:
            logger.info("Task %s found. Updating it.", task.id)
            session.add(task)
            await session.refresh(task)
            logger.info("Task updated: %s", task)
            return {"message": f"Task {task.id} updated."}

@router.get("/{task_id}", response_model=TaskRead)
async def read_task(
    task_id: str,
    session: AsyncSession = Depends(get_async_session)):
    """Get task by id.

    Args:
        task_id (str): Task id.

    Returns:
        TaskRead: Task.
    """
    if not is_valid_uuid(task_id):
        logger.info("task_id is not a valid uuid.")
        raise HTTPException(status_code=400, detail="task_id is not a valid uuid.")

    logger.info("Reading task with id: %s", task_id)
    async with session.begin():
        stmt = select(Task).where(Task.id == task_id)
        result = await session.exec(stmt)
        result = result.first()
        logger.debug("Task found: %s", result)

        # Raise 404 if task not found
        if not result:
            logger.info("Task not found.")
            raise HTTPException(status_code=404, detail="Task not found.")
        return result

@router.get("/{task_id}/input", response_model=TaskInput)
async def read_task_input(
    task_id: str,
    session: AsyncSession = Depends(get_async_session)):
    """Get task input by id.

    Args:
        task_id (str): Task id.

    Returns:
        TaskInput: Task input.
    """
    if not is_valid_uuid(task_id):
        logger.info("task_id is not a valid uuid.")
        raise HTTPException(status_code=400, detail="task_id is not a valid uuid.")
    
    logger.info("Reading task input with id: %s", task_id)
    async with session.begin():
        stmt = select(Task).where(Task.id == task_id)
        result = await session.exec(stmt)
        result: TaskInput = result.first()
        logger.debug("Task found: %s", result)

        # Raise 404 if task not found
        if not result:
            logger.info("Task not found.")
            raise HTTPException(status_code=404, detail="Task not found.")

        # Raise 404 if task has no input
        if not result.input:
            logger.info("Task has no input.")
            raise HTTPException(status_code=404, detail="Task has no input.")
        return result.input

@router.get("/{task_id}/output", response_model=TaskOutput)
async def read_task_output(
    task_id: str,
    session: AsyncSession = Depends(get_async_session)):
    """Get task output by id.

    Args:
        task_id (str): Task id.

    Returns:
        TaskOutput: Task output.
    """
    if not is_valid_uuid(task_id):
        logger.info("task_id is not a valid uuid.")
        raise HTTPException(status_code=400, detail="task_id is not a valid uuid.")

    logger.info("Reading task output with id: %s", task_id)
    async with session.begin():
        stmt = select(Task).where(Task.id == task_id)
        result = await session.exec(stmt)
        result: TaskOutput = result.first()
        logger.debug("Task found: %s", result)

        # Raise 404 if task not found
        if not result:
            logger.info("Task not found.")
            raise HTTPException(status_code=404, detail="Task not found.")

        # Raise 404 if task has no result
        if not result.output:
            logger.info("Task has no output.")
            raise HTTPException(status_code=404, detail="Task has no output.")
        return result.output

@router.post("/{task_id}/output", status_code=status.HTTP_200_OK)
async def create_task_output(
    task_id: str,
    task_output: TaskOutput,
    session: AsyncSession = Depends(get_async_session)):
    """Create task output.

    Args:
        task_id (str): Task id.
        task_output (TaskOutput): Task output.

    Returns:
        dict: Response message.
    """
    if not is_valid_uuid(task_id):
        logger.info("task_id is not a valid uuid.")
        raise HTTPException(status_code=400, detail="task_id is not a valid uuid.")

    logger.info("Creating task output with id: %s", task_id)
    async with session.begin():
        stmt = select(Task).where(Task.id == task_id)
        result = await session.exec(stmt)
        result: TaskOutput = result.first()
        logger.debug("Task found: %s", result)

        # Raise 404 if task not found
        if not result:
            logger.info("Task not found.")
            raise HTTPException(status_code=404, detail="Task not found.")

        # Raise 400 if task has already output
        if result.output:
            logger.info("Task already has output.")
            raise HTTPException(status_code=400, detail="Task already has output.")

        # Update task output
        result.output = task_output.output
        async with session:
            session.add(result)
            await session.commit()
            await session.refresh(result)
            logger.info("Task output updated: %s", result)
            return {"message": f"Task output {task_id} created."}

@router.put("/{task_id}/output", status_code=status.HTTP_200_OK)
async def update_task_output(
    task_id: str,
    task_output: TaskOutput,
    session: AsyncSession = Depends(get_async_session)):
    """Update task output.

    Args:
        task_id (str): Task id.
        task_output (TaskOutput): Task output.

    Returns:
        dict: Response message.
    """
    if not is_valid_uuid(task_id):
        logger.info("task_id is not a valid uuid.")
        raise HTTPException(status_code=400, detail="task_id is not a valid uuid.")

    logger.info("Updating task output with id: %s", task_id)
    async with session.begin():
        stmt = select(Task).where(Task.id == task_id)
        result = await session.exec(stmt)
        result: TaskOutput = result.first()
        logger.debug("Task found: %s", result)

        # Raise 404 if task not found
        if not result:
            logger.info("Task not found.")
            raise HTTPException(status_code=404, detail="Task not found.")

        # Update task output
        result.output = task_output.output
        async with session:
            session.add(result)
            await session.commit()
            await session.refresh(result)
            logger.info("Task output updated: %s", result)
            return {"message": f"Task output {task_id} updated."}
