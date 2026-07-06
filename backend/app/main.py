from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes.health import router as health_router
from backend.app.routes.demo import router as demo_router
from backend.app.routes.tools import router as tools_router
from backend.app.routes.summary import router as summary_router
from backend.app.routes.profiles import router as profiles_router
from backend.app.routes.logs import router as logs_router
from backend.app.routes.context import router as context_router
from backend.app.routes.evals import router as evals_router
from backend.app.dependencies import init_app_database

def create_app(init_db_on_startup: bool = True) -> FastAPI:
    if init_db_on_startup:
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await init_app_database()
            yield
    else:
        lifespan = None

    app = FastAPI(
        title="LeanBulk Coach API",
        version="0.2.0",
        description="Deterministic lean bulk coaching backend.",
        lifespan=lifespan
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5174",
        ],
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )
    
    app.include_router(health_router)
    app.include_router(demo_router)
    app.include_router(tools_router)
    app.include_router(summary_router)
    app.include_router(profiles_router)
    app.include_router(logs_router)
    app.include_router(context_router)
    app.include_router(evals_router, prefix="/evals", tags=["evals"])
    
    return app

app = create_app()
