"""This module contains the database connection and session creation."""
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from api.utils.settings import Settings
from common.logger import logger

def get_database_url():
    """Returns the database URL based on the settings."""
    return (
        f"{Settings().DATABASE_DIALECT}://"
        f"{Settings().DATABASE_USER}:{Settings().DATABASE_PASSWORD}@"
        f"{Settings().DATABASE_HOST}:{Settings().DATABASE_PORT}/"
        f"{Settings().DATABASE_NAME}"
    )

async_engine = create_async_engine(
    get_database_url(),
    echo=True,
    future=True
)

async def get_async_session() -> AsyncSession:
    async_session = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session

async def create_db_and_tables():
    """Creates the database and tables."""
    logger.info("Creating database and tables.")
    async with async_engine.begin() as conn:
        if Settings().DATABASE_DROP_ALL:
            logger.info("Dropping all tables because DATABASE_DROP_ALL is set to True.")
            await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
