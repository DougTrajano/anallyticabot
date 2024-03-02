"""Main module for the FastAPI application."""
from fastapi import FastAPI
# from fastapi.logger import logger
from api.routes.skills.watson import router as skills_router
from api.routes.tasks import router as tasks_router
from api.database.base import create_db_and_tables
from api.utils.settings import Settings
from common.logger import logger

logger.info("Starting up.")

app = FastAPI(
    title=Settings().API_TITLE,
    description=Settings().API_DESCRIPTION,
    version=Settings().API_VERSION,
    root_path=Settings().API_ROOT_PATH,
    on_startup=[
        create_db_and_tables
    ]
)

@app.get("/", summary="Health check")
@app.get("/health", summary="Health check")
async def health_check():
    """Health check endpoint."""
    logger.info("Health check.")
    return {"STATUS": "OK"}


app.include_router(skills_router)
app.include_router(tasks_router)
