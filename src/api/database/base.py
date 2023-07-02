from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from utils.settings import Settings
from utils.logger import logger

def get_database_url():
    """Returns the database URL based on the settings."""
    return (
        f"{Settings().DB_DIALECT}://"
        f"{Settings().DB_USER}:{Settings().DB_PASSWORD}@"
        f"{Settings().DB_HOST}:{Settings().DB_PORT}/"
        f"{Settings().DB_NAME}"
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
        if Settings().DB_DROP_ALL:
            logger.info("Dropping all tables because DB_DROP_ALL is set to True.")
            await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
