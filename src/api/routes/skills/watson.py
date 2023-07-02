import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from api.utils.logger import logger
from api.utils.misc import is_valid_uuid
from api.database.base import get_async_session
from api.database.models.skills.watson import (
    WatsonAssistant,
    WatsonAssistantCreate,
    WatsonAssistantUpdate,
    WatsonAssistantRead
)


router = APIRouter(
    prefix="/skills/watson",
    tags=["skills"],
    responses={404: {"description": "Not found"}}
)


@router.get("/", response_model=List[WatsonAssistantRead])
async def read_watson_assistants(
    session: AsyncSession = Depends(get_async_session)):
    """Returns a list of Watson Assistants."""
    logger.info("Getting all Watson Assistants.")
    async with session.begin():        
        stmt = select(WatsonAssistant)
        results = await session.execute(stmt)
        results = results.scalars().all()
        logger.info(f"Found {len(results)} Watson Assistants.")
        logger.debug(f"Watson Assistants found: {results}")
        return results


@router.get("/{watson_id}", response_model=WatsonAssistantRead)
async def read_watson_assistant(
    watson_id: str,
    session: AsyncSession = Depends(get_async_session)):
    """Returns a Watson Assistant."""
    if not is_valid_uuid(watson_id):
        logger.info("watson_id is not a valid uuid.")
        raise HTTPException(status_code=400, detail="watson_id is not a valid uuid.")
     
    logger.info(f"Reading Watson Assistant with id: {watson_id}")
    async with session.begin():
        stmt = select(WatsonAssistant).where(WatsonAssistant.id == watson_id)
        result = await session.execute(stmt)
        result = result.scalars().first()
        logger.debug(f"Watson Assistant found: {result}")

        # Raise 404 if watson assistant not found
        if not result:
            logger.info(f"Watson Assistant not found.")
            raise HTTPException(status_code=404, detail="Watson Assistant not found.")
        return result


@router.post("/")
async def create_watson_assistant(
    watson: WatsonAssistantCreate,
    session: AsyncSession = Depends(get_async_session)):
    """Creates a Watson Assistant."""
    logger.info("Creating Watson Assistant.")
    async with session.begin():
        db_watson = WatsonAssistant.from_orm(watson)
        session.add(db_watson)
        logger.info("Watson Assistant created.")
        return {"message": "Watson Assistant created."}
    

@router.put("/")
async def update_watson_assistant(
    watson: WatsonAssistantUpdate,
    session: AsyncSession = Depends(get_async_session)):
    """Creates or updates a Watson Assistant."""
    logger.info("Creating or updating Watson Assistant.")
    async with session.begin():
        stmt = select(WatsonAssistant).where(WatsonAssistant.id == watson.id)
        result = await session.execute(stmt)
        if not result.scalars().first():
            logger.info("Watson Assistant not found, creating.")
            db_watson = WatsonAssistant.from_orm(watson)
            session.add(db_watson)
            logger.info("Watson Assistant created.")
            return {"message": "Watson Assistant created."}
        else:
            logger.info("Watson Assistant found, updating.")
            db_watson = WatsonAssistant.from_orm(watson)
            db_watson.updated_at = datetime.datetime.utcnow()
            await session.merge(db_watson)
            logger.info("Watson Assistant updated.")
            return {"message": "Watson Assistant updated."}


@router.delete("/")
async def delete_watson_assistant(
    watson_id: str,
    session: AsyncSession = Depends(get_async_session)):
    """Deletes a Watson Assistant."""
    logger.info(f"Deleting Watson Assistant with id: {watson_id}")
    async with session.begin():
        stmt = select(WatsonAssistant).where(WatsonAssistant.id == watson_id)
        result = await session.execute(stmt)
        watson = result.scalars().first()
        logger.debug(f"Watson Assistant found: {watson}")

        if not watson:
            logger.info(f"Watson Assistant not found.")
            raise HTTPException(status_code=404, detail="Watson Assistant not found.")
        
        await session.delete(watson)
        logger.info(f"Watson Assistant deleted.")
        return {"message": "Watson Assistant deleted."}
    