import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import downloads, events


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.DOWNLOADS_DIR, exist_ok=True)
    yield


app = FastAPI(title="DL - Universal Video Downloader", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(downloads.router)
app.include_router(events.router)
