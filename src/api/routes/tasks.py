"""Tasks endpoints."""
import json
import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import Response
from sqlmodel import select, col
from sqlmodel.ext.asyncio.session import AsyncSession
from worker.tasks.factory import TaskFactory
from api.backends.factory import BackendFactory
from common.logger import logger
from api.utils.misc import is_valid_uuid, check_task_exists
from api.utils.settings import WorkerSettings
from api.database.base import get_async_session
from api.database.models.task import (
    Task,
    TaskCreate,
    TaskInputs,
    TaskOutputs,
    TaskRead,
    TaskUpdate
)


router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}}
)

backend = BackendFactory.create_backend(WorkerSettings().WORKER_BACKEND)

worker_args = WorkerSettings()

@router.get("/", response_model=List[TaskRead])
async def read_tasks(
    page_limit: int = 10,
    offset: int = 0,    
    session: AsyncSession = Depends(get_async_session)):
    """Get all tasks ordered by start_time desc.

    Args:
    - page_limit (int, optional): Number of tasks to return. Defaults to 10.
    - offset (int, optional): Offset. Defaults to 0.
    
    Returns:
        List[TaskRead]: List of tasks.
    """
    logger.info("Getting all tasks.")
    async with session.begin():
        stmt = select(Task).order_by(col(Task.start_time).desc()).limit(page_limit).offset(offset)
        result = await session.exec(stmt)
        result = result.all()
        logger.debug("Tasks found: %s", result)
        return result

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
    logger.info("Creating task %s", task.name)

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

        logger.debug("Creating task %s in database.", task.id)
        session.add(task)
        await session.commit()
        await session.refresh(task)
        logger.debug("Task %s created in database.", task.id)

    # Send task to worker and update task status
    try:
        # Prepare task to be sent to worker
        if not isinstance(worker_task.environment, dict):
            worker_task.environment = {}
        worker_task.environment["API_BASE_ENDPOINT"] = worker_args.WORKER_API_ENDPOINT
        worker_task.environment["API_TOKEN"] = worker_args.WORKER_API_TOKEN
        worker_task.environment["LOG_LEVEL"] = worker_args.WORKER_LOG_LEVEL

        logger.debug("Environment: %s", worker_task.environment)
        logger.info("Sending task %s to worker.", task.id)
        response = backend.run(worker_task)
        logger.info("Task %s sent to worker. Response: %s", task.id, response)
        return {"message": f"Task {task.id} created.", "task_id": task.id}

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

@router.put("/{task_id}", status_code=status.HTTP_200_OK)
async def update_task(
    task_id: str,
    task: TaskUpdate,
    session: AsyncSession = Depends(get_async_session)):
    """Update task by id.

    Args:
        task_id (str): Task id.
        task (TaskUpdate): Task.

    Returns:
        dict: Response message.
    """
    if not is_valid_uuid(task_id):
        logger.info("task_id is not a valid uuid.")
        raise HTTPException(status_code=400, detail="task_id is not a valid uuid.")

    logger.info("Updating task with id: %s", task_id)
    async with session.begin():
        stmt = select(Task).where(Task.id == task_id)
        result = await session.exec(stmt)
        result = result.first()
        logger.debug("Task found: %s", result)

    # Raise 404 if task not found
    if not result:
        logger.info("Task not found.")
        raise HTTPException(status_code=404, detail="Task not found.")

    # Update task
    for key, value in task.model_dump().items():
        if value is not None:
            setattr(result, key, value)
    logger.debug("Task to be updated: %s", result)

    async with session:
        session.add(result)
        await session.commit()
        await session.refresh(result)
        logger.info("Task updated: %s", result)
        return {"message": f"Task {task_id} updated."}

@router.get("/{task_id}/inputs", response_model=TaskInputs)
async def read_task_inputs(
    task_id: str,
    session: AsyncSession = Depends(get_async_session)):
    """Get task inputs by task id.

    Args:
        task_id (str): Task id.

    Returns:
        TaskInput: Task input.
    """
    if not is_valid_uuid(task_id):
        logger.info("task_id is not a valid uuid.")
        raise HTTPException(status_code=400, detail="task_id is not a valid uuid.")

    logger.info("Reading task inputs with id: %s", task_id)
    async with session.begin():
        stmt = select(Task).where(Task.id == task_id)
        result = await session.exec(stmt)
        result = result.first()
        logger.debug("Task found: %s", result)

        # Raise 404 if task not found
        if not result:
            logger.info("Task not found.")
            raise HTTPException(status_code=404, detail="Task not found.")

        # Raise 404 if task has no input
        if not result.inputs:
            logger.info("Task has no input.")
            raise HTTPException(status_code=404, detail="Task has no input.")
        return {
            "inputs": result.inputs,
            "params": result.params
        }

@router.get("/{task_id}/outputs", response_model=TaskOutputs)
async def read_task_output(
    task_id: str,
    return_as_file: bool = False,
    session: AsyncSession = Depends(get_async_session)):
    """Get task outputs by task id.

    Args:
        task_id (str): Task id.
        return_as_file (bool, optional): Return as file. Defaults to False.

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
        result = result.first()
        logger.debug("Task found: %s", result)

    # Raise 404 if task not found
    if not result:
        logger.info("Task not found.")
        raise HTTPException(status_code=404, detail="Task not found.")

    # Raise 404 if task has no result
    if not result.outputs:
        logger.info("Task has no output.")
        raise HTTPException(status_code=404, detail="Task has no output.")

    if not return_as_file:
        return {"outputs": result.outputs}
    else:
        return Response(
            content=json.dumps(result.outputs, indent=4).encode(),
            headers={"Content-Disposition": "attachment; filename=output.json"},
            # media_type="application/json"
        )


@router.post("/{task_id}/outputs", status_code=status.HTTP_200_OK)
async def create_task_output(
    task_id: str,
    task_output: TaskOutputs,
    session: AsyncSession = Depends(get_async_session)):
    """Create task output.

    Args:
        task_id (str): Task id.
        task_output (TaskOutput): Task output.

    Returns:
        dict: Response message.
    """
    logger.debug("task_id: %s, task_output: %s", task_id, task_output)
    if not is_valid_uuid(task_id):
        logger.info("task_id is not a valid uuid.")
        raise HTTPException(status_code=400, detail="task_id is not a valid uuid.")

    logger.info("Creating task output with id: %s", task_id)
    async with session.begin():
        stmt = select(Task).where(Task.id == task_id)
        result = await session.exec(stmt)
        result = result.first()
        logger.debug("Task found: %s", result)

    # Raise 404 if task not found
    if not result:
        logger.info("Task not found.")
        raise HTTPException(status_code=404, detail="Task not found.")

    # Raise 400 if task has already output
    if result.outputs:
        logger.info("Task already has output.")
        raise HTTPException(status_code=400, detail="Task already has output.")

    # Update task output
    result.outputs = task_output.outputs
    async with session:
        session.add(result)
        await session.commit()
        await session.refresh(result)
        logger.info("Task output updated: %s", result)
    return {"message": f"Task output {task_id} created."}

@router.put("/{task_id}/outputs", status_code=status.HTTP_200_OK)
async def update_task_output(
    task_id: str,
    task_output: TaskOutputs,
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
        result = result.first()
        logger.debug("Task found: %s", result)

        # Raise 404 if task not found
        if not result:
            logger.info("Task not found.")
            raise HTTPException(status_code=404, detail="Task not found.")

        # Update task output
        result.outputs = task_output.outputs
        async with session:
            session.add(result)
            await session.commit()
            await session.refresh(result)
            logger.info("Task output updated: %s", result)
            return {"message": f"Task output {task_id} updated."}
