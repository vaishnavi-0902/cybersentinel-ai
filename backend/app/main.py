import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.database import Base, engine
from backend.app.models import Alert, ModelVersion, SecurityEvent, User  # noqa: F401
from backend.app.routes.auth import router as auth_router
from backend.app.routes.core import router as core_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("cybersentinel")


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("CyberSentinel AI backend started successfully")
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="CyberSentinel AI cybersecurity monitoring platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(core_router)


@app.get("/")
def root_message():
    return {"message": "CyberSentinel AI backend is running"}
