from fastapi import APIRouter
from backend.workflows.demo_flow import run_local_demo_flow

router = APIRouter()

@router.get("/demo/local")
async def get_demo_local():
    return await run_local_demo_flow()
