"""FastAPI app entry point. Run with: uvicorn api.main:app --reload"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.db import init_pool, close_pool
from api.routers import auth as auth_router
from api.routers import chat as chat_router
from api.routers import dashboard as dashboard_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("▶  Initializing Postgres connection pool…")
    init_pool()
    print("✓  API ready.")
    yield
    # Shutdown
    print("◼  Closing Postgres connection pool…")
    close_pool()


app = FastAPI(
    title="Safety Operations API",
    description="AI-augmented executive analytics backend",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — so React (Phase 2) can call us
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router.router)
app.include_router(dashboard_router.router)
app.include_router(chat_router.router)


@app.get("/", tags=["health"])
def root():
    return {
        "name": "Safety Operations API",
        "version": app.version,
        "docs":  "/docs",
    }


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}