"""
Lyncis Core API Service
FastAPI entrypoint for OSINT event processing, storage, and replay streaming.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import init_db
from app.api.routes import router as api_router
from app.api.ws import ws_router
from app.replay.engine import replay_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize SQLite tables & prime replay
    print("[+] Initializing database...")
    init_db()
    print("[+] Loading replay scenario...")
    replay_engine.load_scenario()
    yield
    # Shutdown
    print("[*] Shutting down Lyncis API service...")
    replay_engine.pause()

app = FastAPI(
    title="Lyncis OSINT Core API",
    description="Maritime anomaly detection, sanctions cross-matching, and multi-source correlation engine.",
    version="0.1.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all during local dev / test
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(ws_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
