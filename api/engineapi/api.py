"""
Lootbox API.
"""
import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import data
from .settings import (
    ORIGINS,
)
from .routes.dropper import app as dropper_app
from .routes.leaderboard import app as leaderboard_app
from .routes.admin import app as admin_app
from .routes.play import app as play_app
from .routes.registered_contracts import app as contracts_app
from .version import VERSION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

tags_metadata = [{"name": "time", "description": "Server timestamp endpoints."}]


app = FastAPI(
    title=f"Engine HTTP API",
    description="Engine API endpoints.",
    version=VERSION,
    openapi_tags=tags_metadata,
    openapi_url="/openapi.json",
    docs_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping", response_model=data.PingResponse)
async def ping_handler() -> data.PingResponse:
    """
    Check server status.
    """
    return data.PingResponse(status="ok")


@app.get("/now", tags=["time"])
async def now_handler() -> data.NowResponse:
    """
    Get server current time.
    """
    return data.NowResponse(epoch_time=time.time())


app.mount("/leaderboard", leaderboard_app)
app.mount("/drops", dropper_app)
app.mount("/admin", admin_app)
app.mount("/play", play_app)
app.mount("/contracts", contracts_app)
