from fastapi import FastAPI
from backend.app.routes.health import router as health_router
from backend.app.routes.demo import router as demo_router
from backend.app.routes.tools import router as tools_router
from backend.app.routes.summary import router as summary_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="LeanBulk Coach API",
        version="0.2.0",
        description="Deterministic lean bulk coaching backend."
    )
    
    app.include_router(health_router)
    app.include_router(demo_router)
    app.include_router(tools_router)
    app.include_router(summary_router)
    
    return app

app = create_app()
