from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from api.utils.logger import logger
from api.utils.misc import is_valid_uuid
from api.backends.task import TaskCreator
from api.database.base import get_async_session
from api.database.models.task import (
    Task,
    TaskCreate,
    TaskUpdate,
    TaskRead
)

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    responses={404: {"description": "Not found"}}
)


@router.get("/", response_model=List[TaskRead])
async def read_tasks(
    session: AsyncSession = Depends(get_async_session)):
    logger.info("Getting all tasks.")
    async with session.begin():
        stmt = select(Task)
        results = await session.execute(stmt)
        results = results.scalars().all()
        logger.info(f"Found {len(results)} tasks.")
        logger.debug(f"Tasks found: {results}")
        return results


@router.get("/{task_id}", response_model=TaskRead)
async def read_task(
    task_id: str,
    session: AsyncSession = Depends(get_async_session)):
    if not is_valid_uuid(task_id):
        logger.info("task_id is not a valid uuid.")
        raise HTTPException(status_code=400, detail="task_id is not a valid uuid.")
    
    logger.info(f"Reading task with id: {task_id}")
    async with session.begin():
        stmt = select(Task).where(Task.id == task_id)
        result = await session.execute(stmt)
        result = result.scalars().first()
        logger.debug(f"Task found: {result}")

        # Raise 404 if task not found
        if not result:
            logger.info(f"Task not found.")
            raise HTTPException(status_code=404, detail="Task not found.")
        return result


@router.post("/")
async def create_task(
    task: TaskCreate,
    session: AsyncSession = Depends(get_async_session)):
    logger.info(f"Creating task: {task}")

    creator = TaskCreator(task.name, task.args)
    if not creator.is_task_registered():
        logger.info(f"Task {task.name} not exist.")
        raise HTTPException(status_code=400, detail=f"Task {task.name} not exist.")
    
    async with session.begin():
        session.add(task)
        await session.refresh(task)
        logger.info(f"Task created: {task}")
        return {
            "message": "Task created.",
            "task_id": task.id
        }


@router.put("/")
async def update_task(
    task: TaskUpdate,
    session: AsyncSession = Depends(get_async_session)):
    logger.info(f"Updating task: {task}")

    creator = TaskCreator(task.name, task.args)
    if not creator.is_task_registered():
        logger.info(f"Task {task.name} not exist.")
        raise HTTPException(status_code=400, detail=f"Task {task.name} not exist.")
    
    async with session.begin():
        stmt = select(Task).where(Task.id == task.id)
        result = await session.execute(stmt)
        if not result.scalars().first():
            logger.info(f"Task {task.id} not found. Creating it.")
            session.add(task)
            await session.refresh(task)
            logger.info(f"Task created: {task}")
            return {
                "message": "Task created.",
                "task_id": task.id
            }
        else:
            logger.info(f"Task {task.id} found. Updating it.")
            session.add(task)
            await session.refresh(task)
            logger.info(f"Task updated: {task}")
            return {
                "message": "Task updated.",
                "task_id": task.id
            }


@router.delete("/")
async def delete_task(
    task_id: str,
    session: AsyncSession = Depends(get_async_session)):
    logger.info("Deleting task.")
    raise HTTPException(status_code=501, detail="Not implemented. Task deletion is not allowed.")