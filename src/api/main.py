from fastapi import FastAPI
from fastapi.logger import logger
from routes.skills.watson import router as skills_router
from routes.tasks import router as tasks_router
from database.base import create_db_and_tables
from utils.settings import Settings

logger.info("Starting up.")

app = FastAPI(
    title=Settings().API_TITLE,
    description=Settings().API_DESCRIPTION,
    version=Settings().API_VERSION,
    on_startup=[
        create_db_and_tables
    ]
)

@app.get("/", summary="Health check")
@app.get("/health", summary="Health check")
async def health_check():
    logger.info("Health check.")
    return {"STATUS": "OK"}


app.include_router(skills_router)
app.include_router(tasks_router)